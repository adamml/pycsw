import json, os
from pycsw.core import util
from pycsw.core.etree import etree

NAMESPACE = 'https://schema.org/'
NAMESPACES = {'sdo': NAMESPACE, 'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}

XPATH_MAPPINGS = {
    'pycsw:Title': 'sdo:name',
    'pycsw:Creator': 'dif:Data_Set_Citation/dif:Dataset_Creator',
    'pycsw:TopicCategory': 'dif:ISO_Topic_Category',
    'pycsw:Keywords': 'dif:Keyword',
    'pycsw:Abstract': 'sdo:description',
    'pycsw:Publisher': 'dif:Data_Set_Citation/dif:Dataset_Publisher',
    'pycsw:OrganizationName': 'dif:Originating_Center',
    'pycsw:CreationDate': 'dif:DIF_Creation_Date','pycsw:PublicationDate': 'dif:Data_Set_Citation/dif:Dataset_Release_Date',
    'pycsw:Format': 'dif:Data_Set_Citation/dif:Data_Presentation_Form',
    'pycsw:ResourceLanguage': 'dif:Data_Set_Language',
    'pycsw:Relation': 'dif:Related_URL/dif:URL',
    'pycsw:AccessConstraints': 'dif:Access_Constraints',
    'pycsw:TempExtent_begin': 'dif:Temporal_Coverage/dif:Start_Date',
    'pycsw:TempExtent_end': 'dif:Temporal_Coverage/dif:Stop_Date',
}

def write_record(result, esn, context, url=None):
    typename = util.getqattr(result, context.md_core_model['mappings']['pycsw:Typename'])
    if esn == 'full' and typename == 'sdo:Dataset':
        # dump record as is and exit
        return etree.fromstring(util.getqattr(recobj, context.md_core_model['mappings']['pycsw:XML']), context.parser)
    
    node = etree.Element(util.nspath_eval('rdf:RDF', NAMESPACES), nsmap=NAMESPACES)
    rdfDescription = etree.SubElement(node,util.nspath_eval('rdf:Description', NAMESPACES), nsmap=NAMESPACES)
    rdfType = etree.SubElement(rdfDescription,util.nspath_eval('rdf:type', NAMESPACES), nsmap=NAMESPACES)
    rdfType.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'] = 'https://schema.org/Dataset'
    
    # title
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Title'])
    if not val:
        val = ''
    etree.SubElement(rdfDescription, util.nspath_eval('sdo:name', NAMESPACES)).text = val
    
    # description
    val = util.getqattr(result, context.md_core_model['mappings']['pycsw:Abstract'])
    if not val:
        val = ''
    etree.SubElement(rdfDescription, util.nspath_eval('sdo:description', NAMESPACES)).text = val
    
    return node
