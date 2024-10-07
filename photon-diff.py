from xml.etree import ElementTree as et


import os

print(os.__file__)

tree = et.parse("/Volumes/Ajith/manifest-old.xml")

root = tree.getroot()
packageGroups = root.find('packageGroups')
group = packageGroups.find('group')
packages = group.findall('package')
existing_ph5 = []
for package in packages:
    try:
        if '.ph5' in package.attrib['version']:
            existing_ph5.append(package.attrib['name'] + "-" + package.attrib['version'])
    except KeyError as e:
        print(package.attrib)

tree = et.parse("/Volumes/Ajith/manifest-latest.xml")
root = tree.getroot()
packageGroups = root.find('packageGroups')
group = packageGroups.find('group')
packages = group.findall('package')

latest_ph5 = []
for package in packages:
    if '.ph5' in package.attrib['version']:
        latest_ph5.append(package.attrib['name'] + "-" + package.attrib['version'])

print("Photon package changed...")
latest = []
i = 0
for data in latest_ph5:
    if data not in existing_ph5:
        i=i+1
        latest.append(data)
print(i)

existing = []
i = 0
for data in existing_ph5:
    if data not in latest_ph5:
        i=i+1
        existing.append(data)

latest.sort()
existing.sort()

for i in range(0, len(latest)):
    print(existing[i] + " -> " + latest[i])
