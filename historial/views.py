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


def get_filtered_pedidos(request):
    """
    Helper para aplicar filtros a los pedidos desde la request.
    Retorna el QuerySet filtrado y un diccionario con los filtros aplicados.
    """
    queryset = Pedido.objects.all().order_by('-fecha_pedido')

    # Filtros
    id_pedido = request.GET.get('id_pedido')
    cliente = request.GET.get('cliente')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    fecha_dia = request.GET.get('fecha_dia')

    if id_pedido and id_pedido != "None":
        try:
            pedido_id = int(id_pedido)
            queryset = queryset.filter(id=pedido_id)
        except ValueError:
            pass

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
            pass

    if fecha_fin and fecha_fin != "None":
        try:
            fecha_fin_parsed = parse_datetime(fecha_fin)
            if fecha_fin_parsed:
                queryset = queryset.filter(fecha_pedido__lte=fecha_fin_parsed)
        except ValueError:
            pass

    if fecha_dia and fecha_dia != "None":
        queryset = queryset.filter(fecha_pedido__date=fecha_dia)

    return queryset, {
        'id_pedido': id_pedido,
        'cliente': cliente,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'fecha_dia': fecha_dia
    }

@login_required
def pedido_historial(request):
    queryset, filtros = get_filtered_pedidos(request)

    # Paginación
    paginator = Paginator(queryset, 10)  # 10 pedidos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    context.update(filtros) # Agregar los filtros al contexto

    return render(request, 'historial/pedido_historial.html', context)


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
    pedidos, _ = get_filtered_pedidos(request) # Usar el helper
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
    pedidos, _ = get_filtered_pedidos(request) # Usar el helper
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


@login_required
def exportar_pedidos_detalle_excel(request):
    # Crear libro de trabajo
    wb = Workbook()
    ws = wb.active
    ws.title = "Detalle de Productos"

    # Encabezados
    headers = [
        'ID Pedido', 'Fecha', 'Cliente', 'DNI/RUC', 
        'Producto', 'SKU', 'Cantidad', 'Precio Unit.', 'Subtotal', 
        'Comprobante', 'Notas'
    ]
    ws.append(headers)

    # Estilos
    from openpyxl.styles import Font, Alignment, PatternFill
    
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid") # Azul corporativo
    
    # Estilos para filas alternas (Gris más visible)
    fill_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid") # Blanco
    fill_even = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid") # Gris más oscuro (Excel standard gray)

    # Aplicar estilo al encabezado
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')

    # Datos
    pedidos, _ = get_filtered_pedidos(request) # Usar el helper compartido
    
    # Optimizar consulta para traer productos relacionados
    pedidos = pedidos.prefetch_related('detallepedido_set__producto')

    # Iterar sobre pedidos
    for i, pedido in enumerate(pedidos):
        # Determinar color de fondo para ESTE pedido (y todos sus productos)
        row_fill = fill_even if i % 2 == 0 else fill_odd
        
        detalles = pedido.detallepedido_set.all()
        
        if not detalles:
            ws.append([
                pedido.id,
                pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M'),
                pedido.cliente_nombre,
                pedido.cliente_dni or "",
                "(Sin productos)", "", 0, 0, 0,
                pedido.get_tipo_comprobante_display(),
                pedido.notas or ""
            ])
            # Aplicar color a la fila recien creada
            for cell in ws[ws.max_row]:
                cell.fill = row_fill
        else:
            for detalle in detalles:
                ws.append([
                    pedido.id,
                    pedido.fecha_pedido.strftime('%d/%m/%Y %H:%M'),
                    pedido.cliente_nombre,
                    pedido.cliente_dni or "",
                    detalle.producto.nombre,
                    detalle.producto.sku,
                    detalle.cantidad,
                    float(detalle.producto.precio),
                    float(detalle.subtotal),
                    pedido.get_tipo_comprobante_display(),
                    pedido.notas or ""
                ])
                # Aplicar color a la fila recien creada
                for cell in ws[ws.max_row]:
                    cell.fill = row_fill

    # Ajustar anchos
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    response['Content-Disposition'] = f'attachment; filename="detalle_pedidos_{timestamp}.xlsx"'
    wb.save(response)
    return response


from weasyprint import HTML
import tempfile

@login_required
def exportar_pedidos_pdf(request):
    pedidos, _ = get_filtered_pedidos(request) # Usar el helper

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



