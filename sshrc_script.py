#!/usr/bin/python
import os
import signal
import sys

sys.path.append("/usr/lib/applmgmt/access/py/")
sys.path.append("/usr/lib/applmgmt/pint/py/")
sys.path.append("/usr/lib/applmgmt/base/py/")
sys.path.append("/usr/lib/vmware/site-packages")
vapi_path = '/usr/lib/applmgmt/vapi/lib'
if os.path.exists(vapi_path):
    sys.path.append(vapi_path)
    for p in os.listdir(vapi_path):
        sys.path.append(os.path.join(vapi_path, p))
from vmware.appliance.access.ssh_utils import SSHManager
import psutil
import os
import logging

logger = logging.getLogger(__name__)

import featureState

featureState.init(enableLogging=False)


def getMainSessionProcess(limit=10):
    '''Walk up the process tree until we find a process we like.
   Arguments:
       ok_names: Return the first one of these processes that we find
   '''

    depth = 0
    this_proc = psutil.Process(os.getpid())
    ppid = this_proc.ppid()
    procs = []
    while depth < limit:

        next_proc = psutil.Process(ppid)
        if ppid == 1:
            break
        procs.append(ppid)
        ppid = next_proc.ppid()
        depth += 1
    return procs[len(procs) - 3]


if featureState.getSsh_Management_Phase1():
    sshManager = SSHManager()
    active_sessions = sshManager.getActiveSessionsUsingCommand()
    currentBashPid = getMainSessionProcess()
    if len(active_sessions) > 3:
        print("Max allowed concurrent SSH sessions reached")
        os.kill(currentBashPid, signal.SIGKILL)
    else:
        print("Populate data")
        sshManager.populateSshSessionInfo()
