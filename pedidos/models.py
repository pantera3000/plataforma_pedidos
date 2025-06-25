from django.db import models
from productos.models import Producto

class Pedido(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ('BOLETA', 'Boleta'),
        ('FACTURA', 'Factura'),
        ('NOTA_VENTA', 'Nota de Venta'),
        ('TICKET', 'Ticket'),
        ('COTIZACION', 'Cotización'),
        ('OTRO', 'Otro')
    ]

    cliente_nombre = models.CharField(max_length=100)
    cliente_dni = models.CharField(max_length=20)
    cliente_empresa = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.TextField()
    tipo_comprobante = models.CharField(
        max_length=50,
        choices=TIPO_COMPROBANTE_CHOICES,
        verbose_name="Tipo de Comprobante"
    )
    notas = models.TextField(blank=True, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)



    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nombre}"

    def calcular_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detallepedido_set.all())
        self.save(update_fields=['total'])

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)
        self.pedido.calcular_total()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"