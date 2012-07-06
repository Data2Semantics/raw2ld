import glob
import os
from datetime import datetime
from d2s.prov import Trace
import argparse
import httplib
import re
import urllib
from zipfile import ZipFile
#import shlex


# All reports:
ALL_LOCATIONS = ["/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm083765.htm", "/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm"]

# Only latest year (for testing purposes):
RECENT_LOCATIONS = ["/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm"]


DOWNLOAD_LOC = "/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/"
TARGET_PATH = "../aers_data_files/"

MASK_TO_AERS_DATA = '../aers_data_files/aers_ascii_2011q1/ascii/*.TXT'
MYSQL_PATH = '/usr/local/mysql/bin'
USER = 'root'

PASS = 'visstick'

def downloadAERS(downloadAll = False):
    FDA_SITE = "www.fda.gov"
    
    if downloadAll :
        locations = ALL_LOCATIONS
    else :
        locations = RECENT_LOCATIONS
    
    conn = httplib.HTTPConnection(FDA_SITE)
    
    files = []
    
    for loc in locations :
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


def importToMySQL(year):
    t = Trace(trailFile='out-{}.ttl'.format(datetime.strftime(datetime.now(),'%Y-%m-%dT%H-%M-%S')))
    
    print "Will proceed to import all data"
    
    # Copy all AERS data files to /tmp
    print "Copying AERS data files from {0} to /tmp...".format(MASK_TO_AERS_DATA)
    for f in glob.glob(MASK_TO_AERS_DATA) :
        (fpath,fname) = os.path.split(f)
        fnew = '/tmp/'+fname
        t.execute(['cp','-v',f,fnew],inputs=[f],outputs=[fnew])
    print "... done"
    
    tables = ['demo', 'drug', 'indi', 'outc', 'reac', 'ther']
    
    print "Checking consistency of data files"
    for ftype in tables :
        files = glob.glob('/tmp/{0}11Q1.TXT'.format(ftype.upper()))
        for f in files :
            t.execute(['python','check_files.py',f,f+'.checked'], inputs=[f], outputs=[f+'.checked'])
        
    
    
    
    for tab in tables :
        files = glob.glob('/tmp/{0}11Q1.TXT.checked'.format(tab.upper()))
        print "Truncating table {0} ...".format(tab)
        trunc_command = ['{0}/mysql'.format(MYSQL_PATH),'-u',USER,'-p{0}'.format(PASS),'aers','-e','TRUNCATE TABLE aers.{0};'.format(tab)]
        t.execute(trunc_command, inputs=['aers.{0}'.format(tab)],outputs=['aers.{0}'.format(tab)],replace=PASS)
        print "... done"
        for f in files :
            print "Importing from {0} into {1} ...".format(f, tab)
            command = ['{0}/mysql'.format(MYSQL_PATH),'-u',USER,'-p{0}'.format(PASS),'aers','-e',"LOAD DATA INFILE '{0}' REPLACE INTO TABLE aers.{1} FIELDS TERMINATED BY '$';".format(f,tab)]
            t.execute(command, inputs=[f,'aers.{0}'.format(tab)], outputs=['aers.{0}'.format(tab)], replace=PASS)
            print "... done"
    
    print "DONE!"     
    t.serialize()  


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", help="The reporting year to convert to RDF",
                        type=int)
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--updateall", help="Download all AERS reports from FDA website",
                    action="store_true")
    group.add_argument("--updaterecent", help="Download only recent AERS reports from FDA website (the latest 4 quarters)",
                    action="store_true")
    args = parser.parse_args()

    if args.updateall :
        print "Downloading all AERS reports"
        downloadAERS(True)
    elif args.updaterecent :
        print "Downloading the four most recent AERS reports"
        downloadAERS(False)
    else :
        print "Not downloading any AERS reports"
    
    if args.year :
        year = int(args.year)
    else :
        year = datetime.now().year
        
    importToMySQL(year)
 
