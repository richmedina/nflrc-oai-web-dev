# forms.py
from django.forms import ModelForm, ValidationError
from django import forms
from django.contrib import messages

from .models import OAISitePage, OAISitePost


class PageUpdateForm(ModelForm):
    
    class Meta:
        model = OAISitePage
        fields = ['title', 'content', 'published']


class PostUpdateForm(ModelForm):
    
    class Meta:
        model = OAISitePost
        fields = ['title', 'content', 'featured', 'featured_rank']
