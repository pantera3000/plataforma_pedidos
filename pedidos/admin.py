from django.contrib import admin
from .models import Pedido, DetallePedido
from django.forms import TextInput
from django.db.models import Sum
from .models import Producto, DetallePedido as ModeloDetallePedido  # O simplemente importa models si es necesario
import django.db.models as models  # 👈 Importamos models explícitamente

# Personalizar el admin de DetallePedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ['producto']
    readonly_fields = ['subtotal']

    # Ahora sí puedes usar models.PositiveIntegerField
    formfield_overrides = {
        models.PositiveIntegerField: {'widget': TextInput(attrs={'size': '4'})},
    }

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.subtotal = instance.producto.precio * instance.cantidad
            instance.save()
        form.instance.total = ModeloDetallePedido.objects.filter(pedido=form.instance).aggregate(Sum('subtotal'))['subtotal__sum'] or 0
        form.instance.save()


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'fecha_pedido', 'total')
    search_fields = ('cliente_nombre', 'cliente_dni')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]


admin.site.register(DetallePedido)