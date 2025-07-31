from django.urls import path
from . import views
from .views import excluir_turma
from .views import aplicarDesconto, editar_perfil


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('get_mensalidades/', views.get_mensalidades, name='get_mensalidades'),
    path('registrar/', views.registrar, name='registrar'),
    path('adminDashboard/', views.adminDashboard, name='adminDashboard'),
    path('addTurma/', views.addTurma, name='addTurma'),
    path('turmasDashboard', views.turmasDashboard, name='turmasDashboard'),
    path('turmaDetalhes/<int:turma_id>/', views.turmaDetalhes, name='turmaDetalhes'),
    path('addAluno/', views.addAluno, name='addAluno'),
    path('alunoDetalhes/<int:aluno_id>/', views.alunoDetalhes, name='alunoDetalhes'),
    path('excluirAluno/<int:aluno_id>/', views.excluirAluno, name='excluirAluno'),
    path("turma/<int:turma_id>/excluir/", excluir_turma, name="excluirTurma"),
    path('alunosDashboard/', views.alunosDashboard, name='alunosDashboard'),
    path('editarAluno/<int:aluno_id>/', views.editarAluno, name='editarAluno'),
    path('logout/', views.logout, name='logout'),
    path('pagamentoDashboard/', views.pagamentoDashboard, name='pagamentoDashboard'),
    path('limparFeed/', views.limparFeed, name='limparFeed'),
    path('perfil/', views.perfil, name="perfil"),
    path('aluno/<int:aluno_id>/aplicar_desconto/', aplicarDesconto, name='aplicarDesconto'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    
]
