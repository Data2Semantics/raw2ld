import glob
import os
from d2s.prov import Trace
import shlex





MASK_TO_AERS_DATA = '../aers_data_files/aers_ascii_2011q1/ascii/*.TXT'
MYSQL_PATH = '/usr/local/mysql-5.5.17-osx10.6-x86_64/bin'
USER = 'root'

PASS = 'visstick'
t = Trace(trailFile='out.ttl')

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
    files = glob.glob('/tmp/{0}11Q1.TXT'.format(tab.upper()))
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
