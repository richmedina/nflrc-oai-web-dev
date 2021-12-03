from django.db import models
from django.urls import reverse

# TimeStampedModel adds 'created' and 'modified' fields to each inherited class.
from model_utils.models import TimeStampedModel

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
    title = models.CharField(max_length=512, blank=True)
    content = models.TextField(blank=True)
    featured = models.BooleanField(blank=True, default=False)
    featured_rank = models.IntegerField(blank=True, default=0, help_text='If featured is checked ON, higher numbers are displayed before lower numbers')
    published = models.BooleanField(default=True, blank=True, help_text='Checking this ON will make the post visible')   

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_view', args=[str(self.id)])