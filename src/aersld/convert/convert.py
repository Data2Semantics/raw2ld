import glob
import os
from datetime import datetime
import argparse
import httplib
import re
import urllib
from zipfile import ZipFile
#import shlex
import yaml
import requests
import sys
import logging

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

def download(t, locations, fda_base, download_location, aers_data_path):
    files = []
    
    for loc in locations :
        url = fda_base + loc
        data = requests.get(url).content
    
        for m in re.finditer(r'href="'+ download_location +'((UCM|ucm)\d+\.zip)">(AERS_ASCII_\d\d\d\dq\d\.ZIP)', data) :
            url = "{0}{1}{2}".format(fda_base,download_location,m.group(1))
            target_file = aers_data_path + m.group(3)
            files.append(target_file)
            log.info("Starting download of {0}...".format(m.group(3)))
            # print url
            if not(os.path.exists(target_file)) :
                command = ["curl",url,"-o",target_file]
                inputs = [url]
                outputs = [target_file]
                
                t.execute(command,inputs=inputs,outputs=outputs)
            
            else :
                log.warning("{0} already exists!".format(target_file))
            log.debug("Done")
    
    log.info("All done downloading")
    
    for f in files :
        extract_path = f.rstrip('.ZIP')
        log.info("Extracting {0} to {1}".format(f, extract_path))
        if not(os.path.exists(extract_path)) :
            command = ["unzip",f,"-d",extract_path]
            inputs = [f]
            outputs = [extract_path]
            
            t.execute(command, inputs=inputs, outputs=outputs)
            
        else :
            log.warning("{0} already exists!".format(extract_path))
        log.debug("Done")
        
    log.info("All done extracting")


def mysql_import(t, year, aers_data_mask, mysql_path, mysql_user, mysql_pass, temp_path):

    
    log.info("Will proceed to import all data from year {}".format(year))
    
    # Copy all AERS data files to /tmp
    log.info("Copying AERS data files from {0} to /tmp...".format(aers_data_mask.format(year)))
    for f in glob.glob(aers_data_mask.format(year)) :
        (fpath,fname) = os.path.split(f)
        fnew = '{}{}'.format(temp_path,fname)
        t.execute(['cp','-v',f,fnew],inputs=[f],outputs=[fnew])
    log.debug("... done")
    
    
    
    log.info("Checking consistency of data files")
    for ftype in tables :
        files = glob.glob('{0}{1}{2}Q1.TXT'.format(temp_path, ftype.upper(), year))
        for f in files :
            if not os.path.exists(f+'.checked'):
                t.execute(['python','check_files.py',f,f+'.checked'], inputs=[f], outputs=[f+'.checked'])
            else :
                log.info("{} already exists. {} has already been checked.".format(f+'.checked',f))
        
    
    for tab in tables :
        files = glob.glob('/tmp/{0}{1}Q1.TXT.checked'.format(tab.upper(),year))
        log.info("Truncating table {0} ...".format(tab))
        trunc_command = ['{0}mysql'.format(mysql_path),'-u',mysql_user,'-p{0}'.format(mysql_pass),'aers','-e','TRUNCATE TABLE aers.{0};'.format(tab)]
        t.execute(trunc_command, inputs=['aers.{0}'.format(tab)],outputs=['aers.{0}'.format(tab)],replace=PASS)
        log.debug("... done")
        
        for f in files :
            log.info("Importing from {0} into {1} ...".format(f, tab))
            command = ['{0}mysql'.format(mysql_path),'-u',mysql_user,'-p{0}'.format(mysql_pass),'aers','-e',"LOAD DATA INFILE '{0}' REPLACE INTO TABLE aers.{1} FIELDS TERMINATED BY '$';".format(f,tab)]
            t.execute(command, inputs=[f,'aers.{0}'.format(tab)], outputs=['aers.{0}'.format(tab)], replace=mysql_pass)
            log.debug("... done")
    
    log.info("MySQL import completed")     
    


def dump(t, dumpFile, dump_script, dump_rdf_mapping, dump_file):
    command = [dump_script,'-m',dump_rdf_mapping,'-o',dump_file]
    inputs = []
    outputs = []
    
    for tab in tables :
        inputs.append('aers.{}'.format(tab))
    
    inputs.append(dump_rdf_mapping)
    
    outputs.append(dumpFile)
    
    log.info("Calling rdf-dump script in {}".format(dump_script))
    t.execute(command, inputs=inputs, outputs=outputs)
    log.debug("Done")
    
    
def fourstore_import(t, dumpFile, graphURI):
    import_script = "4s-import"
    repository = "aers"
    
    
    command = [import_script,repository,"-v","--model",graphURI,dumpFile]
    inputs = [dumpFile]
    outputs = [graphURI]
    
    print "Calling 4s-import (Sandbox)"
    t.execute(command, inputs=inputs,outputs=outputs, sandbox=True)
    print "Done"
    





