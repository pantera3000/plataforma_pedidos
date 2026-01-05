from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.pedido_historial, name='pedido_historial'),
    path('exportar-pedidos/', views.exportar_pedidos, name='exportar_pedidos'),


    path('exportar/excel/', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('exportar/pdf/', views.exportar_pedidos_pdf, name='exportar_pedidos_pdf'),

]