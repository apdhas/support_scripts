#!/usr/bin/python
# Copyright (c) 2017-2018 VMware, Inc.  All rights reserved. VMware Confidential

import json
import logging
import os
import sys
sys.path.append(os.environ['VMWARE_PYTHON_PATH'])
from cis.defaults import (get_cis_install_dir, get_component_home_dir)
from cis.utils import (log, get_deployment_nodetype)
from cis.firstboot import FirstBoot

CMBin = os.path.join(get_cis_install_dir(),
                     get_component_home_dir("cm"),
                     "bin")
sys.path.append(CMBin)
from cloudvmcisreg import cloudvm_sso_cm_register, VecsKeyStore
from cis.cisreglib import VmafdClient, LookupServiceClient, SsoClient
from pyVmomi import lookup
from identity.vmkeystore import VmKeyStore

class ApplianceMgmtFB(FirstBoot):
    # Appliance Management firstboot implementation.

    def __init__(self, comp_name, solution_user):
        ''' Initialize the base class.
            The default paths initialized by the base class are not applicable
            to appliance management firstboot. The self._setupEnvironment
            function is called to initialize appliance managment paths.

            The default paths initialized the firstboot class are overwritten
            by appliance management specific paths.
        '''
        super(ApplianceMgmtFB, self).__init__(comp_name, solution_user)
        # override the firstboot variables
        self._home_dir = '/usr/lib/applmgmt'
        self._config_dir = '/etc/applmgmt'
        self._log_dir = '/var/log/vmware/applmgmt'
        self._data_dir = '/var/vmware/applmgmt'
        self._fb_conf_dir = '/etc/applmgmt/firstboot'
        self._appliance_conf = '/etc/applmgmt/appliance/appliance.conf'
        self._service_spec = '/etc/applmgmt/firstboot/applmgmt.properties'
        self._dcui_conf = '/etc/vmware/appliance/dcui.cfg'
        self._flag_file = '/var/vmware/applmgmt/endpoint-fixed'
        # make component name 'applmgmt' for all platforms
        self._service_name = comp_name
        self._nodeType = get_deployment_nodetype()
        self._deployment_types_file = '/etc/vmware/deployment_types.json'
        if os.path.isfile(self._deployment_types_file):
            with open(self._deployment_types_file, 'r') as fp:
                self._product_type = json.load(fp)[self._nodeType]

        control_script_path = 'service-control-default-vmon'
        keystore = VecsKeyStore(self.get_soluser_name())
        dyn_vars = {'solution-user.name': self.get_soluser_id(),
                    'control-script.path': control_script_path}
        self.ls_url = VmafdClient().get_ls_location()
        ks = VmKeyStore('VKS')
        ks.load('machine')
        cert = ks.get_certificate('machine')
        key = ks.get_key('machine')
        self._lookup_service_client = LookupServiceClient(self.ls_url,
                                                          retry_count=2)
        stsUrl, stsCertData = self._lookup_service_client.get_sts_endpoint_data()
        ssoClient = SsoClient(stsUrl, stsCertData, None, None,
                              cert=cert, key=key)
        self._lookup_service_client.set_sso_client(ssoClient)
        filter_spec = lookup.ServiceRegistration.Filter()
        filter_spec.endpointType = lookup.ServiceRegistration.EndpointType(
            protocol="vapi.json.http", type="com.vmware.applmgmt")
        self.service_info = self._lookup_service_client.get_service_info_list(
            search_filter=filter_spec)
        if self.service_info:
            for svc_info in self.service_info:
                for endPoint in svc_info.serviceEndpoints:
                    for attribute in endPoint.endpointAttributes:
                        if attribute.key == \
                                "com.vmware.vapi.metadata.metamodel.file":
                            log("Unregistering old instance with service id %s"
                                "..." % svc_info.serviceId)
                            self._lookup_service_client.unregister_service(
                                svc_info.serviceId)
                            log("Done Unregistration...")
                            break
                    else:
                        continue
                    break
                else:
                    continue
                break

        log("Register new service instance...")
        cloudvm_sso_cm_register(keystore,
                                self._service_spec,
                                self.get_soluser_name(),
                                dyn_vars)
        log("Registered service as owner = %s" % self.get_soluser_ownerId())
        with open(self._flag_file, 'w') as f:
            f.close()


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s  %(message)s")
    applmgmtFB = ApplianceMgmtFB('applmgmt', "machine")
