from django.shortcuts import render

def acceso_denegado(request):
    return render(request, 'acceso_denegado.html')