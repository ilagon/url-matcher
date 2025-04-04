from django import forms

class CSVUploadForm(forms.Form):
    """Form for uploading CSV files for URL matching."""
    
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='Must be a valid CSV file containing Live and Staging URLs',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    
    similarity_threshold = forms.FloatField(
        label='Similarity Threshold',
        help_text='Threshold for partial matching (0.0 to 1.0)',
        initial=0.7,
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05'})
    )
