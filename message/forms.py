from django import forms
from .models import UserInfo
from django.contrib.auth.models import User
from .models import Document

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta():
        model = User
        fields = ('username','password','email')


class UploadFileFormL(forms.Form):
    file = forms.FileField()


class UploadFileFormR(forms.Form):
    file = forms.FileField()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )