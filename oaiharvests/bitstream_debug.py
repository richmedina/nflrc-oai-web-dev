# bitstream_debug.py
from oaiharvests.utils import *
from oaiharvests.models import *

# Namespaces
rdf_ns = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
atom_ns = '{http://www.w3.org/2005/Atom}'
dc_ns = '{http://purl.org/dc/terms/}'

# base_url = 'https://api7.dspace.org/server/oai/request'
# demo_col = Collection.objects.get(identifier='col_10673_8223')


base_url = 'http://scholarspace.manoa.hawaii.edu/dspace-oai/request'
demo_col = Collection.objects.get(identifier='col_10125_35914')
record = demo_col.list_records().last()
record = Record.objects.get(identifier='oai:scholarspace.manoa.hawaii.edu:10125/44203')
sickle = Sickle(base_url)
sickle.class_mapping['GetRecord'] = LltRecordBitstream
rec_xml = sickle.GetRecord(metadataPrefix='ore', identifier=record.identifier)

tree = rec_xml.xml.find('.//' + rec_xml._oai_namespace + 'metadata').getchildren()[0]

doc_urls = tree.findall('.//'+atom_ns+'link') # Retrieves file/url info for primary bitstreams
txt_urls = tree.findall('.//'+rdf_ns+'Description') # Retrieves file/url info for ocr'ed pdfs

doc_bitstreams = []
txt_bitstreams = []
extra_bitstreams = []

for i in doc_urls:
    link_type = i.get('rel')
    if link_type == 'http://www.openarchives.org/ore/terms/aggregates':
        href = i.get('href')
        ftype = i.get('type')
        ftitle = i.get('title')
        doc_bitstreams.append((href, ftype, ftitle))

for i in txt_urls:
    link_type = i.find(rdf_ns+'type').get(rdf_ns+'resource')
    if link_type != 'http://www.dspace.org/objectModel/DSpaceItem':
        href = i.get(rdf_ns+'about')
        ftype = ''
        try:
            ftype = i.find(dc_ns+'description').text
        except Exception as e:
            pass
        if ftype == 'TEXT':
            txt_bitstreams.append((href, ftype))
    
