from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import authenticate, update_session_auth_hash
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
import json
import os
from django.db.models import Q, Sum, F, Case, When
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib import messages
from .models import Turma, Aluno, Mensalidade, Perfil, Feed, ExecucaoTarefas
from datetime import date
from django.utils.timezone import now

from .forms import *
from .forms import AlunoForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'index.html')


@login_required
def perfil(request):
    perfil = get_object_or_404(Perfil, usuario=request.user)
    return render(request, "perfil.html", {"perfil": perfil})


@login_required
def editar_perfil(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        # Verifica qual formulário foi enviado
        if 'nome' in request.POST:  # Formulário de edição de perfil
            # Atualiza o nome de usuário, nome da escola e e-mail
            novo_username = request.POST.get('nome', perfil.usuario.username)
            nome_escola = request.POST.get('nome_escola', perfil.nome_escola)
            novo_email = request.POST.get('email', perfil.usuario.email)

            # Verifica se o nome de usuário já existe
            if User.objects.exclude(id=perfil.usuario.id).filter(username=novo_username).exists():
                messages.error(request, "Nome de usuário já está em uso.")
                return redirect('editar_perfil')

            # Verifica se o email já existe
            if User.objects.exclude(id=perfil.usuario.id).filter(email=novo_email).exists():
                messages.error(request, "E-mail já está em uso.")
                return redirect('editar_perfil')

            perfil.usuario.username = novo_username
            perfil.usuario.email = novo_email
            perfil.nome_escola = nome_escola
            perfil.usuario.save()
            perfil.save()

            # Registro no feed
            Feed.objects.create(
                acao="O perfil do usuário foi atualizado!", data=timezone.now())

            messages.success(request, "Dados atualizados com sucesso!")
            return redirect('editar_perfil')

        elif 'senha_atual' in request.POST:  # Formulário de alteração de senha
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            # Verifica se a senha atual está correta
            if not authenticate(username=request.user.username, password=senha_atual):
                messages.error(request, "Senha atual incorreta.")
                return redirect('editar_perfil')

            # Verifica se a nova senha e a confirmação coincidem
            if nova_senha != confirmar_senha:
                messages.error(request, "As senhas não coincidem.")
                return redirect('editar_perfil')

            # Atualiza a senha
            request.user.set_password(nova_senha)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Mantém o usuário logado

            # Registro no feed
            Feed.objects.create(
                acao="A senha do usuário foi alterada!", data=timezone.now())

            messages.success(request, "Senha alterada com sucesso!")
            return redirect('editar_perfil')

    return render(request, 'editar_perfil.html', {'perfil': perfil})


def registrar(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        if not usuario or not email or not senha:
            return render(request, 'erro.html', {'mensagem': 'Todos os campos são obrigatórios!'})

        try:
            user = User.objects.create_user(
                username=usuario, email=email, password=senha)
            # Cria perfil com nome padrão
            Perfil.objects.create(usuario=user, nome_escola="Minha Escola")

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
            feed = Feed(acao="Usuário logado!", data=timezone.now())
            feed.save()
            return redirect('adminDashboard')
        else:
            # Renderiza a página de erro em caso de falha na autenticação
            return render(request, 'erro.html')

    # Renderiza a página de login para requisições GET
    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    feed = Feed(acao="Usuário foi deslogado!", data=timezone.now())
    feed.save()
    return render(request, 'logout_redirect.html')  # Usa o template de redirecionamento





@login_required
def addTurma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            feed = Feed(
                acao=f"Turma {form.cleaned_data['nome']} foi adicionada!", data=timezone.now())
            feed.save()
            return redirect('turmasDashboard')
    else:
        form = TurmaForm()

    return render(request, 'addTurma.html', {'form': form})


@login_required
def turmasDashboard(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('turmasDashboard')  # Atualiza a página após salvar
    else:
        form = TurmaForm()

    turmas = Turma.objects.all()

    # Criar dicionários para armazenar os saldos
    saldo_anual_por_turma = {}
    saldo_mensal_por_turma = {}

    for turma in turmas:
        # Cálculo do saldo anual: soma todas as mensalidades (matrícula + 11 meses)
        saldo_anual = turma.alunos.aggregate(
            total=Sum('mensalidades__valor_final')
        )['total'] or 0  # Retorna 0 se não houver valores

        # Filtra as mensalidades de DEZEMBRO (mês 12)
        saldo_mensal = turma.alunos.filter(
            mensalidades__data_vencimento__month=12  # Forma correta de filtrar o mês
        ).aggregate(
            total=Sum('mensalidades__valor_final')
        )['total'] or 0

        # Armazena nos dicionários
        saldo_anual_por_turma[turma.id] = saldo_anual
        saldo_mensal_por_turma[turma.id] = saldo_mensal

    return render(request, 'turmasDashboard.html', {
        'turmas': turmas,
        'form': form,
        'saldo_anual_por_turma': saldo_anual_por_turma,
        'saldo_mensal_por_turma': saldo_mensal_por_turma
    })


@login_required
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
            feed = Feed(
                acao=f"Aluno(a) {aluno.nome} foi adicionado(a)!", data=timezone.now())
            feed.save()
            # Redireciona para a mesma página
            return redirect('turmaDetalhes', turma_id=turma.id)
    else:
        # Inicializa o formulário vazio para a adição de novos alunos
        form = AlunoForm()

    # Obtém os alunos da turma utilizando o `related_name='alunos'`
    alunos = turma.alunos.all()

    # Renderiza a página com os dados da turma, alunos e formulário
    return render(request, 'turmaDetalhes.html', {'turma': turma, 'alunos': alunos, 'form': form})


@login_required
def alunosDashboard(request):
    alunos = Aluno.objects.all()
    return render(request, 'alunosDashboard.html', {'alunos': alunos})


def limparFeed(request):
    Feed.objects.all().delete()
    return redirect('adminDashboard')


@login_required
def editarAluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            feed = Feed(
                acao=f"Aluno {aluno.nome} editado com sucesso!", data=timezone.now())
            feed.save()
            return redirect('alunosDashboard')
    else:
        form = AlunoForm(instance=aluno)

    return render(request, 'editarAluno.html', {'form': form, 'aluno': aluno})


@login_required
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
                hoje = timezone.now().date()  # Data atual
                for mes in range(1, 13):  # Para cada mês do ano
                    try:
                        # Define a data de vencimento para o dia de pagamento no mês correspondente
                        data_vencimento = date(
                            hoje.year, mes, aluno.dia_pagamento)
                    except ValueError:
                        # Se o dia de pagamento não for válido para o mês (ex: 31 de fevereiro), ajusta para o último dia do mês
                        ultimo_dia_mes = date(
                            hoje.year, mes + 1, 1) - timezone.timedelta(days=1)
                        data_vencimento = ultimo_dia_mes

                    Mensalidade.objects.create(
                        aluno=aluno,
                        data_vencimento=data_vencimento,  # Usa apenas o campo data_vencimento
                        valor_base=turma.valorMensalidade,  # Valor da mensalidade registrado na turma
                        status="Em Aberto"  # Define o status inicial
                    )

                feed = Feed(
                    acao=f"Aluno(a) {aluno.nome} adicionado(a)!", data=timezone.now())
                feed.save()
                return redirect('addAluno', turma_id=turma.id)
    else:
        form = AlunoForm()

    return render(request, 'addAluno.html', {'form': form, 'turma': turma})


@login_required
def get_mensalidades(request):
    #carrega as mensalidades dos alunos que estão atrasadas
    mensalidades = Mensalidade.objects.all()   
    hoje = date.today()
    
    
    for mensalidade in mensalidades:
        if mensalidade.data_vencimento < hoje:
            mensalidade.status = "Em Atraso"
            #cria um feed para cada mensalidade atrasada
            feed = Feed(
                acao=f"AVISO! Mensalidade {mensalidade.data_vencimento.strftime('%Y-%m-%d')} do aluno(a) {mensalidade.aluno.nome} em atraso!", data=timezone.now()
                )
            feed.save()
            mensalidade.save()
    return redirect('adminDashboard')
    


@login_required
def adminDashboard(request):
    usuario = request.user
    feeds = Feed.objects.all()
    
    context = {
        'usuario': usuario,
        'feeds': feeds
    }
    print(f"aqui está o {usuario}")
    return render(request, 'adminDashboard.html', context=context)


@login_required
def alunoDetalhes(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    mensalidades = aluno.mensalidades.order_by("data_vencimento").all()


    hoje = date.today()

    # Atualiza status das mensalidades
    for mensalidade in mensalidades:
        if mensalidade.valor_base is None:
            mensalidade.valor_base = mensalidade.aluno.turma.valorMensalidade
            mensalidade.save()

        # Verifica se a mensalidade está "Em Atraso"
        if (
            mensalidade.data_vencimento  # Ignora se data_vencimento for None
            # Verifica se a data de vencimento já passou
            and mensalidade.data_vencimento < hoje
            and mensalidade.status == "Em Aberto"  # Verifica se ainda está em aberto
        ):
            mensalidade.status = "Em Atraso"
            feed = Feed(
                acao=f"AVISO! Mensalidade {mensalidade.data_vencimento.strftime('%Y-%m-%d')} do aluno(a) {aluno.nome} em atraso!", data=timezone.now())
            feed.save()
            mensalidade.save()

    if request.method == "POST":
        mensalidade_id = request.POST.get("mensalidade_id")
        forma_pagamento = request.POST.get("forma_pagamento")
        acao = request.POST.get("acao")
        mensalidade = get_object_or_404(Mensalidade, id=mensalidade_id)

        if acao == "marcar_pago":
            mensalidade.status = "Pago"
            mensalidade.dia_pagamento_realizado = hoje
            feed = Feed(
                acao=f"Mensalidade {mensalidade.data_vencimento.strftime('%m')} do aluno(a) {aluno.nome} foi paga!", data=timezone.now())
            feed.save()
            mensalidade.forma_pagamento = forma_pagamento
        elif acao == "desmarcar_pago":
            mensalidade.status = "Em Aberto"
            mensalidade.dia_pagamento_realizado = None

        mensalidade.save()
        return redirect("alunoDetalhes", aluno_id=aluno.id)

    return render(request, "alunoDetalhes.html", {"aluno": aluno, "mensalidades": mensalidades})


@login_required
def aplicarDesconto(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    # Filtra as mensalidades, excluindo janeiro (mês 1)
    mensalidades = aluno.mensalidades.annotate(
        mes=ExtractMonth('data_vencimento')
    ).exclude(mes=1)

    if request.method == "POST":
        form = DescontoForm(request.POST)
        if form.is_valid():
            desconto = form.cleaned_data['desconto']
            for mensalidade in mensalidades:
                if hasattr(mensalidade, 'valor_base'):  # Verifica se o campo existe
                    mensalidade.aplicar_desconto(desconto)

            feed = Feed(
                acao=f"Desconto de {desconto}% aplicado ao aluno(a) {aluno.nome}!",
                data=timezone.now()
            )
            feed.save()
            return redirect('alunoDetalhes', aluno_id=aluno.id)
    else:
        form = DescontoForm()

    context = {'aluno': aluno, 'form': form}
    return render(request, 'desconto.html', context=context)


@login_required
def excluirAluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)

    if request.method == 'POST':  # Garante que a exclusão só ocorre via POST
        aluno.delete()
        feed = Feed(
            acao=f"Aluno {aluno.nome} excluído com sucesso!", data=timezone.now())
        feed.save()
        # Redireciona para o dashboard dos alunos
        origem = request.POST.get('origem', 'alunosDashboard')
        return redirect(origem)

    # Caso o método não seja POST, redirecione ou mostre erro
    messages.error(request, 'Método inválido para exclusão!')

    return redirect('alunosDashboard')


@login_required
def excluir_turma(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)

    if request.method == "POST":
        turma.delete()
        feed = Feed(
            acao=f"Turma {turma.nome} foi excluida!", data=timezone.now())
        feed.save()
        # Redireciona para a lista de turmas
        return redirect("turmasDashboard")

    return redirect("turmaDetalhes", turma_id=turma.id)


@login_required
def pagamentoDashboard(request):
    mensalidades_aberto = Mensalidade.objects.filter(status='Em Aberto')
    mensalidades_atraso = Mensalidade.objects.filter(status='Em Atraso')
    mensalidades_pagas = Mensalidade.objects.filter(status='Pago')
    context = {
        'mensalidades_aberto': mensalidades_aberto,
        'mensalidades_atraso': mensalidades_atraso,
        'mensalidades_pagas': mensalidades_pagas
    }
    return render(request, 'pagamentosDashboard.html', context=context)
