# forms.py
from django.forms import ModelForm, ValidationError
from django import forms
from django.contrib import messages

from .models import OAISitePage, OAISitePost


class PageUpdateForm(ModelForm):
    
    class Meta:
        model = OAISitePage
        fields = ['title', 'content', 'published', ]


class PostCreateForm(ModelForm):
    
    class Meta:
        model = OAISitePost
        fields = ['title', 'content', 'featured', 'featured_rank', 'post_tag']


class PostUpdateForm(ModelForm):
    
    class Meta:
        model = OAISitePost
        fields = ['title', 'content', 'featured', 'featured_rank', 'post_tag']



# error_messages = {
#             NON_FIELD_ERRORS: {
#                 'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
#             }
#         }