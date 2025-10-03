import datetime
import uuid
import json
import csv
from bs4 import BeautifulSoup
from oaiharvests.models import Collection

def get_crossref_timestamp():
    """
    Returns the current timestamp in the format YYYYMMDDHHMMSSsss
    where 'sss' is the milliseconds.
    """
    dt = datetime.datetime.now()
    return dt.strftime("%Y%m%d%H%M%S%f")[:-3]

def get_crossref_doi_batch_id(tag):
    """
    Generates a GUID-like string using the current timestamp (milliseconds),
    a short string, and a random UUID4 segment.
    """
    dt = datetime.datetime.now()
    timestamp = dt.strftime("%Y%m%d%H%M%S") + dt.strftime("%f")[:3]  # YYYYMMDDHHMMSSmmm
    random_part = uuid.uuid4().hex[:4]  # 8 hex digits for extra uniqueness
    return f"{timestamp}-{tag}-{random_part}"

def generate_crossref_doi_xml_submission(base_xml_file, record):
    """
    Generates a Crossref XML file for a single record.
    """
    article_data = record.as_dict()
    filename = 'doi_' + article_data['identifier.uri'][0].split('/')[-1] + '.xml'
    
    # Load the base XML template
    xml_file = base_xml_file # 'crossref-schema-base.xml'
    with open(xml_file, 'r') as file:
        xml_content = file.read()

    base = BeautifulSoup(xml_content, 'xml')

    doi_batch_id = base.find('doi_batch_id')
    doi_batch_id.string = get_crossref_doi_batch_id('nflrc')  # Update DOI batch ID

    timestamp = base.find('timestamp')
    timestamp.string = get_crossref_timestamp()  # Update timestamp
    journal = base.find('journal')

    journal_issue = base.new_tag('journal_issue')
    publication_date = base.new_tag('publication_date', attrs={'media_type': 'online'})    
    issue_year = base.new_tag('year') #
    issue_year.string = article_data['date.issued'][0][:4]
    publication_date.append(issue_year)
    journal_issue.append(publication_date)
    journal.append(journal_issue)
    
    journal_volume = base.new_tag('journal_volume')
    volume_number = base.new_tag('volume')
    volume_number.string = article_data['volume'][0]
    journal_volume.append(volume_number)
    journal_issue_number = base.new_tag('issue') 
    journal_issue_number.string = article_data['number'][0]
    journal_issue.append(journal_volume)
    journal_issue.append(journal_issue_number)    
    
    # # Create a new journal article element
    journal_article = base.new_tag('journal_article')
    
    title = base.new_tag('titles')
    title_tag = base.new_tag('title')
    title_tag.string = article_data['title'][0]  # Add article title
    title.append(title_tag)
    journal_article.append(title)
    
    contributors = base.new_tag('contributors')
    authors = article_data['contributor.author']
    for i, author_name in enumerate(authors):
        person_name = base.new_tag('person_name')
        person_name['contributor_role'] = 'author'
        if i == 0:
            person_name['sequence'] = 'first'
        else:
            person_name['sequence'] = 'additional'            
        given_name = base.new_tag('given_name')
        surname = base.new_tag('surname')
        orcid = base.new_tag('ORCID')
        namesplit = author_name.split(',')
        if len(namesplit) < 2:
            namesplit = author_name.split(' ')            
        given_name.string = namesplit[1].strip()
        surname.string = namesplit[0].strip()
        orcid.string = 'https://orcid.org/0000-0000-0000-0000'  # Placeholder ORCID
        person_name.append(given_name)
        person_name.append(surname)
        person_name.append(orcid)
        contributors.append(person_name)      
    journal_article.append(contributors)

    try:
        abstract = base.new_tag('jats:abstract', attrs={'xml:lang': 'en'})
        p_tag = base.new_tag('jats:p')
        p_tag.string = article_data['description.abstract'][0]
        abstract.append(p_tag)
        journal_article.append(abstract)
    except:
        pass

    date_str = article_data['date.issued'][0] 
    date_issued = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    pub_date = base.new_tag('publication_date', attrs={'media_type': 'online'})
    month = base.new_tag('month')
    month.string = str(date_issued.month)  # Add month
    day = base.new_tag('day')
    day.string = str(date_issued.day)  # Add day
    year = base.new_tag('year')
    year.string = str(date_issued.year)  # Add year
    pub_date.append(month)
    pub_date.append(day)
    pub_date.append(year)
    journal_article.append(pub_date)

    try:
        pages = base.new_tag('pages')
        first_page = base.new_tag('first_page')
        first_page.string = article_data['startingpage'][0]  # Add first page
        last_page = base.new_tag('last_page')
        last_page.string = article_data['endingpage'][0]  # Add last page
        pages.append(first_page)
        pages.append(last_page)
        journal_article.append(pages)
    except Exception as e:
        print(filename, title_tag.string)
        print("Error adding pages:", e, "\n\n")

    license = base.new_tag('ai:program', attrs={'name': 'AccessIndicators'})
    license_ref = base.new_tag('ai:license_ref')
    license_ref.string = 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
    license.append(license_ref)
    journal_article.append(license)

    handle_uri = article_data.get('identifier.uri', '')[0]
    doi_data = base.new_tag('doi_data')
    doi = base.new_tag('doi')
    doi.string = handle_uri.replace('https://hdl.handle.net', '10.64152')
    resource = base.new_tag('resource')
    resource.string = handle_uri  # Use the handle URI as the resource URL
    doi_data.append(doi)
    doi_data.append(resource)
    journal_article.append(doi_data)

    journal.append(journal_article)
    # Write the updated XML to a new file
    with open(filename, 'w') as file:
        file.write(str(base))

