from django import forms
from .models import *


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'idade', 'dataPagamento']
        

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['aluno', 'valor', 'dataPagamentoRealizado']
               

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'turno', 'valor']
        
        
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha']