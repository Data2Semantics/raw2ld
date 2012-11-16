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

FDA_SITE = "www.fda.gov"
    
# All reports:
ALL_LOCATIONS = ["/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm083765.htm", "/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm"]

# Only latest year (for testing purposes):
RECENT_LOCATIONS = ["/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/ucm082193.htm"]


DOWNLOAD_LOC = "/downloads/Drugs/GuidanceComplianceRegulatoryInformation/Surveillance/AdverseDrugEffects/"
TARGET_PATH = "../aers_data_files/"

MASK_TO_AERS_DATA = '../aers_data_files/aers_ascii_20{}q1/ascii/*.TXT'
MYSQL_PATH = '/usr/local/mysql/bin'
USER = 'root'
PASS = 'visstick'

DUMP_RDF_PATH = '../../../srv/d2rq-0.8/'
DUMP_RDF_COMMAND = 'dump-rdf'
DUMP_RDF_MAPPING = '../d2r_mapping_aers.n3'

tables = ['demo', 'drug', 'indi', 'outc', 'reac', 'ther']

def downloadAERS(t, downloadAll = False):

    
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
                command = ["curl",url,"-o",target_file]
                inputs = [url]
                outputs = [target_file]
                
                t.execute(command,inputs=inputs,outputs=outputs)
            
            else :
                print "{0} already exists!".format(target_file)
            print "Done"
    
    print "All done downloading"
    
    for f in files :
        extract_path = f.rstrip('.ZIP')
        print "Extracting {0} to {1}".format(f, extract_path)
        if not(os.path.exists(extract_path)) :
            command = ["unzip",f,"-d",extract_path]
            inputs = [f]
            outputs = [extract_path]
            
            t.execute(command, inputs=inputs, outputs=outputs)
            
        else :
            print "{0} already exists!".format(extract_path)
        print "Done"
        
    print "All done extracting"


def importToMySQL(t, year):

    
    print "Will proceed to import all data from year {}".format(year)
    
    # Copy all AERS data files to /tmp
    print "Copying AERS data files from {0} to /tmp...".format(MASK_TO_AERS_DATA.format(year))
    for f in glob.glob(MASK_TO_AERS_DATA.format(year)) :
        (fpath,fname) = os.path.split(f)
        fnew = '/tmp/'+fname
        t.execute(['cp','-v',f,fnew],inputs=[f],outputs=[fnew])
    print "... done"
    
    
    
    print "Checking consistency of data files"
    for ftype in tables :
        files = glob.glob('/tmp/{0}{1}Q1.TXT'.format(ftype.upper(),year))
        for f in files :
            t.execute(['python','check_files.py',f,f+'.checked'], inputs=[f], outputs=[f+'.checked'])
        
    
    
    
    for tab in tables :
        files = glob.glob('/tmp/{0}{1}Q1.TXT.checked'.format(tab.upper(),year))
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
    


def createDump(t, dumpFile):
    dump_script = DUMP_RDF_PATH+DUMP_RDF_COMMAND
    
    
    
    command = [dump_script,'-m',DUMP_RDF_MAPPING,'-o',dumpFile]
    inputs = []
    outputs = []
    
    for tab in tables :
        inputs.append('aers.{}'.format(tab))
    
    inputs.append(DUMP_RDF_MAPPING)
    
    outputs.append(dumpFile)
    
    print "Calling rdf-dump script in {}".format(dump_script)
    t.execute(command, inputs=inputs, outputs=outputs)
    print "Done"
    
    
def import4store(t, dumpFile, graphURI):
    import_script = "4s-import"
    repository = "aers"
    
    
    command = [import_script,repository,"-v","--model",graphURI,dumpFile]
    inputs = [dumpFile]
    outputs = [graphURI]
    
    print "Calling 4s-import (Sandbox)"
    t.execute(command, inputs=inputs,outputs=outputs, sandbox=True)
    print "Done"
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", help="The reporting year to convert to RDF")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--updateall", help="Download all AERS reports from FDA website",
                    action="store_true")
    group.add_argument("--updaterecent", help="Download only recent AERS reports from FDA website (the latest 4 quarters)",
                    action="store_true")
    parser.add_argument("--dumptordf", help="Dump MySQL database to RDF", action="store_true")
    parser.add_argument("--import4store", help="Create provenance information for importing to 4Store", action="store_true")
    args = parser.parse_args()


    trailFile='../dumps/provenance-trail-{}.ttl'.format(datetime.strftime(datetime.now(),'%Y-%m-%d'))
    
    t = Trace(trailFile=trailFile,provns="http://aers.data2semantics.org/resource/prov/")


    if args.updateall :
        print "Downloading all AERS reports"
        downloadAERS(t, True)
    elif args.updaterecent :
        print "Downloading the four most recent AERS reports"
        downloadAERS(t, False)
    else :
        print "Not downloading any AERS reports"
    

    
    if args.year :
        if len(args.year) == 2 :
            year = args.year
        else :
            print "Using only the last two digits of {}".format(args.year)
            year = args.year[-2:]
        
        print "Uploading AERS reports from year {} to MySQL".format(year)
        importToMySQL(t, year)
    else :
        print "Not uploading any AERS reports to MySQL"
        
    if args.dumptordf :
        dumpFile='../dumps/dump-of-20{}-generated-on-{}.nt'.format(year, datetime.strftime(datetime.now(),'%Y-%m-%d'))
        print "Dumping contents of MySQL to {}".format(dumpFile)
        createDump(t, dumpFile)
    else :
        print "Not dumping to RDF"
        
    if args.import4store :
        graphURI = 'http://aers.data2semantics.org/resource/resource/' + dumpFile.lstrip('./')
        print "Importing dump file {} into 4Store graph {}".format(dumpFile, graphURI)
        import4store(t, dumpFile, graphURI)
        
    t.serialize(trailFile)  
        
    
 
