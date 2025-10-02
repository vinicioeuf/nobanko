from django.urls import path

from . import views

app_name = "nobanko_app"
urlpatterns = [
    path("", views.home, name="home"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", views.login_view, name="login"),  # Alterei para login_view
    path("cliente/", views.cliente_overview, name="cliente"),
    path("atendimento/", views.atendimento, name="atendimento"),
    path("transacoes/", views.transacoes, name="transacoes"),
    path("cartoes/", views.cartoes, name="cartoes"),
    path("fatura/", views.fatura, name="fatura"),
    path("emprestimos/", views.emprestimos, name="emprestimos"),
    path("gerente/", views.gerente, name="gerente"),
    path("gerenciamento/", views.gerenciamento, name="gerenciamento"),
    path("solicitacoes/", views.solicitacoes, name="solicitacoes"),
    path("mensagens/", views.mensagens, name="mensagens"),
    path("boletos/", views.boletos, name="boletos"),
]