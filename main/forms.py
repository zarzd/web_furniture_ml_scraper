from django import forms


class UrlForm(forms.Form):
    url = forms.URLField(label='Введите URL', max_length=400)
