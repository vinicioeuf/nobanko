from datetime import date

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, get_user_model, login, logout

from .models import Usuario

User = get_user_model()
def base_context(extra=None):
	base = {
		"bank_name": "NoBanko",
		"nav_links": [
			{"label": "Início", "view_name": "nobanko_app:home", "description": "Visão geral do NoBanko"},
			{"label": "Cliente", "view_name": "nobanko_app:cliente", "description": "Central do cliente"},
			{"label": "Transações", "view_name": "nobanko_app:transacoes", "description": "Movimentações e histórico"},
			{"label": "Cartões", "view_name": "nobanko_app:cartoes", "description": "Controle dos seus cartões"},
			{"label": "Atendimento", "view_name": "nobanko_app:atendimento", "description": "Fale com a gente"},
			{"label": "Fatura", "view_name": "nobanko_app:fatura", "description": "Resumo da fatura"},
			{"label": "Empréstimos", "view_name": "nobanko_app:emprestimos", "description": "Ofertas sob medida"},
			{"label": "Gerente", "view_name": "nobanko_app:gerente", "description": "Seu gerente pessoal"},
			{"label": "Gerenciamento", "view_name": "nobanko_app:gerenciamento", "description": "Ferramentas para gestores"},
			{"label": "Solicitações", "view_name": "nobanko_app:solicitacoes", "description": "Acompanhe seus pedidos"},
			{"label": "Mensagens", "view_name": "nobanko_app:mensagens", "description": "Comunicação segura"},
			{"label": "Boletos", "view_name": "nobanko_app:boletos", "description": "Pague e emita boletos"},
		],
		"current_year": date.today().year,
	}

	if extra:
		base.update(extra)

	return base


def home(request):
	context = base_context(
		{
			"hero": {
				"title": "NoBanko: um banco digital completo inspirado em quem quer simplificar a vida",
				"subtitle": "Abra sua conta em minutos, controle seus cartões, acompanhe faturas e resolva tudo sem sair do app.",
				"primary_cta": {"label": "Abrir conta", "view_name": "nobanko_app:cadastro"},
				"secondary_cta": {"label": "Acessar conta", "view_name": "nobanko_app:login"},
			},
			"feature_cards": [
				{
					"title": "Conta digital sem tarifas",
					"description": "Transferências ilimitadas, pagamentos instantâneos e atalhos inteligentes para o seu dia a dia.",
					"badge": "Cliente",
				},
				{
					"title": "Cartão NoBanko",
					"description": "Controle total da fatura, ajuste de limite em tempo real e modo viagem com um toque.",
					"badge": "Cartões",
				},
				{
					"title": "Atendimento humano 24/7",
					"description": "Fale com especialistas por chat, voz ou mensagem segura e acompanhe o histórico dentro do app.",
					"badge": "Atendimento",
				},
				{
					"title": "Empréstimo inteligente",
					"description": "Simule e contrate na hora com parcelas inteligentes e acompanhamento transparente.",
					"badge": "Empréstimos",
				},
			],
			"journey_steps": [
				{
					"title": "1. Crie sua conta",
					"description": "Compartilhe seus dados básicos e ganhe acesso imediato ao app NoBanko.",
				},
				{
					"title": "2. Personalize",
					"description": "Escolha limites, defina metas e organize as notificações do seu jeito.",
				},
				{
					"title": "3. Viva o banco",
					"description": "Pague boletos, acompanhe pedidos e fale com o gerente sem burocracia.",
				},
			],
			"testimonials": [
				{
					"name": "Patrícia, 29",
					"role": "Empreendedora",
					"quote": "Com o NoBanko eu centralizei minha vida financeira. A fatura é transparente e o gerente resolve tudo pelo chat.",
				},
				{
					"name": "Gustavo, 34",
					"role": "Designer",
					"quote": "O app é fluido e bonito. Em poucos cliques ajusto limite, agendo boleto e confirmo transferências.",
				},
			],
		}
	)
	return render(request, "home.html", context)


