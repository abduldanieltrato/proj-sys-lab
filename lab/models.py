from django.db import models
from django.conf import settings


# -------------------- Paciente -------------------- #
class Paciente(models.Model):
	nome = models.CharField(max_length=255)
	data_nascimento = models.DateField(null=True, blank=True)
	genero = models.CharField(
		max_length=32,
		choices=[
			('M', 'Masculino'),
			('F', 'Feminino'),
			('O', 'Outro'),
		]
	)
	telefone = models.CharField(max_length=32, blank=True)
	residencia = models.CharField(max_length=255, blank=True)
	proveniencia = models.CharField(max_length=128, blank=True)  # Urgência, Pediatria, etc.
	nacionalidade = models.CharField(max_length=64, blank=True)
	numero_identificacao = models.CharField(max_length=64, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.nome} — {self.numero_identificacao}"


# -------------------- Exame -------------------- #
class Exame(models.Model):
	nome = models.CharField(max_length=255)
	descricao = models.TextField(blank=True)
	valor_referencia = models.CharField(max_length=64, blank=True)  # Ex: 4.5 – 6.0
	unidade = models.CharField(max_length=32, blank=True)
	trl_horas = models.PositiveIntegerField(default=24)  # Tempo de resposta laboratorial
	ativo = models.BooleanField(default=True)

	class Meta:
		ordering = ['nome']

	def __str__(self):
		return self.nome


# -------------------- Requisição de Análises -------------------- #
class RequisicaoAnalise(models.Model):
	paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
	exames = models.ManyToManyField('Exame', through='ItemRequisicao', blank=True)
	data_solicitacao = models.DateTimeField(auto_now_add=True)
	analista = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL
	)
	observacoes = models.TextField(blank=True)

	def __str__(self):
		return f"Req - #{self.id} — {self.paciente.nome}"


# -------------------- Item da Requisição -------------------- #
class ItemRequisicao(models.Model):
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE)
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE)

	def __str__(self):
		return f"{self.requisicao} | {self.exame}"


# -------------------- Resultado -------------------- #
class Resultado(models.Model):
	requisicao = models.ForeignKey(
		RequisicaoAnalise,
		on_delete=models.CASCADE,
		related_name='resultados'
	)
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE)
	valor = models.CharField(max_length=128, blank=True)
	unidade = models.CharField(max_length=32, blank=True)
	valor_referencia = models.CharField(max_length=64, blank=True)
	inserido_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		related_name='resultados_inseridos',
		on_delete=models.SET_NULL
	)
	data_insercao = models.DateTimeField(auto_now=True)
	validado = models.BooleanField(default=False)
	validado_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		related_name='resultados_validados',
		on_delete=models.SET_NULL
	)
	data_validacao = models.DateTimeField(null=True, blank=True)

	class Meta:
		unique_together = (('requisicao', 'exame'),)

	def __str__(self):
		return f"Resultado: {self.requisicao} - {self.exame}"
