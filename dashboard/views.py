from django.shortcuts import render
from pedidos.models import Pedido, DetallePedido
from productos.models import Producto
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone
from collections import defaultdict
from django.contrib.auth.decorators import login_required  # 👈 Añadimos seguridad si es necesario

@login_required
def dashboard(request):
    hoy = timezone.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)

    # Resumen rápido de datos
    total_pedidos = Pedido.objects.count()
    ingresos_totales = Pedido.objects.aggregate(Sum('total'))['total__sum'] or 0.0
    ventas_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).count()
    ingresos_hoy = Pedido.objects.filter(fecha_pedido__date=hoy).aggregate(Sum('total'))['total__sum'] or 0.0
    ventas_semana = Pedido.objects.filter(fecha_pedido__date__gte=hace_7_dias).count()
    ingresos_semana = Pedido.objects.filter(fecha_pedido__date__gte=hace_7_dias).aggregate(Sum('total'))['total__sum'] or 0.0

    # Productos más vendidos (último mes)
    producto_vendido = defaultdict(lambda: {'nombre': '', 'cantidad': 0, 'total': 0})
    detalles = DetallePedido.objects.select_related('producto').filter(
        pedido__fecha_pedido__date__gte=hace_30_dias
    )

    for detalle in detalles:
        p = detalle.producto
        producto_vendido[p.id]['nombre'] = p.nombre
        producto_vendido[p.id]['cantidad'] += detalle.cantidad
        producto_vendido[p.id]['total'] += float(detalle.subtotal)

    productos_mas_vendidos = sorted(
        producto_vendido.values(),
        key=lambda x: x['cantidad'],
        reverse=True
    )[:10]

    # Datos para gráfica de ingresos diarios (últimos 7 días)
    fechas = [hoy - timedelta(days=i) for i in range(6, -1, -1)]  # Desde hace 6 días hasta hoy
    datos_grafica = []
    for fecha in fechas:
        ingreso = Pedido.objects.filter(fecha_pedido__date=fecha).aggregate(Sum('total'))['total__sum'] or 0.0
        datos_grafica.append({
            'fecha': fecha.strftime('%a'),
            'ingreso': round(ingreso, 2)
        })

    return render(request, 'dashboard.html', {
        'total_pedidos': total_pedidos,
        'ingresos_totales': round(ingresos_totales, 2),
        'ventas_hoy': ventas_hoy,
        'ingresos_hoy': round(ingresos_hoy, 2),
        'ventas_semana': ventas_semana,
        'ingresos_semana': round(ingresos_semana, 2),
        'productos_mas_vendidos': productos_mas_vendidos,
        'datos_grafica': datos_grafica,
        'hoy': hoy
    })