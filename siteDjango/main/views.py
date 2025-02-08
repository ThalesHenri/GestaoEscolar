from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Turma, Aluno, Mensalidade, Feed
from datetime import date
from django.utils.timezone import now
from .forms import *
from .forms import AlunoForm
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'index.html')


def perfil(request):
    return render(request, 'perfil.html')


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
            feed = Feed(acao="Usuário registrado com sucesso!",
                        data=timezone.now())
            feed.save()
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
    return redirect('login')


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
    return render(request, 'turmasDashboard.html', {'turmas': turmas, 'form': form})


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
                        data_vencimento = date(hoje.year, mes, aluno.dia_pagamento)
                    except ValueError:
                        # Se o dia de pagamento não for válido para o mês (ex: 31 de fevereiro), ajusta para o último dia do mês
                        ultimo_dia_mes = date(hoje.year, mes + 1, 1) - timezone.timedelta(days=1)
                        data_vencimento = ultimo_dia_mes

                    Mensalidade.objects.create(
                        aluno=aluno,
                        data_vencimento=data_vencimento,  # Usa apenas o campo data_vencimento
                        valor=turma.valorMensalidade,  # Valor da mensalidade registrado na turma
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
def alunoDetalhes(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    mensalidades = aluno.mensalidades.order_by("data_vencimento").all()

    hoje = date.today()

    # Atualiza status das mensalidades
    for mensalidade in mensalidades:
        if mensalidade.valor is None:
            mensalidade.valor = mensalidade.aluno.turma.valorMensalidade
            mensalidade.save()

        # Verifica se a mensalidade está "Em Atraso"
        if (
            mensalidade.data_vencimento  # Ignora se data_vencimento for None
            and mensalidade.data_vencimento < hoje  # Verifica se a data de vencimento já passou
            and mensalidade.status == "Em Aberto"  # Verifica se ainda está em aberto
        ):
            mensalidade.status = "Em Atraso"
            feed = Feed(acao=f"AVISO! Mensalidade {mensalidade.data_vencimento.strftime('%Y-%m-%d')} do aluno(a) {aluno.nome} em atraso!", data=timezone.now())
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
            feed = Feed(acao=f"Mensalidade {mensalidade.data_vencimento.strftime('%Y-%m-%d')} do aluno(a) {aluno.nome} foi paga!", data=timezone.now())
            feed.save()
            mensalidade.forma_pagamento = forma_pagamento
        elif acao == "desmarcar_pago":
            mensalidade.status = "Em Aberto"
            mensalidade.dia_pagamento_realizado = None

        mensalidade.save()
        return redirect("alunoDetalhes", aluno_id=aluno.id)

    return render(request, "alunoDetalhes.html", {"aluno": aluno, "mensalidades": mensalidades})


@login_required
def aplicarDesconto(request, aluno_id, mensalidade_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    mensalidade = get_object_or_404(Mensalidade, id=mensalidade_id)

    if request.method == "POST":
        form = DescontoForm(request.POST)
        if form.is_valid():
            desconto = form.cleaned_data['desconto']
            mensalidade.calcular_valor_desconto(desconto)
            # Aplica o desconto
            feed = Feed(
                acao=f"Desconto de {desconto}% para o aluno {aluno.nome} aplicado com sucesso!", data=timezone.now())
            feed.save()
            # Salva a mensalidade com o valor atualizado
            # Redireciona de volta para a página do aluno
            return redirect('alunoDetalhes', aluno_id=aluno.id)
    else:
        form = DescontoForm()

    context = {'aluno': aluno, 'mensalidade': mensalidade, 'form': form}
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
        return redirect('alunosDashboard')

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
