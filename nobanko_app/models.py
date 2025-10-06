from django.db import models

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    conta = models.CharField(max_length=20, unique=True)
    agencia = models.CharField(max_length=10)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Gerente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    codigo_gerente = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Gerente {self.usuario.nome}"


class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    gerente = models.ForeignKey(Gerente, on_delete=models.SET_NULL, null=True, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    colégio = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Cliente {self.usuario.nome}"


class Cartao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    numero = models.CharField(max_length=16, unique=True)
    validade = models.DateField()
    codigo_seguranca = models.CharField(max_length=4)
    limite = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Cartão {self.numero[-4:]} - {self.cliente.usuario.nome}"


class Fatura(models.Model):
    cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    vencimento = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado')
    ])

    def __str__(self):
        return f"Fatura {self.id} - {self.cartao.cliente.usuario.nome}"


class Solicitacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # ex: "aumento de limite", "cartão adicional"
    data = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pendente')

    def __str__(self):
        return f"{self.tipo} - {self.cliente.usuario.nome}"


class Emprestimo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    taxa_juros = models.FloatField()
    parcelas = models.IntegerField()
    data_inicio = models.DateField()
    status = models.CharField(max_length=20, default='ativo')

    def __str__(self):
        return f"Empréstimo {self.id} - {self.cliente.usuario.nome}"


class Transacao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=[
        ('entrada', 'Entrada'),
        ('saida', 'Saída')
    ])
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tipo} - {self.valor} ({self.cliente.usuario.nome})"


class Mensagem(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    conteudo = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    remetente = models.CharField(max_length=50)  # Ex: “cliente”, “gerente”, “sistema”

    def __str__(self):
        return f"Mensagem para {self.cliente.usuario.nome}"


class Atendimento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    gerente = models.ForeignKey(Gerente, on_delete=models.SET_NULL, null=True, blank=True)
    data_abertura = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='em andamento')
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Atendimento {self.id} - {self.cliente.usuario.nome}"


class Gerenciamento(models.Model):
    gerente = models.ForeignKey(Gerente, on_delete=models.CASCADE)
    descricao = models.TextField()
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gerenciamento por {self.gerente.usuario.nome}"
