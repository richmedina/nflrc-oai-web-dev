# forms.py
from django.forms import ModelForm, ValidationError
from django import forms
from django.contrib import messages

from .models import OAISitePage


class PageUpdateForm(ModelForm):
    
    class Meta:
        model = OAISitePage
        fields = ['title', 'content', 'published']
