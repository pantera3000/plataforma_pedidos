from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente_nombre', 'cliente_dni', 'direccion', 'tipo_comprobante', 'notas']