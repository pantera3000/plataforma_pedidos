from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('nuevo/', views.producto_crear, name='producto_crear'),
    path('<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),  # 👈 Nueva ruta
    path('exportar-productos/', views.exportar_productos, name='exportar_productos'),
    path('lista/', views.producto_lista, name='producto_lista'),
    path('carga-masiva/', views.carga_masiva_productos, name='carga_masiva_productos'), 
    path('procesar-carga/', views.procesar_carga_masiva, name='procesar_carga_masiva'),
    path('ejemplo-carga.csv', views.descargar_ejemplo, name='descargar_ejemplo'),
]


