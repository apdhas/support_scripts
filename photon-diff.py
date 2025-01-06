import json
from xml.etree import ElementTree as et


import os

print(os.__file__)

tree = et.parse("/Volumes/Ajith/manifest-old.xml")

root = tree.getroot()
packageGroups = root.find('packageGroups')
group = packageGroups.find('group')
packages = group.findall('package')
existing_ph5 = {}
for package in packages:
    try:
        if '.ph5' in package.attrib['version']:
            existing_ph5[package.attrib['name']] = package.attrib['version']
    except KeyError as e:
        print(package.attrib)

tree = et.parse("/Volumes/Ajith/manifest-latest.xml")
root = tree.getroot()
packageGroups = root.find('packageGroups')
group = packageGroups.find('group')
packages = group.findall('package')

latest_ph5 = {}
for package in packages:
    if '.ph5' in package.attrib['version']:
        latest_ph5[package.attrib['name']] = package.attrib['version']

print("Photon packages changed...")
latest_new = []
latest = []
i = 0
for key, version in latest_ph5.items():
    if key not in existing_ph5:
        i=i+1
        latest_new.append(key + "=" + version)
    else:
        if version != existing_ph5[key]:
            i=i+1
            latest.append(key + "=" + version)
print(i)

existing = []
removed = []
i = 0
for key, version in existing_ph5.items():
    if key not in latest_ph5:
        i=i+1
        removed.append(key + "=" + version)
    else:
        if version != latest_ph5[key]:
            i=i+1
            existing.append(key + "=" + version)

latest.sort()
existing.sort()
for i in range(0, len(latest)):
    print(existing[i] + " -> " + latest[i])

if latest_new:
    print("\nNew packages:")
    for i in range(0, len(latest_new)):
        print(latest_new[i])

if removed:
    print("\nRemoved packages:")
    for i in range(0, len(removed)):
        print(removed[i])
