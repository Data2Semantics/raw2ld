'''
Created on 19 Jan 2012

@author: hoekstra
'''

from pprint import pprint

def doprint(string=''):
    return string

def lookat(statement):
    print statement
    
    eval(statement)
    
    if hasattr(statement,'__call__') :
        print "call!"
        
    if callable(statement) :
        print dir(statement)
        



if __name__ == '__main__':
    