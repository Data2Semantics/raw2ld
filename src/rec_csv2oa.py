'''
Created on Jun 19, 2012

@author: hoekstra
'''

import csv
import hashlib
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, Literal, BNode, RDF, RDFS

def addAnnotation(rec, level, evSummary, referenceNr, recInReference, evInReference):
#    print rec, level, evSummary, referenceNr, recInReference, evInReference
    
    # Remove the recommendation number from the rec string (as these do not appear in the actual text)
    rec = re.sub(r'(\d\.)+ (.*)',r'\2', rec)
    
    
    recHash = hashlib.md5(rec).hexdigest()
    recURI = ANNOTATION[recHash]
    
    cg.add((recURI, RDF.type, D2SA['RecommendationAnnotation']))
    cg.add((recURI, RDF.type, OA['Annotation']))
    
    if not rec.isupper() :
        target = TARGET[recHash]
        selector = SELECTOR[recHash]
        cg.add((recURI, OA['hasTarget'], target))
        cg.add((target, RDF.type, OA['SpecificResource']))
        cg.add((target, OA['hasSource'], source))
        cg.add((target, OA['hasSelector'], selector))
        
        cg.add((selector, RDF.type, OAX['TextQuoteSelector']))
        cg.add((selector, OAX['prefix'], Literal("")))
        cg.add((selector, OAX['exact'], Literal(rec.decode('utf-8'))))
        cg.add((selector, OAX['suffix'], Literal("")))
    else :
        target = TARGET[recHash]
        cg.add((recURI, OA['hasTarget'], source))
        
        cg.add((recURI, OA['hasBody'], Literal(rec.decode('utf-8').title().strip())))
        
    if level :
#        levelHash = hashlib.md5(level).hexdigest()
        levelURI = LEVEL[level]      
        
        cg.add((recURI, D2SA['hasLevel'], levelURI))
        cg.add((levelURI, RDFS.label, Literal(level))) 
        
    if evSummary :
        evsHash = hashlib.md5(evSummary).hexdigest()
        
        evsURI = SUMMARY[evsHash]
        target = TARGET[evsHash]
        selector = SELECTOR[evsHash]
        
        cg.add((recURI, D2SA['hasEvidenceSummary'], evsURI))
        
        cg.add((evsURI, RDF.type, D2SA['EvidenceSummaryAnnotation']))
        cg.add((evsURI, RDF.type, OA['Annotation']))
        
        cg.add((evsURI, OA['hasTarget'], target))
        cg.add((target, RDF.type, OA['SpecificResource']))
        cg.add((target, OA['hasSource'], source))
        cg.add((target, OA['hasSelector'], selector))
        
        cg.add((selector, RDF.type, OAX['TextQuoteSelector']))
        cg.add((selector, OAX['prefix'], Literal("")))
        cg.add((selector, OAX['exact'], Literal(evSummary.decode('utf-8'))))
        cg.add((selector, OAX['suffix'], Literal("")))
    
        if referenceNr :
            referenceNr = referenceNr.strip('[]')
            
            refSourceURI = URIRef(guideline + '/' + referenceNr)
            
            
            if recInReference :   
                recInRefHash = hashlib.md5(recInReference).hexdigest()
                recURI = URIRef(guideline + '/' + referenceNr + '/' + recInRefHash)
                
                target = TARGET[recInRefHash]
                selector = SELECTOR[recInRefHash]
                
                cg.add((evsURI, SWANREL['referencesAsSupportingEvidence'], recURI))
                
                cg.add((recURI, RDF.type, D2SA['EvidenceAnnotation']))
                cg.add((recURI, RDF.type, OA['Annotation']))
                
                cg.add((recURI, OA['hasTarget'], target))
                cg.add((target, RDF.type, OA['SpecificResource']))
                cg.add((target, OA['hasSource'], refSourceURI))
                cg.add((target, OA['hasSelector'], selector))
                
                cg.add((selector, RDF.type, OAX['TextQuoteSelector']))
                cg.add((selector, OAX['prefix'], Literal("")))
                cg.add((selector, OAX['exact'], Literal(recInReference.decode('utf-8'))))
                cg.add((selector, OAX['suffix'], Literal("")))
            
                if evInReference :
                    evInRefHash = hashlib.md5(evInReference).hexdigest()
                    evURI = URIRef(guideline + '/' + referenceNr + '/' + evInRefHash)
                    
                    target = TARGET[evInRefHash]
                    selector = SELECTOR[evInRefHash]
                    
                    cg.add((recURI, SWANREL['referencesAsSupportingEvidence'], evURI))
                    
                    cg.add((evURI, RDF.type, D2SA['EvidenceAnnotation']))
                    cg.add((evURI, RDF.type, OA['Annotation']))
                    
                    cg.add((evURI, OA['hasTarget'], target))
                    cg.add((target, RDF.type, OA['SpecificResource']))
                    cg.add((target, OA['hasSource'], refSourceURI))
                    cg.add((target, OA['hasSelector'], selector))
                    
                    cg.add((selector, RDF.type, OAX['TextQuoteSelector']))
                    cg.add((selector, OAX['prefix'], Literal("")))
                    cg.add((selector, OAX['exact'], Literal(evInReference.decode('utf-8'))))
                    cg.add((selector, OAX['suffix'], Literal("")))
            else :
                cg.add((evsURI, SWANREL['referencesAsSupportingEvidence'], refSourceURI))
                
                
                
                