def cliente_overview(request):
	context = base_context(
		{
			"page_title": "Central do Cliente",
			"account_snapshot": {
				"saldo": "R$ 8.540,27",
				"investido": "R$ 3.200,00",
				"limite": "R$ 12.000,00",
				"fatura_atual": "R$ 1.980,63",
			},
			"modules": [
				{
					"title": "Cartão",
					"summary": "Visualize número virtual, limite, bloqueie e desbloqueie em segundos.",
					"cta": {"label": "Ir para cartões", "view_name": "nobanko_app:cartoes"},
				},
				{
					"title": "Fatura",
					"summary": "Acompanhe a fatura em tempo real, organize categorias e gere PDF.",
					"cta": {"label": "Ver fatura", "view_name": "nobanko_app:fatura"},
				},
				{
					"title": "Solicitações",
					"summary": "Abra chamados, acompanhe status e envie documentos com segurança.",
					"cta": {"label": "Acompanhar pedidos", "view_name": "nobanko_app:solicitacoes"},
				},
				{
					"title": "Mensagens",
					"summary": "Converse com especialistas, receba orientações personalizadas e histórico completo.",
					"cta": {"label": "Abrir mensagens", "view_name": "nobanko_app:mensagens"},
				},
				{
					"title": "Boletos",
					"summary": "Emita, pague e acompanhe boletos com leitura automática pelo app.",
					"cta": {"label": "Gerenciar boletos", "view_name": "nobanko_app:boletos"},
				},
				{
					"title": "Empréstimo",
					"summary": "Simule valores, consulte ofertas e contrate com assinatura digital.",
					"cta": {"label": "Ver ofertas", "view_name": "nobanko_app:emprestimos"},
				},
			],
			"timeline": [
				{
					"label": "Limite ajustado",
					"timestamp": "Hoje, 09:40",
					"status": "Concluído",
				},
				{
					"label": "Pagamento recebido",
					"timestamp": "Ontem, 19:21",
					"status": "Concluído",
				},
				{
					"label": "Solicitação de cartão adicional",
					"timestamp": "Há 3 dias",
					"status": "Em análise",
				},
			],
		}
	)
	return render(request, "cliente_overview.html", context)


def atendimento(request):
	context = base_context(
		{
			"page_title": "Atendimento humano 24/7",
			"support_channels": [
				{
					"title": "Chat inteligente",
					"description": "Conecte-se com especialistas em segundos com histórico completo de conversas.",
					"availability": "Sempre disponível",
				},
				{
					"title": "Mensagem segura",
					"description": "Envie anexos, fale com o gerente e receba atualizações com criptografia de ponta a ponta.",
					"availability": "Retorno em até 30 min",
				},
				{
					"title": "Atendimento por voz",
					"description": "Se preferir uma ligação, um especialista liga para você na hora marcada.",
					"availability": "Das 7h às 22h",
				},
			],
			"service_metrics": [
				{"label": "Tempo médio de resposta", "value": "2 min"},
				{"label": "Satisfação dos clientes", "value": "98%"},
				{"label": "Chamados resolvidos no primeiro contato", "value": "87%"},
			],
			"faqs": [
				{
					"question": "Como acompanho uma solicitação em andamento?",
					"answer": "Acesse a área de Solicitações para visualizar status, prazo estimado e responder ao time.",
				},
				{
					"question": "Posso falar direto com o gerente?",
					"answer": "Sim, escolha o canal Gerente e agende um horário ou envie uma mensagem instantânea.",
				},
			],
		}
	)
	return render(request, "atendimento.html", context)


def transacoes(request):
	context = base_context(
		{
			"page_title": "Transações em tempo real",
			"transaction_filters": [
				{"label": "Todos", "active": True},
				{"label": "Entradas", "active": False},
				{"label": "Saídas", "active": False},
				{"label": "Agendadas", "active": False},
			],
			"transactions": [
				{
					"title": "Transferência recebida",
					"category": "Entrada",
					"amount": "+ R$ 1.200,00",
					"timestamp": "Hoje, 10:15",
				},
				{
					"title": "Pagamento fatura cartão",
					"category": "Saída",
					"amount": "- R$ 850,40",
					"timestamp": "Ontem, 22:58",
				},
				{
					"title": "Boleto agendado",
					"category": "Agendada",
					"amount": "- R$ 230,00",
					"timestamp": "05 Out, 08:00",
				},
				{
					"title": "Transferência PIX",
					"category": "Saída",
					"amount": "- R$ 95,30",
					"timestamp": "03 Out, 13:44",
				},
			],
			"insights": [
				"Você movimentou R$ 6.430,00 nos últimos 7 dias.",
				"As inscrições em serviços representaram 12% das saídas do mês.",
				"Seu boleto de energia vence em 3 dias.",
			],
		}
	)
	return render(request, "transacoes.html", context)


