from django.shortcuts import render
from .forms import *

# Create your views here.

def home(request):
    return render(request, 'index.html')


def registrar(request):
    if request.method == 'POST':
        usuario = request.POST['usuario']
        email = request.POST['email']
        senha = request.POST['senha']
        object = Usuario(nome=usuario, email=email, senha=senha)
        try:
            object.save()
            return render(request, 'sucesso.html')
        except:
            return render(request, 'erro.html')
    return render(request, 'registrar.html')


def login(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        senha = request.POST['senha']
        try:
            object = Usuario.objects.get(nome=nome, senha=senha)
            return render(request, 'sucesso.html')
        except:
            return render(request, 'erro.html')
    return render(request, 'login.html')

