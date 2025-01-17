from django.db import models

# Create your models here.


class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    dataPagamento = models.DateField()  

    def __str__(self):
        return self.nome
    
class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    senha = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    

class Pagamento(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    dataPagamentoRealizado = models.DateField()
    
    

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    turno = models.CharField(max_length=10)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    participantes = models.ManyToManyField(Aluno)