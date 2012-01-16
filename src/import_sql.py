import glob
import os
from d2s.prov import prov

MASK_TO_AERS_DATA = '../aers_data_files/AERS_ASCII_*/ascii/*.TXT'
USER = 'root'
PASS = 'ouCh1euk'

print "Will proceed to import all data"

# Copy all AERS data files to /tmp
print "Copying AERS data files from {0} to /tmp...".format(MASK_TO_AERS_DATA)
os.system('cp -v {0} /tmp'.format(MASK_TO_AERS_DATA))
print "... done"


print "Fixing INDI files with 'sed'"
os.system("sed -i 's/\\r/\\$\\r/g' /tmp/INDI*.TXT")
print "... done"


print "Using 'sed' to remove dates in all tables with value '00000000' to ensure XSD compliance."
os.system("sed -i 's/\\$00000000\\$/\\$\\$/g' /tmp/*.TXT")
print "... done"


command_template = "mysql -u {0} -p{1} aers -e \"LOAD DATA INFILE '{2}' REPLACE INTO TABLE aers.{3} FIELDS TERMINATED BY '$' IGNORE 1 LINES;\""

tables = ['demo', 'drug', 'indi', 'outc', 'reac', 'ther']

for t in tables :
    files = glob.glob('/tmp/{0}*.TXT'.format(t.upper()))
    print "Truncating table {0} ...".format(t)
    os.system('mysql -u {0} -p{1} aers -e \"TRUNCATE TABLE aers.{2};\"'.format(USER, PASS, t))
    print "... done"
    for f in files :
        print "Importing from {0} into {1} ...".format(f, t)
        command = command_template.format(USER, PASS, f, t)
        os.system(command)
        print "... done"
        
