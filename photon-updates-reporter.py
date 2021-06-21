import json
import requests
from packaging import version


def get_cve_fixes(date = None):
    response = requests.get("https://photonsecurity.eng.vmware.com/api/0.1/branch/3.0/cve?photon_branch=3.0&cve_state=closed", verify=False)
    cve_fix_list = json.loads(response.text)
    data = {}
    for fix in cve_fix_list:
        if fix["status"] == "Closed":
            if fix["cve_score"] > 7.0:
                fix_json = {}
                fix_list = []
                cve_data = {}
                pkg_name = fix["pkg_name"]
                if pkg_name in data:
                    fix_json = data[pkg_name]
                cve_data["cve_num"] = fix["cve_num"]
                cve_data["score"] = fix["cve_score"]
                if fix_json and fix["res_ver"] in fix_json:
                    fix_list = fix_json[fix["res_ver"]]
                fix_list.append(cve_data)
                fix_json[fix["res_ver"]] = fix_list
                data[pkg_name]= fix_json
    return data

def get_rpm_manifest(buildNumber):
    response = requests.get("http://build-squid.eng.vmware.com/build/mts"
                            "/release/bora-"+buildNumber+"/publish/exports/Update_Repo"
                                              "/package-pool/rpm-manifest.json")
    rpm_list = json.loads(response.text)
    return rpm_list["files"]

source_rpms = get_rpm_manifest("17694817")

def get_refined_cve(cve_fix_list, source_rpms):
    data = {}
    for pkg, details in source_rpms.items():
        fix_version_data = {}
        if pkg in cve_fix_list:
            src_version = version.parse(details["version"] + "-" + details[
                "release"])
            fix_version = ""
            for fix_version, cve_detail in cve_fix_list[pkg].items():
                fix_data = []
                cve_fix_version = version.parse(fix_version)
                if cve_fix_version > src_version:
                    fix_data = cve_fix_list[pkg][fix_version]
            if fix_version and fix_data:
                fix_version_data[fix_version] = fix_data
            if fix_version_data:
                data[pkg] = fix_version_data
    return data


refined_cves = get_refined_cve(get_cve_fixes(), source_rpms)

target_rpms = get_rpm_manifest("18142938")


def get_fixed_cves(target_rpms, refined_cves):
    data = {}
    for pkg, details in refined_cves.items():
        rpm_version = version.parse(target_rpms[pkg]["version"] + "-" + target_rpms[pkg]["release"])
        for fix_version, cve_detail in details.items():
            cve_fix_version = version.parse(fix_version)
            if cve_fix_version == rpm_version or cve_fix_version < rpm_version:
                data[pkg] = details
    return data

print(get_fixed_cves(target_rpms, refined_cves))
