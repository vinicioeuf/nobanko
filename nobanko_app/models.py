import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone

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
    limite_credito = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("2000.00"))

    def __str__(self):
        return f"Cliente {self.usuario.nome}"

    def depositar(self, valor, descricao=""):
        try:
            valor_decimal = Decimal(valor)
        except (TypeError, ValueError, InvalidOperation):
            raise ValidationError("Informe um valor numérico válido.")

        if valor_decimal <= 0:
            raise ValidationError("O valor do depósito deve ser maior que zero.")

        valor_decimal = valor_decimal.quantize(Decimal("0.01"))

        descricao = (descricao or "Depósito")[:255]

        with transaction.atomic():
            cliente = Cliente.objects.select_for_update().get(pk=self.pk)
            cliente.saldo += valor_decimal
            cliente.save(update_fields=["saldo"])

            transacao = Transacao.objects.create(
                cliente=cliente,
                valor=valor_decimal,
                tipo=Transacao.Tipo.ENTRADA,
                descricao=descricao,
                saldo_resultante=cliente.saldo,
            )

        return transacao

    def solicitar_credito(self, valor, motivo=""):
        if not self.gerente:
            raise ValidationError("Nenhum gerente vinculado ao cliente.")

        try:
            valor_decimal = Decimal(valor)
        except (TypeError, ValueError, InvalidOperation):
            raise ValidationError("Informe um valor numérico válido.")

        if valor_decimal <= 0:
            raise ValidationError("O valor solicitado deve ser maior que zero.")

        valor_decimal = valor_decimal.quantize(Decimal("0.01"))
        motivo = (motivo or "").strip()

        return SolicitacaoCredito.objects.create(
            cliente=self,
            gerente=self.gerente,
            valor=valor_decimal,
            motivo=motivo,
        )

    def pode_solicitar_cartao(self, modelo):
        if not isinstance(modelo, ModeloCartao):
            raise ValidationError("Modelo de cartão inválido.")

        if not modelo.ativo:
            return False

        limite_cliente = (self.limite_credito or Decimal("0"))
        limite_cliente = limite_cliente.quantize(Decimal("0.01"))

        if limite_cliente < modelo.limite_minimo:
            return False

        if modelo.limite_maximo is not None and limite_cliente > modelo.limite_maximo:
            return False

        return True

    def solicitar_cartao(self, modelo, justificativa=""):
        if not self.gerente:
            raise ValidationError("Nenhum gerente vinculado ao cliente.")

        if not self.pode_solicitar_cartao(modelo):
            raise ValidationError("Cliente não atende aos requisitos para este cartão.")

        justificativa = (justificativa or "").strip()

        return PedidoCartao.objects.create(
            cliente=self,
            gerente=self.gerente,
            modelo=modelo,
            justificativa=justificativa,
        )

    def transferir_para(self, destino, valor, descricao=""):
        if not isinstance(destino, Cliente):
            raise ValidationError("Destino inválido para transferência.")

        if self.pk == destino.pk:
            raise ValidationError("Não é possível transferir para a mesma conta.")

        try:
            valor_decimal = Decimal(valor)
        except (TypeError, ValueError, InvalidOperation):
            raise ValidationError("Informe um valor numérico válido.")

        if valor_decimal <= 0:
            raise ValidationError("O valor da transferência deve ser maior que zero.")

        valor_decimal = valor_decimal.quantize(Decimal("0.01"))

        descricao = (descricao or "").strip()

        with transaction.atomic():
            remetente = Cliente.objects.select_for_update().get(pk=self.pk)
            destinatario = Cliente.objects.select_for_update().get(pk=destino.pk)

            if remetente.saldo < valor_decimal:
                raise ValidationError("Saldo insuficiente para realizar a transferência.")

            remetente.saldo -= valor_decimal
            destinatario.saldo += valor_decimal

            remetente.save(update_fields=["saldo"])
            destinatario.save(update_fields=["saldo"])

            descricao_saida = descricao or (
                f"Transferência para conta {destinatario.usuario.agencia}-"
                f"{destinatario.usuario.conta}"
            )
            descricao_entrada = descricao or (
                f"Transferência recebida de conta {remetente.usuario.agencia}-"
                f"{remetente.usuario.conta}"
            )

            transacao_saida = Transacao.objects.create(
                cliente=remetente,
                valor=valor_decimal,
                tipo=Transacao.Tipo.SAIDA,
                descricao=descricao_saida,
                saldo_resultante=remetente.saldo,
                contraparte=destinatario,
            )

            transacao_entrada = Transacao.objects.create(
                cliente=destinatario,
                valor=valor_decimal,
                tipo=Transacao.Tipo.ENTRADA,
                descricao=descricao_entrada,
                saldo_resultante=destinatario.saldo,
                contraparte=remetente,
            )

            transferencia = Transferencia.objects.create(
                origem=remetente,
                destino=destinatario,
                valor=valor_decimal,
                descricao=descricao,
                status=Transferencia.Status.CONCLUIDA,
                processada_em=timezone.now(),
                transacao_origem=transacao_saida,
                transacao_destino=transacao_entrada,
            )

            transacao_saida.transferencia = transferencia
            transacao_saida.save(update_fields=["transferencia"])

            transacao_entrada.transferencia = transferencia
            transacao_entrada.save(update_fields=["transferencia"])

            return transferencia


