from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.pedido_historial, name='pedido_historial'),
    path('exportar-pedidos/', views.exportar_pedidos, name='exportar_pedidos'),
    
]