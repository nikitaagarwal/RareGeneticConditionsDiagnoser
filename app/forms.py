from django import forms


class HomeForm(forms.Form):
	post = forms.CharField(widget=forms.TextInput(attrs={'class' : 'input is-primary'}))

