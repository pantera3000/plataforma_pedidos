from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout

@login_required
def acceso_denegado(request):
    return render(request, 'acceso_denegado.html')






def logout_view(request):
    logout(request)
    return redirect('historial:pedido_historial')  # Redirige al historial de pedidos