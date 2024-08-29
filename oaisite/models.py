from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

# TimeStampedModel adds 'created' and 'modified' fields to each inherited class.
from model_utils.models import TimeStampedModel

from oaiharvests.models import Collection

class OAISitePage(TimeStampedModel):
    title = models.CharField(max_length=512, blank=True)
    content = models.TextField(blank=True)
    published = models.BooleanField(default=True, blank=True, help_text='Checking this ON will make the page visible')
    slug = models.SlugField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page_view', args=[str(self.id)])


class OAISitePost(TimeStampedModel):
    title = models.CharField(max_length=512, blank=False)
    content = models.TextField(blank=True)
    featured = models.BooleanField(blank=True, default=False)
    featured_rank = models.IntegerField(blank=True, default=0, help_text='If featured is checked ON, higher numbers are displayed before lower numbers')
    published = models.BooleanField(default=True, blank=True, help_text='Checking this ON will make the post visible')

    BLANK  = ''
    CFPPLS = 'Call for Proposals'
    CFPPRS = 'Call for Papers'
    CFVOLS = 'Call for Volunteers'
    AWARDS = 'Awards'
    
    POST_TAGS = [
        (BLANK, ''),
        (CFPPLS, 'Call for Proposals'),
        (CFPPRS, 'Call for Papers'),
        (CFVOLS, 'Call for Volunteers'),
        (AWARDS, 'Awards'),
    ]
    post_tag = models.CharField(blank=True, max_length=48, choices=POST_TAGS, default=BLANK,)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_view', args=[str(self.id)])


class OAISiteSupplementaryCollection(TimeStampedModel):
    title = models.CharField(max_length=512, blank=False, help_text='Enter a display title for this collection.')
    collection_id = models.ForeignKey(Collection, on_delete=models.CASCADE)
    collection_type = models.CharField(max_length=512, blank=False, help_text='Enter a short string to indicate the type of items in this collection (E.g., podcasts, media, reports)')
    slug = models.SlugField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('media_collection', args=[self.slug])