def generate_crossref_xml(base_xml_file, collection):
    """
    Generates a Crossref XML file with data extracted from a collection.
    """
    records = collection.list_records()
    if not records:
        print("No records found in the collection.")
        return
    
    filename = 'v'+records[0].get_metadata_item('volume')[0][0] + 'n' + records[0].get_metadata_item('number')[0][0] + '_crossref.xml'
    # print(filename)

    # Load the base XML template
    xml_file = base_xml_file # 'crossref-schema-base.xml'
    with open(xml_file, 'r') as file:
        xml_content = file.read()

    base = BeautifulSoup(xml_content, 'xml')

    doi_batch_id = base.find('doi_batch_id')
    doi_batch_id.string = get_crossref_doi_batch_id('nflrc')  # Update DOI batch ID

    timestamp = base.find('timestamp')
    timestamp.string = get_crossref_timestamp()  # Update timestamp
    journal = base.find('journal')

    journal_issue = base.new_tag('journal_issue')
    publication_date = base.new_tag('publication_date', attrs={'media_type': 'online'})    
    issue_year = base.new_tag('year') #
    issue_year.string = str(collection.get_collection_date().year)
    publication_date.append(issue_year)
    journal_issue.append(publication_date)
    journal.append(journal_issue)
    
    try:
        journal_volume = base.new_tag('journal_volume')
        volume_number = base.new_tag('volume')
        volume_number.string = records[0].get_metadata_item('volume')[0][0]
        journal_volume.append(volume_number)
        journal_issue_number = base.new_tag('issue') 
        journal_issue_number.string = records[0].get_metadata_item('number')[0][0] 
        journal_issue.append(journal_volume)
        journal_issue.append(journal_issue_number)    
    except Exception as e:
        print(filename, records[0])
        print('Error retrieving volume or number', e, "\n\n")
    
    
    for article in records:
        article_data = article.as_dict()
        # # Create a new journal article element
        journal_article = base.new_tag('journal_article')
        
        title = base.new_tag('titles')
        title_tag = base.new_tag('title')
        title_tag.string = article_data['title'][0]  # Add article title
        title.append(title_tag)
        journal_article.append(title)
        
        contributors = base.new_tag('contributors')
        authors = article_data['contributor.author']
        for i, author_name in enumerate(authors):
            person_name = base.new_tag('person_name')
            person_name['contributor_role'] = 'author'
            if i == 0:
                person_name['sequence'] = 'first'
            else:
                person_name['sequence'] = 'additional'            
            given_name = base.new_tag('given_name')
            surname = base.new_tag('surname')
            namesplit = author_name.split(',')
            if len(namesplit) < 2:
                namesplit = author_name.split(' ')            
            given_name.string = namesplit[1].strip()
            surname.string = namesplit[0].strip()
            person_name.append(given_name)
            person_name.append(surname)
            contributors.append(person_name)      
        journal_article.append(contributors)

        try:
            abstract = base.new_tag('jats:abstract', attrs={'xml:lang': 'en'})
            p_tag = base.new_tag('jats:p')
            p_tag.string = article_data['description.abstract'][0]
            abstract.append(p_tag)
            journal_article.append(abstract)
        except:
            pass

        date_str = article_data['date.issued'][0] 
        date_issued = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        pub_date = base.new_tag('publication_date', attrs={'media_type': 'online'})
        month = base.new_tag('month')
        month.string = str(date_issued.month)  # Add month
        day = base.new_tag('day')
        day.string = str(date_issued.day)  # Add day
        year = base.new_tag('year')
        year.string = str(date_issued.year)  # Add year
        pub_date.append(month)
        pub_date.append(day)
        pub_date.append(year)
        journal_article.append(pub_date)

        try:
            pages = base.new_tag('pages')
            first_page = base.new_tag('first_page')
            first_page.string = article_data['startingpage'][0]  # Add first page
            last_page = base.new_tag('last_page')
            last_page.string = article_data['endingpage'][0]  # Add last page
            pages.append(first_page)
            pages.append(last_page)
            journal_article.append(pages)
        except Exception as e:
            print(filename, title_tag.string)
            print("Error adding pages:", e, "\n\n")

        license = base.new_tag('ai:program', attrs={'name': 'AccessIndicators'})
        license_ref = base.new_tag('ai:license_ref')
        license_ref.string = 'https://creativecommons.org/licenses/by-nc-nd/4.0/'
        license.append(license_ref)
        journal_article.append(license)

        handle_uri = article_data.get('identifier.uri', '')[0]
        indices = [i for i, c in enumerate(handle_uri) if c == '/']
        doi_uri = ''
        if len(indices) >= 3:
            third_index = indices[2]
            doi_uri = handle_uri[third_index:]
        
        doi_url = '10.64152' + doi_uri  # Construct DOI using handle URI
        doi_data = base.new_tag('doi_data')
        doi = base.new_tag('doi')
        doi.string = doi_url
        resource = base.new_tag('resource')
        resource.string = handle_uri  # Use the handle URI as the resource URL
        doi_data.append(doi)
        doi_data.append(resource)
        journal_article.append(doi_data)

        journal.append(journal_article)

    # Write the updated XML to a new file  
    with open(filename, 'w') as file:
        file.write(str(base))


               


if __name__ == "__main__":
    for i in Collection.objects.all():
        generate_crossref_xml('crossref-schema-base.xml', i)


# Running in a Django shell example:
"""
from oaiharvests import xml_doi_generator as gen
from oaiharvests.models import Collection

for collection in Collection.objects.all().order_by('name'):
  if collection.name != 'Language Learning & Technology Media':
    gen.generate_crossref_xml('crossref-schema-base.xml', collection)

OR

from oaiharvests import xml_doi_generator as gen
from oaiharvests.models import Record
record = Record.objects.get(pk=1190)
gen.generate_crossref_doi_xml_submission('crossref-schema-base.xml', record)

OR


"""