## GLOBAL SETTINGS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

logHandler = logging.StreamHandler()
logHandler.setLevel(logging.DEBUG)

logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(logFormatter)

log.addHandler(logHandler)



if __name__ == '__main__':
    log.debug("Parsing command line arguments")
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="The YAML configuration file to use", default='config.yaml')
    parser.add_argument("--year", help="The reporting year to convert to RDF")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--updateall", help="Download all AERS reports from FDA website",
                    action="store_true")
    group.add_argument("--updaterecent", help="Download only recent AERS reports from FDA website (the latest 4 quarters)",
                    action="store_true")
    parser.add_argument("--dumptordf", help="Dump MySQL database to RDF", action="store_true")
    parser.add_argument("--import4store", help="Create provenance information for importing to 4Store", action="store_true")
    parser.add_argument("--trailfile", help="Specify existing Prov-O-Matic trailfile to append to")
    args = parser.parse_args()

    # Load configuration file
    log.debug("Loading configuration file from {}".format(args.config))
    config = yaml.load(open(args.config, "r"))



    # Set the base directory for conversion output
    output_base = config['output']['base']
    log.debug("Output base directory is {}".format(output_base))
              
    if not os.path.exists(output_base):
        log.info("Creating {} for output".format(output_base))
        os.makedirs(output_base)
  
  
  
    ## PROV-O-MATIC
    
    log.debug("Initializing Prov-O-Matic")
    # Add Prov-O-Matic to the python path
    sys.path.append(config['provomatic'])
    
    # Import Prov-O-Matic
    from provomatic.prov import Trace
    
    # Create a Prov-O-Matic instance
    if args.trailfile :
        trailFile = args.trailfile
    else :
        trailFile = '{}provenance-trail-{}.ttl'.format(output_base, datetime.strftime(datetime.now(),'%Y-%m-%d'))
        
    t = Trace(trailFile=trailFile,provns="http://aers.data2semantics.org/resource/prov/")

    
    ## AERS DOWNLOAD

    # Set locations for AERS downloads
    fda_base = config['fda']['url']
    download_location = config['fda']['download']
    aers_data_path = output_base + config['output']['aers_data_dir']
    aers_data_mask = output_base + config['output']['aers_data_mask']
    
    if not os.path.exists(aers_data_path) :
        log.info("Creating {} for downloaded AERS data files".format(aers_data_path))
        os.makedirs(aers_data_path)

    if args.updateall :
        log.info("Downloading all AERS reports")
        locations = config['fda']['locations']['all']
        download(t, locations, fda_base, download_location, aers_data_path)
    elif args.updaterecent:
        log.info("Downloading the four most recent AERS reports")
        locations = config['fda']['locations']['recent']
        download(t, locations, fda_base, download_location, aers_data_path)
    else :
        log.info("Not downloading any AERS reports")

    
    
    ## MYSQL IMPORT
    
    log.info("Initializing MySQL Import")
    
    mysql_path = config['mysql']['path']
    mysql_user = config['mysql']['user']
    mysql_pass = config['mysql']['pass']
    temp_path = config['output']['temp']
    
    if args.year :
        if len(args.year) == 2 :
            year = args.year
        else :
            log.warning("Using only the last two digits of {}".format(args.year))
            year = args.year[-2:]
        
        log.info("Uploading AERS reports from year {} to MySQL".format(year))
        
        mysql_import(t, year, aers_data_mask, mysql_path, mysql_user, mysql_pass, temp_path)
    else :
        log.warning("Not uploading any AERS reports to MySQL")
        
       
    ## RDF DUMP   
    
    dump_script = config['d2rq']['path'] + 'dump-rdf'
    dump_rdf_mapping = config['d2rq']['mapping']
    
    if args.dumptordf and args.year:
        dump_file ='{}/dump-of-20{}-generated-on-{}.nt'.format(output_base, year, datetime.strftime(datetime.now(),'%Y-%m-%d'))
        log.info("Dumping contents of MySQL to {}".format(dump_file))
        dump(t, dump_file, dump_script, dump_rdf_mapping, dump_file)
    else :
        log.warning("Not dumping to RDF")

    ## 4STORE IMPORT
        
    if args.import4store :
        graphURI = 'http://aers.data2semantics.org/resource/resource/' + dump_file.lstrip('./')
        log.info("Importing dump file {} into 4Store graph {}".format(dump_file, graphURI))
        fourstore_import(t, dump_file, graphURI)
    else :
        log.warning("Not importing into 4Store")

    log.info("Serializing Prov-O-Matic trail to {}".format(trailFile))        
    t.serialize(trailFile)  
    
    log.info("Done!")
        
    
 
