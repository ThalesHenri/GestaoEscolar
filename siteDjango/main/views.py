from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Turma, Aluno, Mensalidade
from .forms import TurmaForm, AlunoForm
from .forms import *
from django.contrib.auth.decorators import login_required

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
            User.objects.create_user(
                username=usuario, email=email, password=senha)
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
            # Substitua pelo nome da URL do dashboard
            return redirect('adminDashboard')
        else:
            # Renderiza a página de erro em caso de falha na autenticação
            return render(request, 'erro.html')

    # Renderiza a página de login para requisições GET
    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required
def adminDashboard(request):
    usuario = request.user
    context = {
        'usuario': usuario
    }
    print(f"aqui está o {usuario}")
    return render(request, 'adminDashboard.html', context=context)


def addTurma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turma adicionada com sucesso!')
            return redirect('turmasDashboard')
    else:
        form = TurmaForm()

    return render(request, 'addTurma.html', {'form': form})


def turmasDashboard(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('turmasDashboard')  # Atualiza a página após salvar
    else:
        form = TurmaForm()

    turmas = Turma.objects.all()
    return render(request, 'turmasDashboard.html', {'turmas': turmas, 'form': form})

def turmaDetalhes(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            # Cria o aluno mas não salva no banco ainda
            aluno = form.save(commit=False)
            # Associa o aluno à turma atual
            aluno.turma = turma
            aluno.save()  # Salva o aluno no banco de dados
            return redirect('turmaDetalhes', turma_id=turma.id)  # Redireciona para a mesma página
    else:
        # Inicializa o formulário vazio para a adição de novos alunos
        form = AlunoForm()

    # Obtém os alunos da turma utilizando o `related_name='alunos'`
    alunos = turma.alunos.all()
    
    # Renderiza a página com os dados da turma, alunos e formulário
    return render(request, 'turmaDetalhes.html', {'turma': turma, 'alunos': alunos, 'form': form})


def addAluno(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            aluno = form.save(commit=False)
            aluno.turma = turma
            
            # Verificação do dia de pagamento antes de salvar
            if aluno.dia_pagamento is None:
                form.add_error('dia_pagamento', 'Data para Pagamento:')
            else:
                aluno.save()
                
                # Criação das mensalidades com base no dia de pagamento
                for mes in range(1, 13):  # Assumindo a criação de mensalidades para todos os meses do ano
                    data_vencimento = timezone.now().replace(month=mes, day=aluno.dia_pagamento, year=timezone.now().year).date()
                    Mensalidade.objects.create(
                        aluno=aluno,
                        mes=mes,
                        valor=turma.valorMensalidade,  # Valor da mensalidade registrado na turma
                        data_vencimento=data_vencimento,  # Data de vencimento com o ano vigente
                        pago=False
                    )
                messages.success(request, 'Aluno adicionado com sucesso!')
                return redirect('addAluno', turma_id=turma.id)
    else:
        form = AlunoForm()

    return render(request, 'addAluno.html', {'form': form, 'turma': turma})




def alunoDetalhes(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    mensalidades = aluno.mensalidades.order_by("mes").all()

    MESES = {
        1: "1 - Janeiro",
        2: "2 - Fevereiro",
        3: "3 - Março",
        4: "4 - Abril",
        5: "5 - Maio",
        6: "6 - Junho",
        7: "7 - Julho",
        8: "8 - Agosto",
        9: "9 - Setembro",
        10: "10 - Outubro",
        11: "11 - Novembro",
        12: "12 -Dezembro",
    }

    hoje = now().date()

    # Atualiza o status das mensalidades
    for mensalidade in mensalidades:
        # Calcula a data completa de vencimento
        if mensalidade.valor is None:
            mensalidade.valor = mensalidade.aluno.turma.valorMensalidade
            mensalidade.save()

        # Atualizar a data de vencimento
        dia_vencimento = mensalidade.dia_pagamento
        data_vencimento = hoje.replace(
            day=dia_vencimento,
            month=mensalidade.mes,
            year=hoje.year,
        )
        mensalidade.data_vencimento = data_vencimento

        # Atualizar o status
        if data_vencimento < hoje and mensalidade.status == "Em Aberto":
            mensalidade.status = "Em Atraso"
            mensalidade.save()

        # Nome do mês
        mensalidade.mes_nome = MESES[mensalidade.mes]

    if request.method == "POST":
        mensalidade_id = request.POST.get("mensalidade_id")
        mensalidade = get_object_or_404(Mensalidade, id=mensalidade_id)
        mensalidade.status = "Pago"
        mensalidade.save()
        return redirect("alunoDetalhes", aluno_id=aluno.id)

    return render(
        request,
        "alunoDetalhes.html",
        {
            "aluno": aluno,
            "mensalidades": mensalidades,
        },
    )


def excluirAluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    if request.method == 'POST':
        aluno.delete()
        return redirect('turmaDetalhes', aluno.turma.id)  # Redireciona para a turma do aluno