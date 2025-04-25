from django.shortcuts import render
from .forms import PrediccionForm
from django.views.generic import TemplateView
from .models import Predicciones
from PIL import Image
import numpy as np
import requests
import io
from django.core.files.base import ContentFile
from django.conf import settings

# URL del servicio de predicción del modelo (dentro de la red Docker)
MODEL_API_URL = 'http://model_app:5000/predict'

class PrediccionView(TemplateView):
    template_name = 'predicciones/prediccion.html'
    formulario = PrediccionForm

    def get(self, request, *args, **kwargs):
        context = {'formulario': self.formulario}
        prediccion_param = request.GET.get('prediccion')
        if prediccion_param:
            context['mensaje_url'] = f"Mensaje desde la URL: {prediccion_param}"
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = PrediccionForm(request.POST, request.FILES)

        if form.is_valid():
            image_file = form.cleaned_data['imagen']
            prediccion = Predicciones(imagen=image_file)
            prediccion.save()

            try:
                img = Image.open(prediccion.imagen.path).convert('L')
                img = img.resize((28, 28))
                img_array = np.array(img) / 255.0
                img_array_reshaped = img_array.reshape(28, 28)

                # Convertir la imagen a bytes para enviarla al servicio del modelo
                buffer = io.BytesIO()
                image_pil = Image.fromarray((img_array_reshaped * 255).astype(np.uint8))
                image_pil.save(buffer, format='PNG')
                image_bytes = buffer.getvalue()

                # Enviar la imagen al servicio del modelo
                files = {'image': ('image.png', image_bytes, 'image/png')}
                response = requests.post(MODEL_API_URL, files=files)
                response.raise_for_status()  # Lanza una excepción para errores HTTP
                prediction_data = response.json()
                predicted_class = prediction_data.get('predicted_class')
                confidence = prediction_data.get('confidence')

                if predicted_class is not None and confidence is not None:
                    prediccion.prediccion = predicted_class
                    prediccion.confianza = confidence
                    prediccion.save()

                    context = {
                        'formulario': self.formulario,
                        'prediccion': predicted_class,
                        'confianza': confidence,
                        'imagen_url': prediccion.imagen.url,
                    }
                    mensaje_url = request.GET.get('prediccion')
                    if mensaje_url:
                        context['mensaje_url'] = f"Mensaje desde la URL: {mensaje_url}"
                    return render(request, self.template_name, context)
                else:
                    error_message = "Error al obtener la predicción del servicio del modelo."
                    return render(request, self.template_name, {'formulario': self.formulario, 'error': error_message})

            except requests.exceptions.RequestException as e:
                prediccion.delete()
                error_message = f"Error al comunicarse con el servicio del modelo: {e}"
                return render(request, self.template_name, {'formulario': self.formulario, 'error': error_message})
            except Exception as e:
                prediccion.delete()
                error_message = f"Error al preprocesar la imagen o recibir la respuesta: {e}"
                return render(request, self.template_name, {'formulario': self.formulario, 'error': error_message})

        context = {'formulario': form}
        mensaje_url = request.GET.get('prediccion')
        if mensaje_url:
            context['mensaje_url'] = f"Mensaje desde la URL: {mensaje_url}"
        return render(request, self.template_name, context)