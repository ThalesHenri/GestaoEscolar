import re
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from datetime import date, timedelta
from django.contrib.auth.models import User


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_escola = models.CharField(max_length=255, blank=True, null=True)



    def __str__(self):
        return self.usuario.username


class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100, verbose_name="Responsável")
    cpf_responsavel = models.CharField(max_length=14, verbose_name="CPF do Responsável", blank=True, null=True)  # Novo campo
    telefone = models.DecimalField(max_digits=11, decimal_places=0, verbose_name="Telefone")
    idade = models.PositiveIntegerField()
    dia_pagamento = models.PositiveIntegerField()
    turma = models.ForeignKey(
        'Turma', on_delete=models.CASCADE, related_name='alunos')

    def save(self, *args, **kwargs):
        """Cria mensalidades para o aluno ao salvá-lo."""
        super().save(*args, **kwargs)
        if not self.mensalidades.exists():
            # Cria 12 mensalidades com base no dia de pagamento
            hoje = timezone.now().date()  # Data atual
            for mes in range(1, 13):  # Para cada mês do ano
                try:
                    # Define a data de vencimento para o dia de pagamento no mês correspondente
                    data_vencimento = date(hoje.year, mes, self.dia_pagamento)
                except ValueError:
                    # Se o dia de pagamento não for válido para o mês (ex: 31 de fevereiro), ajusta para o último dia do mês
                    ultimo_dia_mes = date(
                        hoje.year, mes + 1, 1) - timezone.timedelta(days=1)
                    data_vencimento = ultimo_dia_mes

                # Define o valor da mensalidade
                if mes == 1:  # Janeiro (matrícula)
                    valor = self.turma.valorMatricula
                else:  # Outros meses (mensalidades)
                    valor = self.turma.valorMensalidade

                Mensalidade.objects.create(
                    aluno=self,
                    data_vencimento=data_vencimento,  # Usa apenas o campo data_vencimento
                    valor_base=valor,  # Valor da mensalidade ou matrícula
                    status="Em Aberto"  # Define o status inicial
                )

    def possui_pendencias(self):
        """Verifica se o aluno possui mensalidades em atraso."""
        hoje = timezone.now().date()
        return self.mensalidades.filter(status='Em Atraso').exists()

    def __str__(self):
        return self.nome


class Turma(models.Model):
    TURNO_CHOICES = [
        ('Manhã', 'Manhã'),
        ('Tarde', 'Tarde'),
    ]
    nome = models.CharField(max_length=100)
    turno = models.CharField(max_length=5, choices=TURNO_CHOICES)
    valorMensalidade = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Mensalidade")
    valorMatricula = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name="Matrícula")  # Valor da matrícula

    def saldo_total(self):
        return self.valorMensalidade * self.alunos.count()

    def __str__(self):
        return self.nome


# MAIS SEGURANÇA PARA SENHAS - CRIAÇÃO DE SENHAS FORTES
def validar_senha_forte(senha):
    if len(senha) < 8:
        raise ValidationError('A senha deve ter pelo menos 8 caracteres.')
    if not re.search(r'[A-Z]', senha):  # Verifica se tem letra maiúscula
        raise ValidationError(
            'A senha deve conter pelo menos uma letra maiúscula.')
    if not re.search(r'[0-9]', senha):  # Verifica se tem número
        raise ValidationError('A senha deve conter pelo menos um número.')
    if not re.search(r'[@$!%*?&]', senha):  # Verifica se tem caractere especial
        raise ValidationError(
            'A senha deve conter pelo menos um caractere especial (@, $, !, %, *, ?, &).')
    return True


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=100)

    def set_senha(self, senha):
        """
        Define a senha com validação de segurança e a armazena de forma segura (hashing).
        """
        validar_senha_forte(senha)  # Valida a senha antes de salvar
        # Armazena a senha com hash para segurança
        self.senha = make_password(senha)

    def check_senha(self, senha):
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        """
        from django.contrib.auth.hashers import check_password
        return check_password(senha, self.senha)

    def __str__(self):
        return self.nome


class Feed(models.Model):
    acao = models.CharField(max_length=100)
    data = models.DateTimeField(default=now)
    

class ExecucaoTarefas(models.Model):
    nome = models.CharField(max_length=100, unique=True,default="ExecucaoTarefas")
    ultima_execucao = models.DateTimeField()


class Mensalidade(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('Dinheiro', 'Dinheiro'),
        ('Cartão', 'Cartão'),
        ('PIX', 'PIX'),
    ]

    aluno = models.ForeignKey(
        'Aluno', on_delete=models.CASCADE, related_name='mensalidades')
    data_vencimento = models.DateField()  # Data de vencimento
    status = models.CharField(
        max_length=20,
        choices=[('Em Aberto', 'Em Aberto'), ('Pago', 'Pago'),
                 ('Em Atraso', 'Em Atraso')],
        default='Em Aberto'
    )
    dia_pagamento_realizado = models.DateField(null=True, blank=True)
    valor_base = models.DecimalField(
        max_digits=8, decimal_places=2)  # Valor original sem desconto
    valor_final = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True)  # Valor com desconto aplicado
    forma_pagamento = models.CharField(
        max_length=10, choices=FORMA_PAGAMENTO_CHOICES, null=True, blank=True)
    desconto_percentual = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)  # Percentual do desconto

    def aplicar_desconto(self, percentual):
        """Aplica um desconto percentual na mensalidade (exceto matrícula)."""
        if percentual > 0 and self.valor_base:
            self.desconto_percentual = percentual
            desconto_aplicado = (percentual / 100) * self.valor_base
            self.valor_final = self.valor_base - desconto_aplicado
        else:
            self.valor_final = self.valor_base  # Sem desconto

        self.save(update_fields=['desconto_percentual', 'valor_final'])

    def save(self, *args, **kwargs):
        """Atualiza o status da mensalidade e aplica o desconto ao salvar."""
        hoje = timezone.now().date()

        if self.status == 'Em Aberto' and self.data_vencimento < hoje:
            self.status = 'Em Atraso'

        # Se ainda não tem um valor final definido, garantir que seja igual ao valor base
        if self.valor_final is None:
            self.valor_final = self.valor_base

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Mensalidade {self.data_vencimento.strftime('%Y-%m-%d')} - {self.aluno.nome}"