class Cartao(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    modelo = models.ForeignKey('ModeloCartao', on_delete=models.PROTECT, null=True, blank=True, related_name='cartoes_emitidos')
    numero = models.CharField(max_length=16, unique=True)
    validade = models.DateField()
    codigo_seguranca = models.CharField(max_length=4)
    limite = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        sufixo = self.numero[-4:] if self.numero else "????"
        referencia = f" {self.modelo.nome}" if self.modelo else ""
        return f"Cartão{referencia} {sufixo} - {self.cliente.usuario.nome}"


class ModeloCartao(models.Model):
    nome = models.CharField(max_length=80, unique=True)
    descricao = models.TextField(blank=True)
    limite_minimo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    limite_maximo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['limite_minimo', 'nome']

    def __str__(self):
        return self.nome


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
    class Tipo(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='transacoes')
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True)
    saldo_resultante = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    contraparte = models.ForeignKey(
        'Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes_como_contraparte'
    )
    transferencia = models.ForeignKey(
        'Transferencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacoes'
    )

    class Meta:
        ordering = ['-data']

    def __str__(self):
        sinal = '+' if self.tipo == self.Tipo.ENTRADA else '-'
        return f"{sinal} {self.valor} ({self.cliente.usuario.nome})"


class Transferencia(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        CONCLUIDA = 'concluida', 'Concluída'
        CANCELADA = 'cancelada', 'Cancelada'

    origem = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='transferencias_enviadas'
    )
    destino = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='transferencias_recebidas'
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    descricao = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    criada_em = models.DateTimeField(auto_now_add=True)
    processada_em = models.DateTimeField(null=True, blank=True)
    transacao_origem = models.OneToOneField(
        'Transacao',
        on_delete=models.PROTECT,
        related_name='transferencia_saida'
    )
    transacao_destino = models.OneToOneField(
        'Transacao',
        on_delete=models.PROTECT,
        related_name='transferencia_entrada'
    )

    class Meta:
        ordering = ['-criada_em']

    def concluir(self):
        self.status = self.Status.CONCLUIDA
        self.processada_em = timezone.now()
        self.save(update_fields=['status', 'processada_em'])

    def __str__(self):
        return (
            f"Transferência de {self.origem.usuario.conta} para {self.destino.usuario.conta} "
            f"no valor de {self.valor}"
        )


