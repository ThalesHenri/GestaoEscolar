import re
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone


class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    idade = models.PositiveIntegerField()
    dia_pagamento = models.PositiveIntegerField()  # Agora é o dia de pagamento (1-31)
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE, related_name='alunos')

    def save(self, *args, **kwargs):
        """Cria mensalidades para o aluno ao salvá-lo."""
        super().save(*args, **kwargs)
        if not self.mensalidades.exists():
            # Cria 12 mensalidades com o dia do pagamento
            for mes in range(1, 13):
                Mensalidade.objects.create(
                    aluno=self,
                    mes=mes,
                    status="Em Aberto",
                    dia_pagamento=self.dia_pagamento  # Define o dia de pagamento para a mensalidade
                )

    def __str__(self):
        return self.nome


class Turma(models.Model):
    TURNO_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
    ]
    nome = models.CharField(max_length=100)
    turno = models.CharField(max_length=5, choices=TURNO_CHOICES)
    valorMensalidade = models.DecimalField(max_digits=8, decimal_places=2)
    

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



class Mensalidade(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='mensalidades')
    mes = models.IntegerField()
    status = models.CharField(max_length=20, choices=[('Em Aberto', 'Em Aberto'), ('Pago', 'Pago'), ('Em Atraso', 'Em Atraso')])
    dia_pagamento = models.IntegerField() # Exemplo de campo de dia de pagamento
    dia_pagamento_realizado = models.DateField(null=True, blank=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # Novo campo

    def __str__(self):
        return f"Mensalidade {self.mes}/{self.aluno.nome}"



