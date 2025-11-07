"""
models.py - Modelos centrais do sistema AnaBioLink
Autor: Abdul Daniel Trato
Versão: 4.0
Descrição: Estrutura de dados principal para gestão laboratorial. Inclui:
- Pacientes
- Exames e campos de resultados
- Requisições de análises
- Resultados
- Histórico de operações
Implementa herança de valores de referência para evitar duplicidade e métodos claros para manipulação de dados.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

# =====================================
# UTILITÁRIOS
# =====================================
def get_user_model_instance():
	"""
	Retorna o modelo de usuário do Django.
	"""
	return get_user_model()

User = get_user_model_instance()


# =====================================
# PACIENTE
# =====================================
class Paciente(models.Model):
	"""
	Modelo que representa um paciente atendido no laboratório.
	"""

	class Proveniencia(models.TextChoices):
		AMBULATORIO = "Ambulatório", "Ambulatório"
		CLINICA_EXTERNA = "Clínica Externa", "Clínica Externa"
		MEDICINA_OCUPACIONAL = "Medicina Ocupacional", "Medicina Ocupacional"
		MATERNIDADE = "Maternidade", "Maternidade"
		GINECOLOGIA = "Ginecologia", "Ginecologia"
		PEDIATRIA = "Pediatria", "Pediatria"
		BANCO_DE_SOCORROS = "Banco de Socorros", "Banco de Socorros"
		CONSULTA_EXTERNA = "Consulta Externa", "Consulta Externa"
		UROLOGIA = "Urologia", "Urologia"
		CIRURGIA = "Cirurgia", "Cirurgia"
		DENTARIA = "Dentária", "Dentária"
		OFTALMOLOGIA = "Oftalmologia", "Oftalmologia"
		OUTRO = "Outro", "Outro"

	nome = models.CharField("Nome completo", max_length=120)
	numero_id = models.CharField("Número de Documento", max_length=50, unique=True)
	data_nascimento = models.DateField("Data de nascimento", null=True, blank=True)
	genero = models.CharField("Gênero", max_length=10, choices=[("M","Masculino"),("F","Feminino")], blank=True)
	contacto = models.CharField("Contacto", max_length=30, blank=True)
	proveniencia = models.CharField("Proveniência", max_length=50, choices=Proveniencia.choices, default=Proveniencia.OUTRO, blank=True)
	data_registo = models.DateTimeField("Data de registo", auto_now_add=True)

	class Meta:
		verbose_name = "Paciente"
		verbose_name_plural = "Pacientes"
		ordering = ["nome"]

	def __str__(self):
		return f"{self.nome} ({self.numero_id})"

	def idade(self):
		"""
		Retorna a idade em anos, meses ou dias:
		- >=2 anos: anos
		- >=2 meses: meses
		- <2 meses: dias
		"""
		if not self.data_nascimento:
			return "—"
		hoje = date.today()
		delta = hoje - self.data_nascimento
		anos = int(delta.days / 365.25)
		if anos >= 2:
			return f"{anos} anos"
		meses = int(delta.days / 30.44)
		if meses >= 2:
			return f"{meses} meses"
		return f"{delta.days} dias"


# =====================================
# EXAME
# =====================================
class Exame(models.Model):
	"""
	Catálogo de exames disponíveis no laboratório.
	"""

	class MetodoExame(models.TextChoices):
		ENZIMATICO = "Enzimático", "Enzimático"
		ENZIMATICO_HIBRIDO = "Enzimático-Híbrido", "Enzimático-Híbrido"
		COLORIMETRICO = "Colorimétrico", "Colorimétrico"
		ESPECTROFOTOMETRICO = "Espectrofotométrico", "Espectrofotométrico"
		CROMATOGRAFICO = "Cromatográfico", "Cromatográfico"
		CROMATOGRAFICO_ACOPLADO = "Cromatográfico Acoplado", "Cromatográfico Acoplado (ex: LC-MS/MS)"
		MICROSCOPICO = "Microscópico", "Microscópico"
		SEPARACAO_FISICOQUIMICA = "Separação Físico-Química", "Separação Físico-Química"
		CULTURA = "Cultura", "Cultura"
		COPROCULTURA = "Coprocultura", "Coprocultura"
		UROCULTURA = "Urocultura", "Urocultura"
		IMUNOLOGICO = "Imunológico", "Imunológico"
		ELISA = "ELISA", "ELISA"
		PCR = "PCR / Reação em Cadeia da Polimerase", "PCR / Reação em Cadeia da Polimerase"
		OUTRO = "Outro", "Outro"

	class SetorExame(models.TextChoices):
		HEMATOLOGIA = "Hematologia", "Hematologia"
		BIOQUIMICA = "Bioquímica", "Bioquímica"
		MICROBIOLOGIA = "Microbiologia", "Microbiologia"
		IMUNOLOGIA = "Imunologia", "Imunologia"
		PARASITOLOGIA = "Parasitologia", "Parasitologia"
		OUTRO = "Outro", "Outro"

	nome = models.CharField("Nome do exame", max_length=100, unique=True)
	codigo = models.CharField("Código", max_length=20, unique=True)
	trl_horas = models.PositiveIntegerField("Tempo de resposta (h)", default=24)
	metodo = models.CharField("Método", max_length=40, choices=MetodoExame.choices, default=MetodoExame.OUTRO)
	setor = models.CharField("Setor", max_length=40, choices=SetorExame.choices, default=SetorExame.OUTRO)
	activo = models.BooleanField("Ativo", default=True)
	criado_em = models.DateTimeField("Criado em", auto_now_add=True)

	class Meta:
		verbose_name = "Exame"
		verbose_name_plural = "Exames"
		ordering = ["nome"]

	def __str__(self):
		return self.nome


# =====================================
# CAMPO DE EXAME (HERDA VALOR DE REFERÊNCIA)
# =====================================
class ExameCampo(models.Model):
	"""
	Campos configuráveis para cada exame.
	Herda unidade e valor de referência para padronizar resultados.
	"""
	TIPO_RESULTADO = [
		("NUM","Numérico"),
		("TXT","Texto"),
		("PRC","Percentagem"),
		("CHC","Escolha"),
	]

	exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name="campos")
	nome_campo = models.CharField("Campo", max_length=80)
	tipo = models.CharField("Tipo", max_length=3, choices=TIPO_RESULTADO, default="TXT")
	unidade = models.CharField("Unidade", max_length=20, blank=True)
	valor_referencia = models.CharField("Valor de referência", max_length=80, blank=True)
	ordem = models.PositiveIntegerField("Ordem", default=1)

	class Meta:
		verbose_name = "Campo de Exame"
		verbose_name_plural = "Campos de Exame"
		ordering = ["exame","ordem"]

	def __str__(self):
		return f"{self.exame.nome} → {self.nome_campo}"


# =====================================
# REQUISIÇÃO DE ANÁLISES
# =====================================
class RequisicaoAnalise(models.Model):
	"""
	Requisição de exames para um paciente.
	Cada requisição gera automaticamente Resultados vinculados aos campos dos exames.
	"""
	STATUS = [
		("PEND","Pendente"),
		("PROC","Em processamento"),
		("CONC","Concluída"),
		("VAL","Validada"),
	]

	paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="requisicoes")
	exames = models.ManyToManyField(Exame, related_name="requisicoes")
	analista = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Analista responsável")
	observacoes = models.TextField("Observações", blank=True)
	status = models.CharField("Estado", max_length=10, choices=STATUS, default="PEND")
	created_at = models.DateTimeField("Criada em", auto_now_add=True)
	updated_at = models.DateTimeField("Atualizada em", auto_now=True)

	class Meta:
		verbose_name = "Requisição"
		verbose_name_plural = "Requisições"
		ordering = ["-created_at"]

	def __str__(self):
		return f"Req #{self.id} - {self.paciente.nome}"

	def criar_resultados_automaticos(self):
		"""
		Gera resultados vinculados a todos os campos dos exames desta requisição.
		"""
		for exame in self.exames.all():
			for campo in exame.campos.all():
				ResultadoItem.objects.get_or_create(
					requisicao=self,
					exame_campo=campo,
					defaults={
						'unidade': campo.unidade,
						'valor_referencia': campo.valor_referencia,
					}
				)

	def marcar_concluida(self):
		self.status = "CONC"
		self.save()

	def marcar_validada(self):
		self.status = "VAL"
		self.save()


# =====================================
# RESULTADO DE EXAME
# =====================================
class ResultadoItem(models.Model):
	"""
	Resultado individual de um campo de um exame em uma requisição.
	"""

	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name="resultados")
	exame_campo = models.ForeignKey(ExameCampo, on_delete=models.CASCADE, related_name="resultados")
	resultado = models.CharField("Resultado", max_length=120, blank=True)
	validado = models.BooleanField("Validado", default=False)
	validado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="validacoes_resultado")
	data_validacao = models.DateTimeField("Data de validação", null=True, blank=True)
	unidade = models.CharField("Unidade", max_length=20, blank=True)
	valor_referencia = models.CharField("Valor de referência", max_length=80, blank=True)

	class Meta:
		verbose_name = "Resultado"
		verbose_name_plural = "Resultados"
		ordering = ["requisicao","exame_campo"]

	def __str__(self):
		return f"{self.requisicao} → {self.exame_campo.nome_campo}"

	def validar(self, usuario):
		"""
		Marca o resultado como validado e registra o usuário.
		"""
		self.validado = True
		self.validado_por = usuario
		self.data_validacao = timezone.now()
		self.save()


# =====================================
# HISTÓRICO DE OPERAÇÕES
# =====================================
class HistoricoOperacao(models.Model):
	"""
	Registo de todas as operações realizadas em requisições ou resultados.
	"""
	utilizador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name="historico")
	acao = models.CharField("Ação", max_length=120)
	detalhes = models.TextField("Detalhes", blank=True)
	data = models.DateTimeField("Data", auto_now_add=True)

	class Meta:
		verbose_name = "Histórico"
		verbose_name_plural = "Histórico de operações"
		ordering = ["-data"]

	def __str__(self):
		return f"{self.data.strftime('%d/%m/%Y %H:%M')} - {self.acao}"