def cartoes(request):
	context = base_context(
		{
			"page_title": "Controle total dos seus cartões",
			"card_overview": {
				"nome": "NoBanko Ultravioleta",
				"limite_atual": "R$ 12.000,00",
				"limite_disponivel": "R$ 8.450,00",
				"fechamento": "10 de cada mês",
				"vencimento": "17 de cada mês",
			},
			"card_actions": [
				{"label": "Ajustar limite", "description": "Defina limites personalizados por categoria de gasto."},
				{"label": "Bloquear/Desbloquear", "description": "Proteção instantânea e modo viagem automático."},
				{"label": "Cartão virtual", "description": "Crie cartões temporários para compras online com validade programada."},
			],
			"additional_cards": [
				{"nome": "Cartão adicional Sofia", "status": "Em uso", "limite": "R$ 1.500,00"},
				{"nome": "Cartão virtual viagem", "status": "Expira em 12 dias", "limite": "R$ 3.000,00"},
			],
		}
	)
	return render(request, "cartoes.html", context)


def fatura(request):
	context = base_context(
		{
			"page_title": "Sua fatura, em detalhe",
			"current_invoice": {
				"valor": "R$ 1.980,63",
				"data_fechamento": "10/10",
				"data_vencimento": "17/10",
				"progresso": 66,
			},
			"spending_categories": [
				{"label": "Alimentação", "value": "R$ 420,00", "percent": 21},
				{"label": "Mobilidade", "value": "R$ 280,50", "percent": 14},
				{"label": "Streaming", "value": "R$ 150,90", "percent": 8},
				{"label": "Viagem", "value": "R$ 940,00", "percent": 47},
			],
			"invoice_actions": [
				{"label": "Antecipar parcelas", "description": "Ganhe desconto ao antecipar compras parceladas."},
				{"label": "Gerar boleto da fatura", "description": "Envie seu boleto de pagamento em PDF ou código de barras."},
				{"label": "Exportar PDF", "description": "Baixe a fatura completa com detalhes por categoria."},
			],
		}
	)
	return render(request, "fatura.html", context)


def emprestimos(request):
	context = base_context(
		{
			"page_title": "Empréstimos sob medida",
			"loan_offers": [
				{
					"title": "Empréstimo pessoal",
					"rate": "1,39% a.m.",
					"description": "Parcelas flexíveis em até 48x com liberação instantânea.",
				},
				{
					"title": "Crédito para projetos",
					"rate": "1,79% a.m.",
					"description": "Pensado para reformas, estudos ou viagens com carência de 60 dias.",
				},
				{
					"title": "Capital de giro",
					"rate": "1,99% a.m.",
					"description": "Ideal para quem empreende e precisa equilibrar o fluxo de caixa.",
				},
			],
			"simulator": {
				"valor_min": "R$ 1.000,00",
				"valor_max": "R$ 80.000,00",
				"parcelas": ["12x", "24x", "36x", "48x"],
			},
			"tips": [
				"Receba alertas quando a taxa ficar mais baixa.",
				"Antecipe parcelas sem custo adicional e reduza juros.",
				"Contrate direto pelo app com assinatura digital.",
			],
		}
	)
	return render(request, "emprestimos.html", context)


