from django import forms
from captcha.fields import CaptchaField

class PostForm(forms.Form):
    boardsubject = forms.CharField(max_length=100,initial='')
    boardname = forms.CharField(max_length=20,initial='')
    boardgender = forms.BooleanField()
    boardmail = forms.EmailField(max_length=100,initial='',required=False)
    boardweb = forms.URLField(max_length=100,initial='',required=False)
    boardcontent = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()

#網路相簿
class PostForm_album(forms.Form):
    username = forms.CharField(max_length=20,initial='')
    pd = forms.CharField(max_length=20,initial='')
    captcha = CaptchaField()
