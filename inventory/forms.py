from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'diameter', 'length', 'quantity', 'import_date']
        
class ImageUploadForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Select Product")
    image = forms.ImageField(label="Upload Warehouse Image")