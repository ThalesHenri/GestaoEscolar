from django import forms
from .models import Turma, Aluno
from .models import *


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'idade', 'dia_pagamento','responsavel']  # Altere para 'dia_pagamento'
        widgets = {
            'nome': forms.TextInput(attrs={'maxlength': 100}),
            'idade': forms.NumberInput(attrs={'min': 1}),
            'dia_pagamento': forms.NumberInput(attrs={'min': 1, 'max': 25}),  # Limite entre 1 e 31
            'responsavel': forms.TextInput(attrs={'maxlength': 100})
        }


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'turno', 'valorMensalidade']
        widgets = {
            'nome': forms.TextInput(attrs={'maxlength': 100, 'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-control'}),
            'valorMensalidade': forms.NumberInput(attrs={'min': 0, 'max': 1000, 'step': 0.01})
        }

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha']
