import json, os, re
from pycsw.core import util
from pycsw.core.etree import etree

NAMESPACE = 'https://schema.org/'
NAMESPACES = {'sdo': NAMESPACE, 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}

XPATH_MAPPINGS = {
    'pycsw:Title': 'sdo:name',
    'pycsw:Identifier': 'sdo:identifier',
    'pycsw:Creator': 'sdo:provider',
    'pycsw:TopicCategory': 'sdo:keywords',
    'pycsw:Keywords': 'sdo:keywords',
    'pycsw:Abstract': 'sdo:description',
    'pycsw:Publisher': 'sdo:publisher',
    'pycsw:OrganizationName': 'sdo:provider',
    'pycsw:CreationDate': 'sdo:dateCreated',
    'pycsw:PublicationDate': 'sdo:datePublished',
    'pycsw:Format': 'sdo:distribution',
    'pycsw:ResourceLanguage': 'sdo:inLanguage',
    'pycsw:Relation': 'sdo:mentions',
    'pycsw:AccessConstraints': 'dif:Access_Constraints',
    'pycsw:TempExtent_begin': 'sdo:temporalCoverage',
    'pycsw:TempExtent_end': 'sdo:temporalCoverage',
    'pycsw:Modified': 'sdo:version',
    'pycsw:Links': 'sdo:mentions',
    'pycsw:AccessConstraints': 'sdo:license',
    'pycsw:OtherConstraints': 'sdo:conditionsOfAccess',
    'pycsw:Contributor': 'sdo:contributor'
}

def write_record(result, esn, context, url=None):
    typename = util.getqattr(result, context.md_core_model['mappings']['pycsw:Typename'])
    if esn == 'full' and typename == 'sdo:Dataset':
        # dump record as is and exit
        return etree.fromstring(util.getqattr(recobj, context.md_core_model['mappings']['pycsw:XML']), context.parser)
    
    node = etree.Element(util.nspath_eval('rdf:RDF', NAMESPACES), nsmap=NAMESPACES)
    rdfDescription = etree.SubElement(node,util.nspath_eval('rdf:Description', NAMESPACES), nsmap=NAMESPACES)

    rdfType = etree.SubElement(rdfDescription,util.nspath_eval('rdf:type', NAMESPACES), nsmap=NAMESPACES)
    rdfType.attrib['{' + NAMESPACES['rdf'] + '}resource'] = NAMESPACES['sdo'] + 'Dataset'
    
    #identifier, title, abstract, modified, format
    for qval in ['pycsw:Identifier',
                 'pycsw:Title',
                 'pycsw:Abstract',
                 'pycsw:Modified',
                 'pycsw:Format',
                 'pycsw:CreationDate',
                 'pycsw:PublicationDate',
                 'pycsw:Publisher',
                 'pycsw:Creator',
                 'pycsw:AccessConstraints',
                 'pycsw:OtherConstraints',
                 'pycsw:Contributor',
                 'pycsw:ResourceLanguage']:
        val = util.getqattr(result, context.md_core_model['mappings'][qval])
        if val:
            if qval in ['pycsw:Creator',
                        'pycsw:Publisher',
                        'pycsw:OrganizationName',
                        'pycsw:Contributor']:
                
                org = etree.SubElement(rdfDescription,util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES), nsmap=NAMESPACES)
                rdfd = etree.SubElement(org,util.nspath_eval('rdf:Description', NAMESPACES), nsmap=NAMESPACES)
                rdft = etree.SubElement(rdfd,util.nspath_eval('rdf:type', NAMESPACES), nsmap=NAMESPACES)
                orgN = etree.SubElement(rdfd, util.nspath_eval('sdo:name', NAMESPACES)).text = val
                rdft.attrib['{' + NAMESPACES['rdf'] + '}resource'] = NAMESPACES['sdo'] + 'Organization'
            else:
                etree.SubElement(rdfDescription, util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES)).text = val
    
    #keywords, links
    for qval in ['pycsw:Keywords',
                 'pycsw:TopicCategory',
                 'pycsw:Links',
                 'pycsw:Relation']:
        val = util.getqattr(result, context.md_core_model['mappings'][qval])
        if val:
            for kw in val.split(','):
                if qval in ['pycsw:Links']:
                    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                    if(len(re.findall(regex,kw) ) > 0):
                        etree.SubElement(rdfDescription, util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES)).text = kw.split('^')[0]
                else:
                    etree.SubElement(rdfDescription, util.nspath_eval(XPATH_MAPPINGS[qval], NAMESPACES)).text = kw
    
    # Temporal coverage
    dateRange = ''
    for qval in ['pycsw:TempExtent_begin',
                 'pycsw:TempExtent_end']:
        val = util.getqattr(result, context.md_core_model['mappings'][qval])
        if not val:
            val = ''
        if qval == 'pycsw:TempExtent_begin':
            if dateRange == '':
                pass
            else:
                if val == '':
                    val = '/..'
                else:
                    val = '/' + val
        dateRange = dateRange + val
    etree.SubElement(rdfDescription, util.nspath_eval(XPATH_MAPPINGS['pycsw:TempExtent_begin'], NAMESPACES)).text = val
    
    return node


