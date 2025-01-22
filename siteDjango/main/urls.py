from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('registrar/', views.registrar, name='registrar'),
    path('adminDashboard/', views.adminDashboard, name='adminDashboard'),
    path('addTurma/', views.addTurma, name='addTurma'),
    path('turmasDashboard', views.turmasDashboard, name='turmasDashboard'),
    path('turmaDetalhes/<int:turma_id>/', views.turmaDetalhes, name='turmaDetalhes'),
    path('addAluno/', views.addAluno, name='addAluno'),
    path('alunoDetalhes/<int:aluno_id>/', views.alunoDetalhes, name='alunoDetalhes'),
    path('excluirAluno/<int:aluno_id>/', views.excluirAluno, name='excluirAluno'),
    path('logout/', views.logout, name='logout'),
]
