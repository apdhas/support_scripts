import requests
import json
import re
import subprocess
import sys


vcenterBuild = "18483431"
vcenterBuild = sys.argv[1]


def getJavaUsage(build_id):
    base_url = "https://build-squid.eng.vmware.com/build/mts/release/bora" \
               "-" + build_id + "/logs/"

    resp = requests.get(base_url)

    lines = resp.text.splitlines(keepends=False)
    extended_path = ""
    for line in lines:
        if "a href" in line:
            if ">linux" in line:
                extended_path = re.findall(r'"([^"]*)"', line)[0]
                break
            if ">windows" in line:
                extended_path = re.findall(r'"([^"]*)"', line)[0]
                break

    url = base_url + extended_path + "gobuilds.log"
    subprocess.call(["wget", url, "-O", "/root/gobuilds.log"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    is_java = False
    java_string = []
    try:
        with open("/root/gobuilds.log") as f:
            lines = f.readlines()
            for line in lines:
                if "JAVA_HOME" in line and"/build/toolchain" in line and "jdk" in \
                        line:
                    is_java = True
                    reg = re.findall(
                        r"/build/toolchain/[a-zA-Z][a-zA-Z][a-zA-Z][0-9][0-9]/jdk-["
                        r"0-9].[0-9].[0-9]",
                        line)
                    if reg:
                        java_string.append(reg[0])
                    else:
                        if "cayman_openjdk" not in line:
                            java_string.append(line)
                        else:
                            java_string.append("cayman_openjdk")
                    break
    except:
        java_string.append("exception")
    return is_java, java_string

componentsJson = {}
product_list = []

def getComponentsDetails(build_id, only_java=False):
    build_id = str(build_id)
    response = requests.get("https://buildapi.eng.vmware.com/ob/buildcomponent"
                        "/?_offset=0&_limit=200&_format=json&build=" + build_id)

    responseJson = json.loads(response.text)

    componentsList = responseJson["_list"]

    dependencyList = dict()
    for component in componentsList:
        compInfo = dict()
        compInfo["build_id"] = component["component_buildid"]
        response = requests.get("https://buildapi.eng.vmware.com" +
                                component["_component_build_url"] + "?_format=json")
        buildInfo = json.loads(response.text)
        product = buildInfo["product"]
        pName = ""
        if buildInfo["product"] == "vcenter":
            product = product + "-" + buildInfo["compilation"]
            pName = product
        else:
            compInfo["branch"] = buildInfo["branch"]
            pName = product + "-" + buildInfo["branch"]
        if pName not in product_list:
            product_list.append(pName)
            compInfo["child_components"] = getComponentsDetails(str(compInfo[
                                                                   "build_id"]), only_java)
        is_java, java_string = getJavaUsage(str(compInfo["build_id"]))
        compInfo["is_java"] = is_java
        if is_java:
            compInfo["jdk"] = java_string
        if only_java:
            if compInfo["is_java"]:
                dependencyList[product] = compInfo
        else:
            dependencyList[product] = compInfo

    return dependencyList


componentsJson["vcenter-all"] = getComponentsDetails(vcenterBuild)

#
# components = componentsJson["vcenter-all"]
#
# for key, value in components.items():
#     compInfo = getComponentsDetails(value['build_id'])
#     components[key]['components'] = compInfo
#
# componentsJson["vcenter-all"] = components

with open('/root/result.json', 'w') as f:
    json.dump(componentsJson, f)
