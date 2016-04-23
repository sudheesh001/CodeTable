from django import forms
from django_ace import AceWidget

from .constants import l
from .models import Pen

class CodeBoxRun(forms.Form):
	name = forms.CharField()
	text = forms.CharField(widget = AceWidget(wordwrap=False, width="650px", height="500px", showprintmargin=True, theme='twilight'))
	inp = forms.CharField(widget = forms.Textarea(attrs={'id':'input'}),required=False)
	langs = forms.ChoiceField(l, initial='C')