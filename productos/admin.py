from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'sku', 'precio')
    search_fields = ('nombre', 'sku')  # 👈 Añadimos esto para habilitar autocompletado
    list_filter = ('precio',)