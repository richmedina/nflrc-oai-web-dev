from oaiharvests.models import Repository, Community, Collection
from oaiharvests.utils import batch_harvest_articles, OAIUtils
from sickle import Sickle

oai = OAIUtils()

base_url = 'http://scholarspace.manoa.hawaii.edu/dspace-oai/request'
sickle = Sickle(base_url)
community = Community.objects.get()
record_headers = sickle.ListIdentifiers(metadataPrefix='oai_dc', set=community.identifier)
cols = oai.list_oai_collections(community)

october = Collection.objects.get(identifier='col_10125_58896')
feb = Collection.objects.get(identifier='col_10125_58892')


# records = oai.harvest_oai_collection_records_sickle(feb)
records = sickle.ListRecords(metadataPrefix='dim', set=feb.identifier)
records = sickle.ListRecords(metadataPrefix='dim', set='col_10125_75793')

# Null Collections:
# https://scholarspace.manoa.hawaii.edu/dspace-oai/request?verb=ListIdentifiers&metadataPrefix=oai_dc&set=com_10125_27123
# 58896 https://scholarspace.manoa.hawaii.edu/handle/10125/58896
# 70101 https://scholarspace.manoa.hawaii.edu/handle/10125/70101
# 73416 https://scholarspace.manoa.hawaii.edu/handle/10125/73416
# 75793 https://scholarspace.manoa.hawaii.edu/handle/10125/75793

