from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Cliente, Transacao, Transferencia, Usuario


class TransferenciaEntreContasTestCase(TestCase):
	def setUp(self):
		self.usuario_origem = Usuario.objects.create(
			nome="Cliente Origem",
			email="origem@example.com",
			senha="senha123",
			conta="12345678",
			agencia="0001",
		)
		self.usuario_destino = Usuario.objects.create(
			nome="Cliente Destino",
			email="destino@example.com",
			senha="senha123",
			conta="87654321",
			agencia="0001",
		)

		self.cliente_origem = Cliente.objects.create(
			usuario=self.usuario_origem,
			saldo=Decimal("1000.00"),
		)
		self.cliente_destino = Cliente.objects.create(
			usuario=self.usuario_destino,
			saldo=Decimal("500.00"),
		)

	def test_transferencia_sucesso(self):
		transferencia = self.cliente_origem.transferir_para(
			destino=self.cliente_destino,
			valor=Decimal("250.00"),
			descricao="Pagamento mensal",
		)

		self.cliente_origem.refresh_from_db()
		self.cliente_destino.refresh_from_db()

		self.assertEqual(self.cliente_origem.saldo, Decimal("750.00"))
		self.assertEqual(self.cliente_destino.saldo, Decimal("750.00"))

		self.assertIsInstance(transferencia, Transferencia)
		self.assertEqual(transferencia.valor, Decimal("250.00"))
		self.assertEqual(transferencia.status, Transferencia.Status.CONCLUIDA)

		transacoes = Transacao.objects.filter(transferencia=transferencia).order_by("tipo")
		self.assertEqual(transacoes.count(), 2)
		tipos = {tx.tipo for tx in transacoes}
		self.assertSetEqual(tipos, {Transacao.Tipo.ENTRADA, Transacao.Tipo.SAIDA})

	def test_transferencia_saldo_insuficiente(self):
		with self.assertRaises(ValidationError):
			self.cliente_origem.transferir_para(
				destino=self.cliente_destino,
				valor=Decimal("2000.00"),
				descricao="Acima do saldo",
			)

	def test_transferencia_mesma_conta_nao_permitida(self):
		with self.assertRaises(ValidationError):
			self.cliente_origem.transferir_para(
				destino=self.cliente_origem,
				valor=Decimal("10.00"),
			)

	def test_deposito_incrementa_saldo_e_gera_transacao(self):
		transacao = self.cliente_origem.depositar(Decimal("300.00"), "Depósito teste")

		self.cliente_origem.refresh_from_db()
		self.assertEqual(self.cliente_origem.saldo, Decimal("1300.00"))
		self.assertEqual(transacao.tipo, Transacao.Tipo.ENTRADA)
		self.assertEqual(transacao.valor, Decimal("300.00"))
		self.assertEqual(transacao.saldo_resultante, Decimal("1300.00"))

	def test_deposito_valor_invalido_dispara_erro(self):
		with self.assertRaises(ValidationError):
			self.cliente_origem.depositar("abc")
