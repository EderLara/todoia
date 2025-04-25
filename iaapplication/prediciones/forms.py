from django import forms
from .models import Predicciones

class PrediccionForm(forms.ModelForm):
    """ Clase para el formulario de subida de imagen """

    class Meta:
        model = Predicciones
        fields = ['imagen']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file'})
        }
