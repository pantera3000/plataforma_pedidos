from django.views.generic import RedirectView, TemplateView
from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from usuarios.views import acceso_denegado  # 👈 Importamos la vista
from usuarios.views import logout_view
from django.urls import path
from . import views
from dashboard.views import dashboard 

urlpatterns = [
     # Página de inicio o redirección
    path('', TemplateView.as_view(template_name='inicio.html'), name='inicio'),
    #path('', RedirectView.as_view(url='/historial/', permanent=False)),
    path('admin/', admin.site.urls),
    path('productos/', include('productos.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('historial/', include('historial.urls')),
    path('dashboard/', include('dashboard.urls')),  # 👈 Agrega esta línea
    path('dashboard/', dashboard, name='dashboard'),  # 👈 Botón funciona si existe esta URL
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de login/logout
    path('accounts/logout/', logout_view, name='logout'),
    path('acceso-denegado/', acceso_denegado, name='acceso_denegado'),  # 👈 Añade esta línea
]
