import subprocess

def runCommand(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p.returncode, out, err

path = "/opt/vmware/share/vami/"
commands = [["vami_all_interfaces"], ["vami_access"], ["vami_default_interface"],
            ["vami_dns"], ["vami_domain"], ["vami_first_ip"], ["vami_fullhostname"],
            ["vami_gateway", "eth0"], ["vami_gateway6", "eth0"], ["vami_get_network", "eth0"],
            ["vami_hname"], ["vami_hw_addr", "eth0"], ["vami_ip_addr", "eth0"],
            ["vami_ip6_addr", "eth0"], ["vami_interfaces"], ["vami_netmask","eth0"], ["vami_prefix", "eth0"],
            ["vami_set_network"], ["vami_set_proxy"], ["vami_set_dns"], ["vami_set_hostname"]]

for cmd in commands:
    run_cmd = [path + cmd[0]]
    run_cmd = run_cmd + cmd[1:]
    rc, out, err = runCommand(run_cmd)
    if rc != 0:
        print("Failed to run command %s. Err: %s" % (cmd, err))
    print(out)
