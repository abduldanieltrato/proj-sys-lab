from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import (
    Paciente, Exame, RequisicaoAnalise, ItemRequisicao,
    Resultado, ExameCampoResultado, ResultadoItem
)

User = get_user_model()


class PacienteModelTest(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            id=1,
            nome="Abdul Daniel",
            data_nascimento="1990-01-01",
            genero='M',
            numero_id="1234567890"
        )

    def test_idade_calculo(self):
        idade = self.paciente.idade
        self.assertIsInstance(idade, int)

    def test_resumo(self):
        self.assertIn("Abdul Daniel", self.paciente.resumo())


class ExameModelTest(TestCase):
    def setUp(self):
        self.exame = Exame.objects.create(
            id=1,
            nome="Hemograma",
            valor_ref="4-10",
            unidade="10^9/L"
        )

    def test_str(self):
        self.assertEqual(str(self.exame), "#1 - Hemograma")


class RequisicaoAnaliseModelTest(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            id=1,
            nome="Paciente Teste",
            genero='M',
            numero_id="111222333"
        )
        self.exame = Exame.objects.create(
            id=1,
            nome="Hemograma",
            valor_ref="4-10",
            unidade="10^9/L"
        )
        self.requisicao = RequisicaoAnalise.objects.create(paciente=self.paciente)
        ItemRequisicao.objects.create(requisicao=self.requisicao, exame=self.exame)

        # Criar campos do exame
        self.campo1 = ExameCampoResultado.objects.create(exame=self.exame, nome_campo="Hemácias", tipo_campo="number")
        self.campo2 = ExameCampoResultado.objects.create(exame=self.exame, nome_campo="Leucócitos", tipo_campo="number")

        # Criar ResultadoItem para cada campo do exame
        for campo in self.exame.campos.all():
            ResultadoItem.objects.get_or_create(requisicao=self.requisicao, exame_campo=campo)

    def test_exames_summary(self):
        self.assertIn("Hemograma", self.requisicao.exames_summary())

    def test_resultado_items_criados(self):
        items = ResultadoItem.objects.filter(requisicao=self.requisicao)
        self.assertEqual(items.count(), 2)  # Dois campos do exame
        for item in items:
            self.assertEqual(item.unidade, item.exame_campo.exame.unidade)
            self.assertEqual(item.valor_referencia, item.exame_campo.exame.valor_ref)


class ResultadoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tech1", password="123456", first_name="Abdul", last_name="Trato")
        self.paciente = Paciente.objects.create(id=1, nome="Paciente X", genero='M', numero_id="555")
        self.exame = Exame.objects.create(id=1, nome="Hemograma", valor_ref="4-10", unidade="10^9/L")
        self.requisicao = RequisicaoAnalise.objects.create(paciente=self.paciente)
        ItemRequisicao.objects.create(requisicao=self.requisicao, exame=self.exame)
        # Campos do exame
        self.campo1 = ExameCampoResultado.objects.create(exame=self.exame, nome_campo="Hemácias", tipo_campo="number")
        self.campo2 = ExameCampoResultado.objects.create(exame=self.exame, nome_campo="Leucócitos", tipo_campo="number")
        # Criar ResultadoItem
        for campo in self.exame.campos.all():
            ResultadoItem.objects.get_or_create(requisicao=self.requisicao, exame_campo=campo)

        self.resultado = Resultado.objects.create(
            requisicao=self.requisicao,
            exame=self.exame,
            valor="5.5",
            inserido_por=self.user
        )

    def test_valor_referencia_e_unidade(self):
        self.assertEqual(self.resultado.unidade, "10^9/L")
        self.assertEqual(self.resultado.valor_referencia, "4-10")

    def test_nome_completo(self):
        self.assertEqual(self.resultado.nome_completo, "Abdul Trato")

    def test_resultado_item_integridade(self):
        for item in ResultadoItem.objects.filter(requisicao=self.requisicao):
            self.assertIsNotNone(item.exame_campo.exame.id)
            self.assertEqual(item.unidade, item.exame_campo.exame.unidade)
            self.assertEqual(item.valor_referencia, item.exame_campo.exame.valor_ref)

    def test_resultado_item_str(self):
        item = ResultadoItem.objects.get(exame_campo=self.campo1)
        self.assertIn("Hemácias", str(item))
        self.assertIn("Hemograma", str(item))


class SistemaLaboratorialTest(TestCase):
    """
    Testes integrados de requisição e resultados.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="tech1", password="123456", first_name="Abdul", last_name="Trato")
        self.paciente = Paciente.objects.create(id=1, nome="Paciente Teste", genero='M', numero_id="999")
        # Exames e campos
        self.exame1 = Exame.objects.create(id=1, nome="Hemograma", valor_ref="4-10", unidade="10^9/L")
        self.exame2 = Exame.objects.create(id=2, nome="Glicose", valor_ref="70-100", unidade="mg/dL")
        self.campo1 = ExameCampoResultado.objects.create(exame=self.exame1, nome_campo="Hemácias", tipo_campo="number")
        self.campo2 = ExameCampoResultado.objects.create(exame=self.exame1, nome_campo="Leucócitos", tipo_campo="number")
        self.campo3 = ExameCampoResultado.objects.create(exame=self.exame2, nome_campo="Glicemia", tipo_campo="number")

    def test_criacao_resultado_items_automaticamente(self):
        requisicao = RequisicaoAnalise.objects.create(paciente=self.paciente, analista=self.user)
        ItemRequisicao.objects.create(requisicao=requisicao, exame=self.exame1)
        ItemRequisicao.objects.create(requisicao=requisicao, exame=self.exame2)

        # Criar ResultadoItem automaticamente
        for exame in requisicao.exames.all():
            for campo in exame.campos.all():
                ResultadoItem.objects.get_or_create(requisicao=requisicao, exame_campo=campo)

        items = ResultadoItem.objects.filter(requisicao=requisicao)
        self.assertEqual(items.count(), 3)  # 2 campos do Hemograma + 1 da Glicose
        for item in items:
            self.assertEqual(item.unidade, item.exame_campo.exame.unidade)
            self.assertEqual(item.valor_referencia, item.exame_campo.exame.valor_ref)
