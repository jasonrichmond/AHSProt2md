import json
import os
import re
import shutil
from markdownify import markdownify
import requests


outFolder = "build"
imgFolder = outFolder + "/img"
inFolder = "unzip/content/"
releaseAPI = "https://www.ahsems.com/public/protocols/releaseinfo_113.json"

def cleanPath(path):
    return re.sub(r'/','-', path.rstrip())

def folderParse(folderName,Parent = os.getcwd() + "/" + outFolder, imgDir = "../img/"):
    pattern = r'!\[([^\]]*?)\]\(([^\)]+)\/([^\.]*\.png)\)'

    for fname in folderName:
        newFolderName = cleanPath (fname['folderName'].rstrip())
        newFolder = Parent + "/" + newFolderName
        print(newFolder)

        #create folder
        os.mkdir(newFolder)

        #get protocols
        for p in fname['protocols']:
            protocolName = cleanPath(p['protocolName'])
            mdContent=""
            for tab in p['tabContent'].keys():
                if (p['tabContent'][tab] == True):
                    # what tab am i
                    for t in tabs:
                        if ( f"{t['tabID']}" == tab):
                            mdContent += f"# {t['tabName']}\n\n"
                            break
                    #grab the file
                    contentFileName = f"content_{p['protocolID']}_{p['protocolSetID']}_{tab}.html"
                    with open (inFolder + contentFileName, "r") as f:
                        content = f.read()
                    #mdContent += pyhtml2md.convert(content,pyhtml2md.Options()) + "\n\n"
                    mdContent += markdownify(content) + "\n\n"

            #replace links. point the images at the img folder
            mdContent = re.sub(pattern, lambda x: f'![{x.group(1)}]({imgDir}{x.group(3)})', mdContent)
            #write the file
            with open(newFolder + "/" + protocolName + ".md","w") as f:
                f.write (mdContent)
                print (newFolder + "/" + protocolName + " written")



        # get sub folders
        if (len(fname['folders'])>0):
            
            folderParse(fname['folders'], Parent + "/" + newFolderName, "../" + imgDir)
            
#get the latest release
print ("Look for updates")
response = requests.get(releaseAPI)
releaseData = response.json()

ziploc = ""
for pack in releaseData['packages']:
    if re.search(r'Critical Care MCPs', pack['name']):
        ziploc = pack['packageURL']
        break

if ziploc == "":
    raise("Failed to get the zip url")

response = requests.get(ziploc)
if response.status_code == 200:
    if os.path.exists("download") and os.path.isdir("download"):
        shutil.rmtree("download")
    os.mkdir("download")

    with open("download/in.zip", "wb") as file:
        file.write(response.content)
        print("File downloaded successfully!")
        if os.path.exists("unzip") and os.path.isdir("unzip"):
            shutil.rmtree("unzip")
        os.mkdir("unzip")
        shutil.unpack_archive("download/in.zip","unzip")
        print("File unzipped downloaded successfully!")
else:
    print("Failed to download the file.")

with open ("unzip/lifecycle.json","r") as f:
    lifecycle = json.load(f)

with open ("unzip/tabs.json","r") as f:
    tabs = json.load(f)

with open ("unzip/tabset.json","r") as f:
    tabset = json.load(f)

with open ("unzip/version.json","r") as f:
    version = json.load(f)

shutil.rmtree(outFolder)
os.mkdir(outFolder)
os.mkdir(imgFolder)

for file in os.listdir(inFolder):
    if file.endswith(".png"):
        # Copy the file to the destination directory
        shutil.copy(os.path.join(inFolder, file), imgFolder)

folderParse (lifecycle['live']['folders'])
    