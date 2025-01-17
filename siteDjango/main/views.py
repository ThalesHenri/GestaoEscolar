from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from .forms import *

# Create your views here.

def home(request):
    return render(request, 'index.html')


def registrar(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not usuario or not email or not senha:
            return render(request, 'erro.html', {'mensagem': 'Todos os campos são obrigatórios!'})

        try:
            User.objects.create_user(username=usuario, email=email, password=senha)
            return render(request, 'sucesso.html')
        except Exception as e:
            return render(request, 'erro.html', {'mensagem': str(e)})

    return render(request, 'registrar.html')

def login(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        senha = request.POST.get('senha')

        # Tenta autenticar o usuário com o sistema padrão do Django
        usuario = authenticate(request, username=nome, password=senha)
        if usuario is not None:
            # Realiza o login do usuário e redireciona para o dashboard
            auth_login(request, usuario)
            return redirect('adminDashboard')  # Substitua pelo nome da URL do dashboard
        else:
            # Renderiza a página de erro em caso de falha na autenticação
            return render(request, 'erro.html')
    
    # Renderiza a página de login para requisições GET
    return render(request, 'login.html')



def adminDashboard(request):
    usuario = request.user
    context = {
        'usuario': usuario
    }
    print(f"aqui está o {usuario}")
    return render(request, 'adminDashboard.html', context=context)