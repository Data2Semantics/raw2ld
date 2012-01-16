import httplib
import re
import urllib
import os
from zipfile import ZipFile

FDA_SITE = "www.fda.gov"
LOCATIONS = ["/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm083765.htm", "/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm"]
DOWNLOAD_LOC = "/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/"
TARGET_PATH = "../aers_data_files/"

conn = httplib.HTTPConnection(FDA_SITE)

files = []

for loc in LOCATIONS :
    conn.request("GET", loc)

    r = conn.getresponse()
    print r.status, r.reason

    data = r.read()

    for m in re.finditer(r'href="'+ DOWNLOAD_LOC +'((UCM|ucm)\d+\.zip)">(AERS_ASCII_\d\d\d\dq\d\.ZIP)', data) :
        # print m.group(1), m.group(3)
        url = "http://{0}{1}{2}".format(FDA_SITE,DOWNLOAD_LOC,m.group(1))
        target_file = TARGET_PATH + m.group(3)
        files.append(target_file)
        print "Starting download of {0}...".format(m.group(3))
        # print url
        if not(os.path.exists(target_file)) :
            urllib.urlretrieve(url,target_file)
        else :
            print "{0} already exists!".format(target_file)
        print "Done"

print "All done downloading"

for f in files :
    extract_path = f.rstrip('.ZIP')
    print "Extracting {0} to {1}".format(f, extract_path)
    if not(os.path.exists(extract_path)) :
        zf =  ZipFile(f,'r')
        zf.extractall(extract_path)
    else :
        print "{0} already exists!".format(extract_path)
    print "Done"
    
print "All done extracting"




