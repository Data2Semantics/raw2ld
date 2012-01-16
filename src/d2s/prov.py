'''
Created on 16 Jan 2012

@author: hoekstra
'''

from rdflib import ConjunctiveGraph, Graph, Namespace, URIRef, Literal, BNode, RDF, RDFS, OWL 
from subprocess import call
from datetime import datetime
from urllib import quote
from optparse import OptionParser, OptionValueError
import shlex
import logging

class Trace(object):
    '''
    classdocs
    '''
    
    def __init__(self, provns = "http://www.example.com/prov/", logLevel = logging.DEBUG):
        '''
        Constructor
        '''
        
        # Initialise logger
        
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logLevel)
        
        logHandler = logging.StreamHandler()
        logHandler.setLevel(logging.DEBUG)
        
        logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logHandler.setFormatter(logFormatter)
        
        self.log.addHandler(logHandler)
        
        # Initialise graph
        
        self.log.debug("Initialising graph")
        self.g = ConjunctiveGraph()

        
        self.log.debug("Initialising namespaces")
        self.PROVO = Namespace("http://www.w3.org/ns/prov-o/")
        self.D2S = Namespace("http://www.data2semantics.org/provenance-ontology/")
        self.FRBR = Namespace("http://purl.org/vocab/frbr/core#")
        self.TIME = Namespace("http://www.w3.org/2006/time#")
        self.PROVNS = Namespace(provns)
        
        self.log.debug("Binding namespace prefixes")
        self.g.bind("prov-o", self.PROVO)
        self.g.bind("d2sprov", self.D2S)
        self.g.bind("frbr", self.FRBR)
        self.g.bind("time", self.TIME)
        self.g.bind("provns", self.PROVNS)
        
        self.log.debug("Initialised")
        
        return
    
    def execute(self, params = [], inputs = [], outputs = [], replace = None, logOutput = True):
        '''
        Calls a commandline using subprocess.call, and captures relevant provenance information
            @param params - A list of strings used as arguments to the subprocess.call method
            @param inputs - A list of strings (QNames) for all input resources
            @param outputs - A list of strings (QNames) for all output resources
            @param replace - A string that should not be reported in in the provenance trail (e.g. a password)
            @param logOutput - A boolean option for capturing the output of the shell script in an rdfs:comment field
        '''
        
        commandURI = self.mintActivity(params[0])
        
        start = self.mintTime()
        self.g.add((commandURI, self.PROVO['startedAt'], start))
        
        for p in params[1:] :
            if replace :
                p = p.replace(replace, 'HIDDENVALUE')
            if p in inputs :
                # p is an input to the process, and thus a resource by itself
                # p is a frbr:Expression (version) of a work (e.g. we could generate multiple versions of the same file)
                pExpressionURI = self.mintExpression(p)
                self.g.add((commandURI, self.PROVO['used'], pExpressionURI))
            elif p in outputs :
                pExpressionURI = self.mintExpression(p)
                self.g.add((pExpressionURI, self.PROVO['wasGeneratedBy'], commandURI))
            else :
                self.g.add((commandURI, self.D2S['parameter'], Literal(p)))
                
        if logOutput :
            out = open('prov.tmp', mode = 'rw')
            self.log.debug("Executing {0}".format(params))
            exit_status = call(params, stdout = out)
            self.log.debug("Exit status: {0}".format(exit_status))
            output = out.read()
            self.log.debug("Output:\n{0}".format(output))
            if logOutput :
                self.g.add((commandURI, RDFS.comment, Literal(output)))
            out.close()
        else :
            self.log.debug("Executing {0}".format(params))
            exit_status = call(params)
            self.log.debug("Exit status: {0}".format(exit_status))
            
        
        end = self.mintTime()
        self.g.add((commandURI, self.PROVO['endedAt'], end))
        
        return
    
    
    def mintActivity(self, p):
        p = quote(p, safe='~/')
        commandURI = self.PROVNS["{0}_{1}".format(p, datetime.now().isoformat())]
        commandTypeURI = self.D2S[p.capitalize()]
        
        self.g.add((commandTypeURI, RDFS.subClassOf, self.PROVO['Activity']))
        self.g.add((commandURI, RDF.type, commandTypeURI))
        
        return commandURI
    
    def mintTime(self):
        time = BNode()
        now = datetime.now().isoformat()
        self.g.add((time, RDF.type, self.TIME['Instant']))
        self.g.add((time, self.TIME['inXSDDateTime'], Literal(now)))
        
        return time
        
    def mintExpression(self, p):
        p = quote(p, safe='~/')
        pExpressionURI = self.PROVNS["{0}_{1}".format(p, datetime.now().isoformat())]
        
        self.g.add((self.PROVNS[p], RDF.type, self.FRBR['Work']))
        self.g.add((pExpressionURI, RDF.type, self.FRBR['Expression']))
        self.g.add((pExpressionURI, RDF.type, self.PROVO['Entity']))
                
        self.g.add((pExpressionURI, self.FRBR['realizationOf'], self.PROVNS[p]))
        
        return pExpressionURI
    
    
    
    def serialize(self, file = 'out.ttl'):
        return self.g.serialize(file, format='turtle')
    





def checkNS(option, opt, value, parser):
    if value.endswith('/') or value.endswith('#') :
        setattr(parser.values, option.dest, value)
    else :
        raise OptionValueError("NAMESPACE should end with a / or # character")






if __name__ == '__main__':
    usage = "usage: %prog [options] \"shell-command\""
    parser = OptionParser(usage=usage)
    parser.add_option("--prov-ns", type="string", action="callback", callback=checkNS, metavar="NAMESPACE", dest="provns", help="Where NAMESPACE is the target namespace for generated resources (should end with # or /)")
    parser.add_option("--prov-destination", type="string", metavar="FILE", dest="destination", help="Serialize the generated RDF graph to FILE (default is 'out.ttl')", default='out.ttl')
    parser.add_option("--prov-inputs", type="string", metavar="INPUTS", dest="inputs", help="Comma separated list of input resources (QNames) for this activity")
    parser.add_option("--prov-outputs", type="string", metavar="OUTPUTS", dest="outputs", help="Comma separated list of output resources (QNames) for this activity")
    parser.add_option("--prov-hide", type="string", dest="hidden", help="String to hide from provenance record (e.g. passwords)")
    (option,args) = parser.parse_args()
    
    print option
    print args
    
    if option.inputs:
        splitter = shlex.shlex(option.inputs, posix=True)
        splitter.whitespace = ','
        splitter.whitespace_split = True
        trace_inputs = list(splitter)
    else :
        trace_inputs = []
    if option.outputs:
        splitter = shlex.shlex(option.outputs, posix=True)
        splitter.whitespace = ','
        splitter.whitespace_split = True
        trace_outputs = list(splitter)
    else :
        trace_outputs = []
    
    if option.provns :
        t = Trace(provns=option.provns)
    else :
        t = Trace()
    
    for command in args :
        splitter = shlex.shlex(command, posix=True)
        splitter.whitespace = ' '
        splitter.whitespace_split = True
        command_call = list(splitter)
        t.execute(command_call, inputs=trace_inputs, outputs=trace_outputs, replace=option.hidden)
    
    t.serialize(file=option.destination)