from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse  # 👈 IMPORTAR reverse
from django.http import HttpResponseRedirect
from .models import Producto
from .forms import ProductoForm
from django.contrib import messages  # 👈 IMPORTAR
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import csv
from .models import Producto
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
import csv
import openpyxl
from django.shortcuts import render, redirect






def es_admin(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser

def es_vendedor(user):
    return user.groups.filter(name='Vendedor').exists()

def es_lector(user):
    return user.groups.filter(name='Lector').exists()


@login_required
@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
@user_passes_test(lambda u: not es_lector(u), login_url='/acceso-denegado/')
def producto_list(request):
    query = request.GET.get('q', '')
    orden = request.GET.get('ordenar_por', '')

    productos = Producto.objects.all()

    # Filtrar por nombre si hay búsqueda
    if query:
        productos = productos.filter(nombre__icontains=query)

    # Aplicar ordenamiento
    if orden == 'nombre_asc':
        productos = productos.order_by('nombre')
    elif orden == 'nombre_desc':
        productos = productos.order_by('-nombre')
    elif orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')

    return render(request, 'productos/producto_list.html', {
        'productos': productos,
        'query': query,
        'orden': orden
    })



@login_required
@user_passes_test(lambda u: es_admin(u), login_url='/acceso-denegado/')
#@user_passes_test(es_admin, login_url='/acceso-denegado/')
def producto_crear(request):
    if request.method == "POST":
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos:producto_list')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {'form': form})



@login_required
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos:producto_list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {'form': form})



@login_required
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, f"Producto '{producto.nombre}' eliminado con éxito.")
        except Exception as e:
            messages.error(request, f"No se pudo eliminar el producto '{producto.nombre}'. Error: {str(e)}")
        return HttpResponseRedirect(reverse('productos:producto_list'))
    return HttpResponseRedirect(reverse('productos:producto_list'))



def exportar_productos(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="productos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nombre', 'SKU', 'Precio', 'Descripción'])

    productos = Producto.objects.all()
    for producto in productos:
        writer.writerow([
            producto.nombre,
            producto.sku,
            producto.precio,
            producto.descripcion or ''
        ])

    return response















@login_required
def carga_masiva_productos(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        try:
            decoded_file = None
            reader = None

            # Procesar archivo CSV
            if archivo.name.endswith('.csv'):
                raw_data = archivo.read()
                
                # ✅ Mejorar la detección de codificación
                for encoding in ['utf-8-sig', 'latin1', 'cp1252']:
                    try:
                        decoded_file = raw_data.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not decoded_file:
                    raise Exception("No se pudo leer el archivo con ninguna codificación")
                
                reader = csv.DictReader(decoded_file.splitlines())

            # Procesar archivo Excel (.xlsx)
            elif archivo.name.endswith('.xlsx'):
                workbook = openpyxl.load_workbook(archivo)
                sheet = workbook.active
                reader = []
                for row in sheet.iter_rows(min_row=2, values_only=True):  # Saltar encabezado
                    reader.append({
                        'nombre': row[0],
                        'sku': row[1],
                        'precio': row[2],
                        'descripcion': row[3]
                    })
            else:
                return render(request, 'productos/carga_masiva.html', {
                    'error': 'Formato no soportado. Usa .csv o .xlsx'
                })

            nuevos = []
            errores = []

            for row in reader:
                try:
                    # Validar que los campos obligatorios no estén vacíos
                    if not all(row.values()):
                        raise ValueError(f"Campos incompletos en fila {len(nuevos) + 1}")

                    # Validar si el SKU ya existe
                    if Producto.objects.filter(sku=row['sku']).exists():
                        raise ValueError(f"SKU '{row['sku']}' duplicado")

                    # Crear producto
                    producto = Producto.objects.create(
                        nombre=row['nombre'],
                        sku=row['sku'],
                        precio=float(row['precio']),
                        descripcion=row['descripcion']
                    )
                    nuevos.append(producto)

                except Exception as e:
                    errores.append({
                        'fila': len(nuevos) + 1,
                        'error': str(e)
                    })

            return render(request, 'productos/carga_masiva_resultado.html', {
                'nuevos': nuevos,
                'errores': errores
            })

        except Exception as e:
            return render(request, 'productos/carga_masiva_resultado.html', {
                'error': f"Error al procesar el archivo: {str(e)}"
            })

    return render(request, 'productos/carga_masiva.html')



def descargar_ejemplo(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ejemplo_carga.csv"'
    writer = csv.writer(response)
    writer.writerow(['nombre', 'sku', 'precio', 'descripcion'])
    writer.writerow(['Producto Ejemplo', 'SKU001', '99.99', 'Este es un ejemplo de descripción.'])
    return response



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Producto
import csv
import openpyxl

@login_required
def procesar_carga_masiva(request):
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        archivo = request.FILES['archivo_csv']
        try:
            decoded_file = archivo.read().decode('utf-8-sig')
            reader = csv.DictReader(decoded_file.splitlines())
            nuevos = []
            errores = []

            for row in reader:
                try:
                    Producto.objects.create(
                        nombre=row['nombre'],
                        sku=row['sku'],
                        precio=row['precio'],
                        categoria=row['categoria'],
                        stock=int(row['stock'])
                    )
                    nuevos.append(row)
                except Exception as e:
                    errores.append({
                        'fila': row,
                        'error': str(e)
                    })

            return render(request, 'productos/carga_masiva_resultado.html', {
                'nuevos': nuevos,
                'errores': errores
            })

        except Exception as e:
            return render(request, 'productos/carga_masiva_resultado.html', {
                'error': f"Error al leer el archivo: {str(e)}"
            })

    return redirect('productos:carga_masiva_productos')





from django.shortcuts import render
from .models import Producto
import csv
from django.contrib.auth.decorators import login_required

@login_required
def producto_lista(request):
    productos = Producto.objects.all()
    return render(request, 'productos/producto_lista.html', {'productos': productos})