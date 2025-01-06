import subprocess
import sys
import time
from datetime import datetime

import requests
import json
import logging

# initialize logger
logger = logging.getLogger(__name__)
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logger.setLevel(logging.DEBUG)
log_filename = f"uts_tests_{timestamp}.log"
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler(filename='uts_tests.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)



def get_uts_pipeline_status(uts_id):
    pipeline_query = 'https://uts-testdata.lvn.broadcom.net/v1/api/testdata/pipeline/' + uts_id
    logger.info(pipeline_query)
    response = requests.get(pipeline_query)
    json_response = response.json()
    logger.info(json_response['status'])
    return json_response['status']


def trigger_uts_pipeline(tests_list, cln):
    command = ['/build/apps/bin/uts', 'precheckin', '-c', cln]
    for test in tests_list:
        command.append('-t')
        command.append(test)
    command.append('--no-deflaker')
    command.append('--no-policies')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        logger.info("Error executing command: ", err)
        exit(1)
    uts_id = None
    logger.info(out)
    for line in out.decode('utf-8').splitlines():
        if line.startswith('https://'):
            uts_url = line.strip()
            logger.info(line)
            # Get last part in the uts url
            uts_id = uts_url.split('/')[-1]
            logger.info(uts_id)
    return uts_id


def wait_for_test_rerun(uts_id, rerun_test_ids):
    test_query_url = "https://uts-testdata.lvn.broadcom.net/v1/api/testdata/test/"
    test_run_status = {}
    is_test_running = False
    for test_id in rerun_test_ids:
        response = requests.get(test_query_url + test_id).json()
        test_run_status[test_id] = response['result']
        if response['result'] == 'Running':
            is_test_running = True
    if is_test_running:
        time.sleep(5 * 60)
        wait_for_test_rerun(uts_id, rerun_test_ids)
    else:
        return test_run_status


def retry_failed_tests(uts_id, failed_tests):
    rerun_url = "https://uts-scheduler.lvn.broadcom.net/v1/api/test-scheduler/rerun-test"
    if failed_tests:
        retry_count = 2
        while retry_count > 0:
            for test in failed_tests:
                payload = {'test_fk': test, 'requestor': 'dhasa'}
                response = requests.post(rerun_url, json=payload)
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 202:
                    logger.info("Test rerun triggered successfully, wait for the test to complete")
                    logger.info(str(response.json()))
            time.sleep(5 * 60)
            test_results = get_test_details(uts_id)
            rerun_test_ids = []
            for test in test_results:
                if test['aggregated_status'] == 'Failed':
                    for test_data in test['tests_data']:
                        if test_data['previous_test_fk'] and test_data['previous_test_fk'] in failed_tests:
                            rerun_test_ids.append(test_data['id'])
            rerun_status = wait_for_test_rerun(uts_id, rerun_test_ids)
            for test_id, status in rerun_status.items():
                if status == 'Passed':
                    failed_tests.remove(test_id)
            retry_count -= 1
        if failed_tests:
            logger.info("Failed tests after retrying: ", failed_tests)
            # TODO: Mail


def get_test_details(uts_id):
    test_details_url = f'https://ui-service.vdp.lvn.broadcom.net/api/v1/dashboard/generic/pipeline-tests?pipeline_fk={uts_id}&triagedFiltered=false&untriagedFiltered=false&rerunFiltered=false'
    response = requests.get(test_details_url).json()
    response_tests = []
    for test_object in response['objects']:
        test_data = {
            'name': test_object['test_name'],
            'tests_data': [],
            'aggregated_status': 'Failed',
            'test_type': ''
        }
        for test in test_object['tests']:
            test_aggregation_data = {
                'id': test['_id'],
                'name': test['test_name'],
                'area': test['area_name'],
                'status': test['result'],
                'previous_test_fk': test.get('previous_test_fk', '')
            }
            test_data['tests_data'].append(test_aggregation_data)
            if test['test_type']:
                test_data['test_type'] = test['test_type']
            if test["aggregated_result"] == "Passed":
                test_data['aggregated_status'] = "Passed"
        response_tests.append(test_data)
    logger.info(json.dumps(response_tests, indent=4))
    return response_tests


def wait_and_retry_pipeline(uts_id):
    while (status := get_uts_pipeline_status(uts_id)) == 'RUNNING':
        logger.info('Pipeline is running, wait for few minutes')
        time.sleep(2 * 60)

    if status == 'NOT_BUILT':
        logger.info('Pipeline is not built, retrying')
        exit(2)
    elif status == 'FAILURE':
        logger.info('Pipeline failed, check logs for details')
        #time.sleep(2 * 60)
        failed_tests = [
            test_data['id']
            for test in get_test_details(uts_id)
            for test_data in test['tests_data']
            if test['aggregated_status'] == 'Failed' and not test_data['previous_test_fk']
        ]
        if failed_tests:
            logger.info('Failed tests : ' + str(failed_tests))
            retry_failed_tests(uts_id, failed_tests)
    elif status == 'SUCCESS':
        logger.info('Pipeline completed successfully')
        exit(0)

if __name__ == '__main__':
    test_list = ['vc-precheckin', 'update-cli-repo-main-main-resume', 'update-cli-repo-main-main',
                 'vc-install-emb-default', 'vcha-embedded-2', 'vc-upgrade-80ga-all-in-one-api']
    # Get the cln from the command line
    cln = sys.argv[1] if len(sys.argv) > 1 else None
    if not cln:
        logger.info("Please provide a CLN as a command line argument")
        sys.exit(1)

    # Trigger UTS pipeline and wait for completion or failure
    utsId = trigger_uts_pipeline(test_list, cln)
    time.sleep(5 * 60)
    wait_and_retry_pipeline(utsId)
