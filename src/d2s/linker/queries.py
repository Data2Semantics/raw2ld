'''
Created on Jul 17, 2012

@author: hoekstra
'''

class Queries(object):
    '''
    classdocs
    '''
    
    # Define prefixes for the SPARQL queries
    prefixes = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
        PREFIX dbpedia: <http://dbpedia.org/resource/>
        PREFIX aers-vocab: <http://aers.data2semantics.org/vocab/>
        PREFIX aers: <http://aers.data2semantics.org/resource/>
        PREFIX sider: <http://www4.wiwiss.fu-berlin.de/sider/resource/sider/>
        PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX ct: <http://data.linkedct.org/resource/linkedct/>
        PREFIX calbc: <http://linkedlifedata.com/resource/calbc/>
        PREFIX calbc-group: <http://linkedlifedata.com/resource/calbc/group/>
        PREFIX drugbank: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/>
        PREFIX ctcae: <http://ncicb.nci.nih.gov/xml/owl/EVS/ctcae.owl#>
    """


#    aers_drug = prefixes + """
#    SELECT DISTINCT ?resource ?label WHERE {
#        ?resource   rdf:type    aers-vocab:Drug .
#        ?resource   rdfs:label  ?label . 
#    } 
#    """
#    
#    aers_drug_related = prefixes + """
#    SELECT DISTINCT ?resource ?label WHERE {
#        ?resource   rdf:type    aers-vocab:Drug .
#        { ?resource   rdfs:label  ?label . }
#        UNION 
#        { ?resource skos:relatedMatch ?relresource .
#          ?relresource rdfs:label ?label .}
#    } 
#    """

    aers_country = prefixes + """
        SELECT DISTINCT ?resource ?label WHERE {
            ?resource   rdf:type    aers-vocab:Country .
            ?resource   rdfs:label  ?label .
        } 
    """
    
    
#    aers_diagnosis = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            {
#                ?resource   rdf:type    aers-vocab:Diagnosis . 
#                ?resource   rdfs:label  ?label .
#            }
#            UNION
#            {   ?resource   rdf:type    aers-vocab:Reaction . 
#                ?resource   rdfs:label  ?label .
#            }
#        } 
#    """
    
    ctcae = prefixes + """
        SELECT DISTINCT ?resource ?label WHERE {
            ?resource   rdf:type    owl:Class .
            ?resource   rdfs:label  ?label .
        }
    """
    
    
#    dbpedia_drug = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            {
#                ?resource   rdf:type    dbpedia-owl:Drug .
#                ?resource   rdfs:label  ?label .
#            } 
#            UNION
#            {
#                ?resource   rdf:type    dbpedia-owl:Drug .
#                ?label      dbpedia-owl:wikiPageRedirects ?resource .
#            }
#            UNION
#            {
#                ?resource   rdf:type    dbpedia-owl:ChemicalCompound .
#                ?resource   rdfs:label  ?label .
#            } 
#            UNION
#            {
#                ?resource   rdf:type    dbpedia-owl:ChemicalCompound .
#                ?label      dbpedia-owl:wikiPageRedirects ?resource .
#            } 
#            UNION
#            {
#                ?resource   rdf:type    dbpedia-owl:ChemicalSubstance .
#                ?resource   rdfs:label  ?label .
#            } 
#            UNION
#            {
#                ?resource   rdf:type    dbpedia-owl:ChemicalSubstance .
#                ?label      dbpedia-owl:wikiPageRedirects ?resource .
#            }
#        } 
#    """
    
    dbpedia_country = prefixes + """
        SELECT DISTINCT ?resource ?label WHERE {
            {
                ?resource   rdf:type    dbpedia-owl:Country .
                ?resource   rdfs:label  ?label .
            } 
            UNION
            {
                ?resource   rdf:type    dbpedia-owl:Country .
                ?label      dbpedia-owl:wikiPageRedirects ?resource .
            }
        } 
    """
    
#    sider_drug = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            {
#                ?resource   rdf:type    sider:drugs .
#                ?resource   rdfs:label  ?label .
#            }
#            UNION
#            {
#                ?resource   rdf:type        sider:drugs .
#                ?resource   sider:drugName  ?label .
#            }    
#            FILTER(?resource != <http://www4.wiwiss.fu-berlin.de/sider/resource/drugs/2232>)
#        }
#    """
    
#    sider_effect = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            {
#                ?resource   rdf:type    sider:side_effects .
#                ?resource   rdfs:label  ?label .
#            }
#            UNION
#            {
#                ?resource   rdf:type              sider:side_effects .
#                ?resource   sider:sideEffectName  ?label .
#            }    
#        }
#    """
    
#    linkedct_condition = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            ?resource   rdf:type            ct:condition .
#            ?resource   ct:condition_name   ?label .
#        }
#    """
    
#    umls_drug = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            { 
#                ?resource   calbc:hasCorrelation       calbc-group:CHEM .
#                ?resource   skos-xl:prefLabel   ?prefLabel .
#                ?prefLabel  skos-xl:literalForm ?label . 
#            }
#            UNION
#            { 
#                ?resource   calbc:hasCorrelation       calbc-group:CHEM .
#                ?resource   skos-xl:altLabel   ?altLabel .
#                ?altLabel   skos-xl:literalForm ?label .        
#            }
#        }"""
        
#    umls_diagnosis = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            { 
#                ?resource   calbc:hasCorrelation       calbc-group:DISO .
#                ?resource   skos-xl:prefLabel   ?prefLabel .
#                ?prefLabel  skos-xl:literalForm ?label . 
#            }
#            UNION
#            { 
#                ?resource   calbc:hasCorrelation       calbc-group:DISO .
#                ?resource   skos-xl:altLabel   ?altLabel .
#                ?altLabel   skos-xl:literalForm ?label .        
#            }
#        }
#    """
    
#    drugbank_drug = prefixes + """
#        SELECT DISTINCT ?resource ?label WHERE {
#            ?resource   rdf:type    drugbank:drugs .
#            {
#                ?resource   drugbank:brandName  ?label .
#            }
#            UNION
#            {
#                ?resource   drugbank:synonym  ?label .
#            }
#            UNION
#            {
#                ?resource   rdfs:label  ?label .
#            }        
#        }
#    """

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    