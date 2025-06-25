from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from .forms import PedidoForm
from .models import Pedido
from django.http import JsonResponse
from productos.models import Producto  # 👈 Importa el modelo Producto
from django.db.models import Q  # 👈 Importa Q para hacer consultas complejas
from django.shortcuts import render, redirect, get_object_or_404  # 👈 Agrega get_object_or_404 aquí
from django.shortcuts import render, redirect
from .forms import PedidoForm
from .models import Pedido, DetallePedido
from productos.models import Producto
import json
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


def es_admin(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser

def es_vendedor(user):
    return user.groups.filter(name='Vendedor').exists() or False

def es_lector(user):
    return user.groups.filter(name='Lector').exists() or False



@login_required
#@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
#@user_passes_test(es_admin, login_url='/acceso-denegado/')
#@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
@user_passes_test(lambda u: not es_lector(u), login_url='/acceso-denegado/')
def pedido_crear(request):
    if request.method == "POST":
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save()  # Guarda el pedido

            # Recuperar productos seleccionados desde el campo oculto
            productos_json = request.POST.get('productos_seleccionados')
            if productos_json:
                try:
                    productos = json.loads(productos_json)
                    for item in productos:
                        producto = Producto.objects.get(id=item['id'])
                        cantidad = int(item['cantidad'])
                        subtotal = float(item['precio']) * cantidad

                        DetallePedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=cantidad,
                            subtotal=subtotal
                        )
                    pedido.total = sum(detalle.subtotal for detalle in pedido.detallepedido_set.all())
                    pedido.save()
                except Exception as e:
                    print("Error al guardar los productos:", e)

            return redirect('historial:pedido_historial')
    else:
        form = PedidoForm()

    return render(request, 'pedidos/pedido_crear.html', {'form': form})



@login_required
def pedido_detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    detalles = pedido.detallepedido_set.all()  # Obtener todos los productos del pedido
    return render(request, 'pedidos/pedido_detalle.html', {'pedido': pedido, 'detalles': detalles})



@login_required
def buscar_producto(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(
            Q(nombre__icontains=query) | Q(sku__icontains=query)
        )[:50]
        results = [{'id': p.id, 'nombre': p.nombre, 'sku': p.sku, 'precio': float(p.precio)} for p in productos]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)




@login_required
#@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
#@user_passes_test(lambda u: not (es_vendedor(u) or es_lector(u)), login_url='/acceso-denegado/')
@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
@user_passes_test(lambda u: not es_lector(u), login_url='/acceso-denegado/')
def pedido_editar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    pedido_id = pedido.id  # Guardamos el ID antes de eliminar
    
    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            pedido = form.save()

            # Eliminar detalles anteriores (opcional, puedes dejarlo si prefieres mantener historial)
            DetallePedido.objects.filter(pedido=pedido).delete()

            # Recuperar productos seleccionados desde el campo oculto
            productos_json = request.POST.get('productos_seleccionados')
            if productos_json:
                try:
                    productos = json.loads(productos_json)
                    for item in productos:
                        producto = Producto.objects.get(id=item['id'])
                        cantidad = int(item['cantidad'])
                        subtotal = float(item['precio']) * cantidad

                        DetallePedido.objects.create(
                            pedido=pedido,
                            producto=producto,
                            cantidad=cantidad,
                            subtotal=subtotal
                        )
                    pedido.total = sum(detalle.subtotal for detalle in pedido.detallepedido_set.all())
                    pedido.save()
                except Exception as e:
                    print("Error al guardar los productos:", e)

            return redirect('pedidos:pedido_detalle', pk=pedido.pk)
    else:
        form = PedidoForm(instance=pedido)
        detalles = pedido.detallepedido_set.all()
        productos_seleccionados = [
            {
                'id': d.producto.id,
                'nombre': d.producto.nombre,
                'sku': d.producto.sku,
                'precio': float(d.producto.precio),
                'cantidad': d.cantidad,
                'subtotal': float(d.subtotal)
            }
            for d in detalles
        ]

    return render(request, 'pedidos/pedido_crear.html', {
        'form': form,
        'productos_seleccionados': json.dumps(productos_seleccionados),  # Convertido a JSON
        'es_edicion': True,
        'pedido': pedido
    })





# Vista eliminar pedido (si existe) → denegada a vendedores
@user_passes_test(lambda u: not es_vendedor(u), login_url='/acceso-denegado/')
@user_passes_test(lambda u: not es_lector(u), login_url='/acceso-denegado/')
def pedido_eliminar(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        try:
            pedido.delete()
            messages.success(request, f"Pedido #{pedido.id} eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"No se pudo eliminar el pedido. Error: {str(e)}")
        return redirect('historial:pedido_historial')
    return redirect('pedidos:pedido_detalle', pk=pk)


def es_vendedor(user):
    return user.groups.filter(name='Vendedor').exists()


def acceso_denegado(request):
    return render(request, 'acceso_denegado.html')








