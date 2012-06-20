from django import forms
 
class UploadFileForm(forms.Form):
    file = forms.FileField(
        label = 'Select a file',
        help_text = 'csv files, please'
    )