def gerente(request):
	context = base_context(
		{
			"page_title": "Seu gerente pessoal",
			"manager_profile": {
				"nome": "Camila Ribeiro",
				"especialidade": "Planejamento financeiro",
				"disponibilidade": "Seg. a Sex. 8h - 20h",
				"tempo_resposta": "Resposta média em 12 min",
			},
			"contact_channels": [
				{"label": "Chat prioritário", "description": "Converse com Camila por chat com fila dedicada."},
				{"label": "Reunião por vídeo", "description": "Agende uma chamada para planejar suas finanças."},
				{"label": "Mensagens seguras", "description": "Envie metas e documentos em ambiente criptografado."},
			],
			"recent_actions": [
				"Analisou sua solicitação de aumento de limite.",
				"Sugeriu realocar 10% do saldo para investimento protegido.",
				"Revisou situação da fatura e enviou relatório resumido.",
			],
		}
	)
	return render(request, "gerente.html", context)


def gerenciamento(request):
	context = base_context(
		{
			"page_title": "Painel de gerenciamento",
			"management_cards": [
				{
					"title": "Contas vinculadas",
					"description": "Gerencie contas PJ, usuários adicionais e permissões de acesso.",
				},
				{
					"title": "Políticas de segurança",
					"description": "Acompanhe dispositivos conectados, configure aprovações duplas e biometria.",
				},
				{
					"title": "Relatórios",
					"description": "Baixe relatórios de transações, faturas e auditoria com filtros avançados.",
				},
			],
			"workflow_steps": [
				"Defina perfis de acesso para colaboradores.",
				"Aprove ou rejeite solicitações pendentes.",
				"Configure alertas personalizados para cada equipe.",
			],
		}
	)
	return render(request, "gerenciamento.html", context)


def solicitacoes(request):
	context = base_context(
		{
			"page_title": "Solicitações em andamento",
			"requests": [
				{
					"title": "Cartão adicional para Sofia",
					"status": "Em análise",
					"estimated": "Resposta em até 12h",
				},
				{
					"title": "Aumento limite cartão principal",
					"status": "Concluído",
					"estimated": "Aprovado hoje às 09h32",
				},
				{
					"title": "Revisão de tarifa",
					"status": "Aguardando documentos",
					"estimated": "Envie até 07/10",
				},
			],
			"next_steps": [
				"Envie documentos pendentes diretamente pela área de mensagens.",
				"Acompanhe as atualizações do gerente em tempo real.",
				"Receba notificações push a cada mudança de status.",
			],
		}
	)
	return render(request, "solicitacoes.html", context)


def mensagens(request):
	context = base_context(
		{
			"page_title": "Mensagens seguras",
			"threads": [
				{
					"title": "Equipe de atendimento",
					"last_message": "Tudo certo com a antecipação da fatura",
					"timestamp": "Hoje, 08:15",
					"status": "Respondido",
				},
				{
					"title": "Gerente Camila",
					"last_message": "Enviei o relatório com metas para outubro",
					"timestamp": "Ontem, 21:47",
					"status": "Mensagem nova",
				},
				{
					"title": "Suporte técnico",
					"last_message": "Novo dispositivo reconhecido",
					"timestamp": "02 Out, 16:02",
					"status": "Resolvido",
				},
			],
			"message_tips": [
				"Use tags para organizar mensagens importantes.",
				"Responda anexando documentos direto da nuvem.",
				"Convide seu gerente para um chat compartilhado em segundos.",
			],
		}
	)
	return render(request, "mensagens.html", context)


def boletos(request):
	context = base_context(
		{
			"page_title": "Emissão e pagamento de boletos",
			"boleto_actions": [
				{
					"title": "Emitir boleto",
					"description": "Crie boletos em segundos e compartilhe o PDF pelo app.",
				},
				{
					"title": "Pagar boleto",
					"description": "Faça leituras por QR Code ou código digitável em segundos.",
				},
				{
					"title": "Agendar pagamento",
					"description": "Garanta que seus boletos sejam pagos automaticamente na data certa.",
				},
			],
			"upcoming_bills": [
				{"title": "Energia elétrica", "valor": "R$ 230,00", "vencimento": "05/10"},
				{"title": "Internet fibra", "valor": "R$ 129,90", "vencimento": "12/10"},
				{"title": "Plano saúde", "valor": "R$ 420,50", "vencimento": "18/10"},
			],
			"integrations": [
				"Envie comprovantes direto para mensagens seguras.",
				"Acompanhe status de pagamentos na área de transações.",
				"Notifique seu gerente sobre boletos acima de R$ 5.000,00.",
			],
		}
	)
	return render(request, "boletos.html", context)


