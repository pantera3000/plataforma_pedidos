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











from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime

@login_required
def exportar_pedidos_excel(request):
    # Crear libro de trabajo
    wb = Workbook()
    ws = wb.active
    ws.title = "Historial de Pedidos"

    # Encabezados
    headers = ['ID', 'Cliente', 'DNI', 'Fecha Pedido', 'Dirección', 'Tipo Comprobante', 'Total', 'Notas']
    ws.append(headers)

    # Estilo de encabezado (opcional)
    from openpyxl.styles import Font
    for cell in ws[1]:
        cell.font = Font(bold=True)

    # Datos
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    for pedido in pedidos:
        ws.append([
            pedido.id,
            pedido.cliente_nombre,
            pedido.cliente_dni or "",
            pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M'),
            pedido.direccion or "",
            pedido.get_tipo_comprobante_display(),
            float(pedido.total),
            pedido.notas or ""
        ])

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column].width = adjusted_width

    # Respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="pedidos_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx"'
    wb.save(response)
    return response


from weasyprint import HTML
import tempfile

@login_required
def exportar_pedidos_pdf(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')

    # Crear HTML para el PDF
    html_string = render(request, 'historial/pedidos_pdf.html', {
        'pedidos': pedidos,
        'titulo': 'Historial de Pedidos',
        'fecha_exportacion': timezone.now().strftime('%d/%m/%Y %H:%M')
    }).content.decode('utf-8')

    # Generar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historial_pedidos.pdf"'

    HTML(string=html_string).write_pdf(response)

    return response