class SolicitacaoCredito(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADO = 'aprovado', 'Aprovado'
        NEGADO = 'negado', 'Negado'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitacoes_credito')
    gerente = models.ForeignKey(Gerente, on_delete=models.PROTECT, related_name='analises_credito')
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    motivo = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    resposta = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']

    def aprovar(self, gerente, resposta=""):
        if self.status != self.Status.PENDENTE:
            raise ValidationError("Solicitação já foi analisada.")
        if gerente.pk != self.gerente.pk:
            raise ValidationError("Gerente inválido para aprovação.")

        self.status = self.Status.APROVADO
        self.resposta = (resposta or "").strip()
        self.respondido_em = timezone.now()
        self.save(update_fields=['status', 'resposta', 'respondido_em'])

    def negar(self, gerente, resposta=""):
        if self.status != self.Status.PENDENTE:
            raise ValidationError("Solicitação já foi analisada.")
        if gerente.pk != self.gerente.pk:
            raise ValidationError("Gerente inválido para reprovação.")

        self.status = self.Status.NEGADO
        self.resposta = (resposta or "").strip()
        self.respondido_em = timezone.now()
        self.save(update_fields=['status', 'resposta', 'respondido_em'])

    def __str__(self):
        return f"Crédito {self.valor} - {self.cliente.usuario.nome} ({self.get_status_display()})"


class PedidoCartao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        APROVADO = 'aprovado', 'Aprovado'
        NEGADO = 'negado', 'Negado'

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos_cartao')
    gerente = models.ForeignKey(Gerente, on_delete=models.PROTECT, related_name='pedidos_cartao', null=True, blank=True)
    modelo = models.ForeignKey(ModeloCartao, on_delete=models.PROTECT, related_name='pedidos')
    justificativa = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE)
    observacao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(null=True, blank=True)
    cartao_emitido = models.OneToOneField(Cartao, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedido_origem')

    class Meta:
        ordering = ['-criado_em']

    def aprovar(self, gerente, observacao=""):
        if self.status != self.Status.PENDENTE:
            raise ValidationError("Pedido já foi analisado.")
        if gerente.pk != self.gerente.pk:
            raise ValidationError("Gerente inválido para aprovação.")

        limite_cliente = self.cliente.limite_credito
        limite_cartao = limite_cliente
        if self.modelo.limite_maximo is not None:
            limite_cartao = min(limite_cartao, self.modelo.limite_maximo)

        numero = self._gerar_numero_cartao_unico()
        validade = (timezone.now() + timedelta(days=365 * 4)).date()
        codigo = f"{secrets.randbelow(1000):03d}"

        cartao = Cartao.objects.create(
            cliente=self.cliente,
            modelo=self.modelo,
            numero=numero,
            validade=validade,
            codigo_seguranca=codigo,
            limite=limite_cartao,
        )

        self.status = self.Status.APROVADO
        self.observacao = (observacao or "").strip()
        self.respondido_em = timezone.now()
        self.cartao_emitido = cartao
        self.save(update_fields=['status', 'observacao', 'respondido_em', 'cartao_emitido'])

        return cartao

    def negar(self, gerente, observacao=""):
        if self.status != self.Status.PENDENTE:
            raise ValidationError("Pedido já foi analisado.")
        if gerente.pk != self.gerente.pk:
            raise ValidationError("Gerente inválido para reprovação.")

        self.status = self.Status.NEGADO
        self.observacao = (observacao or "").strip()
        self.respondido_em = timezone.now()
        self.save(update_fields=['status', 'observacao', 'respondido_em'])

    @staticmethod
    def _gerar_numero_cartao_unico():
        while True:
            numero = ''.join(str(secrets.randbelow(10)) for _ in range(16))
            if not Cartao.objects.filter(numero=numero).exists():
                return numero

    def __str__(self):
        return f"Pedido de cartão {self.modelo.nome} - {self.cliente.usuario.nome} ({self.get_status_display()})"


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
