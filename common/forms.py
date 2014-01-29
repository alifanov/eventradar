# coding: utf-8
__author__ = 'vampire'
from django import forms
from common.models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'text']