def readCSV():
    print "Loading annotations from annotations-anita.csv"
    recReader = csv.reader(open('annotations-anita.csv', 'r'), delimiter=',', quotechar='"')
    
    rec = None
    level = None
    evSummary = None
    referenceNr = None
    recInReference = None
    evInReference = None
    
    for row in recReader :
        if row[0] != '':
            rec = row[0]
            level = None
            evSummary = None
            referenceNr = None
            recInReference = None
            evInReference = None

        if row[1] != '':
            level = row[1]
            evSummary = None
            referenceNr = None
            recInReference = None
            evInReference = None
            
        if row[2] != '':
            evSummary = row[2]
            referenceNr = None
            recInReference = None
            evInReference = None
            
        if row[3] != '':
            referenceNr = row[3]
            recInReference = None
            evInReference = None
            
        if row[4] != '':
            recInReference = row[4]
            evInReference = None    
            
        if row[5] != '':
            evInReference = row[5]
            
        if rec :
            addAnnotation(rec, level, evSummary, referenceNr, recInReference, evInReference)

if __name__ == '__main__':
    print "I'm going to read from a CSV file, but I won't check whether the file is suitable for me!"
    
    cg = ConjunctiveGraph()
    
    print "Loading reference mappings"
    cg.load(open('reference-mappings.n3','r'), format='n3')
    
    guideline = 'http://cid.oxfordjournals.org/content/52/4/e56.full'
    source = URIRef(guideline)
    
    
    DEFAULT = Namespace('http://aers.data2semantics.org/resource/')
    ANNOTATION = Namespace('http://aers.data2semantics.org/resource/annotation/')
    TARGET = Namespace('http://aers.data2semantics.org/resource/target/')
    SELECTOR = Namespace('http://aers.data2semantics.org/resource/selector/')
    LEVEL = Namespace('http://aers.data2semantics.org/resource/level/')
    SUMMARY = Namespace('http://aers.data2semantics.org/resource/summary/')
    REF = Namespace('http://aers.data2semantics.org/resource/reference/')
    
    
    D2SA = Namespace('http://aers.data2semantics.org/vocab/annotation/')
    OA = Namespace('http://www.w3.org/ns/openannotation/core/')
    OAX = Namespace('http://www.w3.org/ns/openannotation/extensions/')
    SWANREL = Namespace('http://purl.org/swan/2.0/discourse-relationships/')
    
    cg.bind('',DEFAULT)
#    cg.bind('annotation', ANNOTATION)
#    cg.bind('target', TARGET)
#    cg.bind('selector', SELECTOR)
#    cg.bind('level', LEVEL)
#    cg.bind('summary', SUMMARY)
#    cg.bind('ref',REF)
    cg.bind('oa',OA)
    cg.bind('oax',OAX)
    cg.bind('d2sa', D2SA)
    cg.bind('swanrel',SWANREL)
    
    
    
    readCSV()
    
    cg.serialize(open('output.n3','w'), format='n3')
        