def cadastro(request):
	context = base_context(
		{
			"page_title": "Abra sua conta NoBanko",
			"subtitle": "Leva menos de 5 minutos para começar a usar um banco pensado para a sua rotina.",
			"form_sections": [
				{
					"title": "Seus dados",
					"fields": [
						{
							"label": "Nome completo",
							"name": "full_name",
							"type": "text",
							"autocomplete": "name",
							"placeholder": "Ex: Ana Maria Silva",
						},
						{
							"label": "CPF",
							"name": "cpf",
							"type": "text",
							"autocomplete": "off",
							"placeholder": "000.000.000-00",
							"width": "half",
						},
						{
							"label": "Data de nascimento",
							"name": "birth_date",
							"type": "date",
							"autocomplete": "bday",
							"width": "half",
						},
						{
							"label": "Celular",
							"name": "phone",
							"type": "tel",
							"autocomplete": "tel",
							"placeholder": "(11) 99999-9999",
							"width": "half",
						},
						{
							"label": "E-mail",
							"name": "email",
							"type": "email",
							"autocomplete": "email",
							"placeholder": "seuemail@exemplo.com",
							"width": "half",
						},
					],
				},
				{
					"title": "Dados de acesso",
					"fields": [
						{
							"label": "Senha",
							"name": "password",
							"type": "password",
							"autocomplete": "new-password",
							"placeholder": "Mínimo 8 caracteres",
						},
						{
							"label": "Confirmar senha",
							"name": "password_confirmation",
							"type": "password",
							"autocomplete": "new-password",
							"placeholder": "Repita a senha",
						},
					],
				},
			],
			"benefits": [
				"Conta digital gratuita e com transferências ilimitadas.",
				"Cartão com controle em tempo real e modo viagem automático.",
				"Atendimento humano 24/7 para resolver qualquer situação.",
			],
		}
	)
	if request.method == "GET":
		return render(request, "cadastro.html", context)

	nome = request.POST.get("full_name")
	cpf = request.POST.get("cpf")
	birth_date = request.POST.get("birth_date") or None
	phone = request.POST.get("phone")
	email = request.POST.get("email")
	password = request.POST.get("password")
	password_confirmation = request.POST.get("password_confirmation")

	if password != password_confirmation:
		return HttpResponse("As senhas não coincidem")

	if User.objects.filter(email=email).exists():
		return HttpResponse("Usuário já existe")

	if cpf and Usuario.objects.filter(cpf=cpf).exists():
		return HttpResponse("CPF já cadastrado")

	novo_usuario = User.objects.create_user(
		email=email,
		username=email,
		password=password,
		first_name=nome,
	)
	Usuario.objects.create(
		user=novo_usuario,
		cpf=cpf,
		phone=phone,
		birth_date=birth_date,
	)
	login(request, novo_usuario)
	return redirect('nobanko_app:cliente')
    
	



def login_view(request):
	context = base_context(
		{
			"page_title": "Entre na sua conta",
			"subtitle": "Use suas credenciais para acessar todos os produtos NoBanko.",
			"login_fields": [
				{
					"label": "E-mail",
					"name": "username",
					"type": "text",
					"autocomplete": "username",
					"placeholder": "seuemail@exemplo.com",
				},
				{
					"label": "Senha",
					"name": "password",
					"type": "password",
					"autocomplete": "current-password",
					"placeholder": "Digite sua senha",
				},
			],
			"tips": [
				"Não compartilhe sua senha e ative a biometria para mais segurança.",
				"Você pode verificar dispositivos conectados na área de gerenciamento.",
			],
		}
	)

	if request.method == "GET":
		return render(request, "login.html", context)

	username = request.POST.get("username")
	password = request.POST.get("password")
	user = authenticate(request, username=username, password=password)
	if user:
		login(request, user)
		return redirect('nobanko_app:cliente')
	return HttpResponse('E-mail ou senha inválidas')
	
 

