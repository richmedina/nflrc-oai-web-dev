from oaiharvests.models import Repository, Community, Collection
from oaiharvests.utils import batch_harvest_articles, OAIUtils, LltRecordBitstream
from sickle import Sickle

oai = OAIUtils()

# base_url = 'http://scholarspace.manoa.hawaii.edu/dspace-oai/request'
base_url = 'https://api7.dspace.org/server/oai/request'
sickle = Sickle(base_url)
community = Community.objects.all()[1]
record_headers = sickle.ListIdentifiers(metadataPrefix='oai_dc', set=community.identifier)
cols = oai.list_oai_collections(community)

demo_col = Collection.objects.get(identifier='col_10673_8223')
# feb = Collection.objects.get(identifier='col_10125_58892')


# records = oai.harvest_oai_collection_records_sickle(feb)
records = sickle.ListRecords(metadataPrefix='dim', set=demo_col.identifier)
# records = sickle.ListRecords(metadataPrefix='dim', set='col_10125_75793')

# Null Collections:
# https://scholarspace.manoa.hawaii.edu/dspace-oai/request?verb=ListIdentifiers&metadataPrefix=oai_dc&set=com_10125_27123
# 58896 https://scholarspace.manoa.hawaii.edu/handle/10125/58896
# 70101 https://scholarspace.manoa.hawaii.edu/handle/10125/70101
# 73416 https://scholarspace.manoa.hawaii.edu/handle/10125/73416
# 75793 https://scholarspace.manoa.hawaii.edu/handle/10125/75793

