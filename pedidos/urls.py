from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('crear/', views.pedido_crear, name='pedido_crear'),
    path('<int:pk>/', views.pedido_detalle, name='pedido_detalle'),
    path('<int:pk>/editar/', views.pedido_editar, name='pedido_editar'),
    path('<int:pk>/eliminar/', views.pedido_eliminar, name='pedido_eliminar'),  # 👈 Corrige el typo: debe ser 'pedido_eliminar' (no 'pedido_elimnar')
    path('buscar-producto/', views.buscar_producto, name='buscar_producto'),  # 👈 Nueva ruta
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),
    path('<int:pk>/pdf/', views.generar_pdf_pedido, name='generar_pdf_pedido'),  # 👈 Nueva ruta
]