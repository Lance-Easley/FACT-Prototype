from django.urls import path
from .views import TestTemplateView

urlpatterns = [
    path('', TestTemplateView.as_view(), name='test'),
]