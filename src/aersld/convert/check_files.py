'''
Created on 17 Jan 2012

@author: hoekstra
'''
import re
from optparse import OptionParser, OptionValueError

def checkFile(f, fout):
    print "\nFile: " + f
    file = open(f, mode = 'r' )
    cfile = open(fout, mode = 'w')
    
    firstline = file.next()
    print "Headers: " + firstline
    if 'INDI' in f :
        cols = firstline.count('$')
    else :
        cols = firstline.count('$') + 1
    
    print "Expecting {0} columns".format(cols)
    
    for l in file :
        cline = l
        
        if l.count('$') < cols :
            print "Unexpected line break"
            concat = ''
            next = file.next()
            while next.strip() == '' :
                concat += next
                next = file.next()
            cline = cline.rstrip() + concat.rstrip() + next.rstrip()  

            if cline.count('$') == cols :
                print "... fixed"
                
            else :
                print "Incomplete fix"
                print "old: " + l
                print "new: " + cline
              
            
        if 'INDI' in f :
            cline = re.sub(r'\r\n','$\n',cline)    
        else :
            cline = re.sub(r'\$\r\n','$\n',cline)
        
        cline = re.sub(r'\$00000000\$','$$',cline)
        cfile.write(cline)
    file.close()
    cfile.close()
    print "Removed silly line breaks and fixed line endings"
    print "Removed invalid date values ('00000000')"

if __name__ == '__main__':
    usage = "usage: %prog \"path-to-file\" \"path-to-checked-file\""
    parser = OptionParser(usage=usage)
    (option,args) = parser.parse_args()
    
    checkFile(args[0], args[1])
    
