from django.db import models
from datetime import date

def subirImagen(instance, filename) -> str:
    today = date.today().strftime('%Y/%m/%d')
    return f'img_predict/{today}/' + filename

# Create your models here.
class Predicciones(models.Model):
    imagen = models.ImageField(upload_to = subirImagen)
    imagen_preprocesada = models.ImageField(upload_to = subirImagen, null=True, blank=True)
    prediccion = models.IntegerField(null=True, blank=True)
    confianza = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Predicciones'
    
    def __str__(self):
        return f'Prediccion para la imagen { self.imagen }, el { self.created }'