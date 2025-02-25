from django import forms
from .models import Turma, Aluno
from .models import *


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'idade', 'dia_pagamento',
                  'responsavel', 'cpf_responsavel', 'telefone']  # Altere para 'dia_pagamento'
        widgets = {
            'nome': forms.TextInput(attrs={'maxlength': 100, 'placeholder': 'Nome completo:'}),
            'idade': forms.NumberInput(attrs={'min': 1}),
            # Limite entre 1 e 31
            'dia_pagamento': forms.NumberInput(attrs={'min': 1, 'max': 25,'placeholder': 'Selecione o melhor dia para pagamento.'}),
            'responsavel': forms.TextInput(attrs={'maxlength': 100, 'placeholder': 'Nome completo:'}),
            'telefone': forms.NumberInput(attrs={'min': 11, 'max': 99999999999, 'placeholder': '(00) 00000-0000'}),
            'cpf_responsavel': forms.TextInput(attrs={'maxlength': 14, 'placeholder': '000.000.000-00'}),  # Novo campo
        }


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'turno', 'valorMensalidade', 'valorMatricula']
        widgets = {'nome': forms.TextInput(attrs={'maxlength': 50,'class': 'form-control','placeholder': 'Nome da turma'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'valorMensalidade': forms.NumberInput(attrs={'min': 0,'max': 10000,'step': 0.01,'maxlength': 10,'placeholder': 'R$ 0,00','class': 'form-control'}),
            'valorMatricula': forms.NumberInput(attrs={'min': 0,'max': 10000,'step': 0.01,'maxlength': 10,'placeholder': 'R$ 0,00','class': 'form-control'})
        }

    def clean_valorMensalidade(self):
        """Valida o valor da mensalidade."""
        valor_base = self.cleaned_data['valorMensalidade']
        if valor_base < 0:
            raise forms.ValidationError("O valor da mensalidade não pode ser negativo.")
        return valor_base

    def clean_valorMatricula(self):
        """Valida o valor da matrícula."""
        valor = self.cleaned_data['valorMatricula']
        if valor < 0:
            raise forms.ValidationError("O valor da matrícula não pode ser negativo.")
        return valor


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha']



class DescontoForm(forms.Form):
    desconto = forms.DecimalField(
        label="Desconto (%)",
        min_value=0,
        max_value=100,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )