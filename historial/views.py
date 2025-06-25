from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pedidos.models import Pedido
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse
import csv
from pedidos.models import Pedido, DetallePedido
from pedidos.models import DetallePedido


@login_required
def pedido_historial(request):
    queryset = Pedido.objects.all().order_by('-fecha_pedido')

    # Filtros
    id_pedido = request.GET.get('id_pedido')
    cliente = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    fecha_dia = request.GET.get('fecha_dia')  # 👈 Nuevo filtro: una sola fecha

    if id_pedido and id_pedido != "None":
        try:
            pedido_id = int(id_pedido)
            queryset = queryset.filter(id=pedido_id)
        except ValueError:
            pass  # Si el ID no es un número válido, ignoramos el filtro

    if cliente:
        queryset = queryset.filter(
            Q(cliente_nombre__icontains=cliente) |
            Q(cliente_dni__icontains=cliente)
        )

    if fecha_inicio and fecha_inicio != "None":
        try:
            fecha_inicio_parsed = parse_datetime(fecha_inicio)
            if fecha_inicio_parsed:
                queryset = queryset.filter(fecha_pedido__gte=fecha_inicio_parsed)
        except ValueError:
            pass  # Si la fecha no es válida, ignoramos el filtro

    if fecha_fin and fecha_fin != "None":
        try:
            fecha_fin_parsed = parse_datetime(fecha_fin)
            if fecha_fin_parsed:
                queryset = queryset.filter(fecha_pedido__lte=fecha_fin_parsed)
        except ValueError:
            pass

    if fecha_dia and fecha_dia != "None":
        queryset = queryset.filter(fecha_pedido__date=fecha_dia)




    # Paginación
    paginator = Paginator(queryset, 10)  # 10 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'historial/pedido_historial.html', {
        'page_obj': page_obj,
        'id_pedido': id_pedido,
        'cliente': cliente,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_dia': fecha_dia  # 👈 Pasamos el valor a la plantilla
    })





@login_required
def exportar_pedidos(request):
    # Preparar respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'

    writer = csv.writer(response)
    # Encabezados
    writer.writerow([
        'ID', 'Cliente', 'DNI', 'Fecha Pedido', 'Dirección',
        'Tipo Comprobante', 'Total', 'Notas'
    ])

    # Datos
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    for pedido in pedidos:
        writer.writerow([
            pedido.id,
            pedido.cliente_nombre,
            pedido.cliente_dni,
            pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M'),
            pedido.direccion,
            pedido.tipo_comprobante,
            pedido.total,
            pedido.notas or ''
        ])

    return response



