from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone

# -------------------- Paciente -----------------------------
class Paciente(models.Model):
	id = models.BigIntegerField(primary_key=True, verbose_name='NID')
	nome = models.CharField(max_length=255, verbose_name='Nome')
	data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de nascimento')
	genero = models.CharField(max_length=32, choices=[('M', 'Masculino'), ('F', 'Feminino')], verbose_name='Sexo')
	telefone = models.CharField(max_length=32, blank=True, verbose_name='Telefone')
	residencia = models.CharField(max_length=255, blank=True, verbose_name='Residência')
	proveniencia = models.CharField(max_length=128, blank=True, verbose_name='Proveniência')
	nacionalidade = models.CharField(max_length=64, blank=True, verbose_name='Nacionalidade')
	numero_id = models.CharField(max_length=64, unique=True, verbose_name='Identidade')
	historico_medico = models.TextField(blank=True, null=True, verbose_name='Histórico')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Entrada')

	class Meta:
		verbose_name = "Paciente"
		verbose_name_plural = "Pacientes"
		ordering = ['nome']

	@property
	def idade(self):
		if not self.data_nascimento:
			return None
		hoje = date.today()
		idade_em_anos = hoje.year - self.data_nascimento.year
		if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
			idade_em_anos -= 1
		return idade_em_anos

	def __str__(self):
		idade_display = self.idade_display()
		return f"{self.nome} ({self.numero_id}) - Idade: {idade_display}"

	def idade_display(self):
		if self.idade is None:
			return "—"

		# Menores de 2 anos: exibir detalhe meses/dias
		if self.idade < 2:
			hoje = date.today()
			idade_total_dias = (hoje - self.data_nascimento).days
			idade_em_anos = idade_total_dias // 365
			idade_em_meses = (idade_total_dias % 365) // 30
			idade_em_dias = idade_total_dias % 30

			if idade_em_anos > 0:
				return f"{idade_em_anos} ano{'s' if idade_em_anos > 1 else ''}, {idade_em_meses} mês{'es' if idade_em_meses != 1 else ''} e {idade_em_dias} dia{'s' if idade_em_dias != 1 else ''}"
			elif idade_em_meses > 0:
				return f"{idade_em_meses} mês{'es' if idade_em_meses != 1 else ''} e {idade_em_dias} dia{'s' if idade_em_dias != 1 else ''}"
			else:
				return f"{idade_em_dias} dia{'s' if idade_em_dias != 1 else ''}"

		if self.idade == 1:
			return f"{self.idade} ano"

		return f"{self.idade} anos"

	idade_display.short_description = "Idade"


# -------------------- Exame -------------------------------
class Exame(models.Model):
	id = models.IntegerField(primary_key=True)
	nome = models.CharField(max_length=255, verbose_name='Exames')
	descricao = models.TextField(blank=True, help_text="Descrição", verbose_name='Descrição')
	valor_ref = models.CharField(max_length=64, blank=True, verbose_name='Referência')
	unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidades')
	trl_horas = models.PositiveIntegerField(default=24, verbose_name='TRL(horas)')

	class Meta:
		verbose_name = "Exame"
		verbose_name_plural = "Exames"
		ordering = ['nome']

	def __str__(self):
		return f'#{self.id} - {self.nome}'

	def display_valor_ref(self):
		return self.valor_ref or "—"
	display_valor_ref.short_description = "Valor de referência"

	def tempo_resposta_display(self):
		if self.trl_horas > 1:
			return f'{self.trl_horas} horas'
		else:
			return f"{self.trl_horas} hora"
	tempo_resposta_display.short_description = "TRL"


# -------------------- Requisição de Análises -----------------
class RequisicaoAnalise(models.Model):
	paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
	exames = models.ManyToManyField('Exame', through='ItemRequisicao', blank=True, verbose_name='Exames requisitados')
	analista = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Técnico de Laboratório')
	observacoes = models.TextField(blank=True, verbose_name="Observações adicionais")
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')

	@property
	def exames_list(self):
		return Exame.objects.filter(itemrequisicao__requisicao=self)

	@property
	def exames_count(self):
		return self.exames_list.count()

	def exames_summary(self):
		names = list(self.exames_list.values_list('nome', flat=True)[:5])
		summary = ", ".join(names)
		if self.exames_count > 5:
			summary += " …"
		return summary or "—"
	exames_summary.short_description = "Resumo dos Exames"

	def observacoes_short(self):
		return (self.observacoes[:80] + '…') if self.observacoes and len(self.observacoes) > 80 else (self.observacoes or "—")
	observacoes_short.short_description = "Observações"

	def __str__(self):
		return f"Req - #{self.id} — {self.paciente.nome.upper()} | Exames: {self.exames_summary()}"

	class Meta:
		verbose_name = "Requisição de Análises"
		verbose_name_plural = "Requisições de Análises"
		ordering = ['-id']


# -------------------- Item da Requisição ------------------
class ItemRequisicao(models.Model):
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, verbose_name='Requisição')
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame')

	def __str__(self):
		return f"{self.requisicao} | {self.exame}"

	class Meta:
		verbose_name = "Item de Requisição"
		verbose_name_plural = "Itens de Requisição"


# -------------------- Resultado ---------------------------
class Resultado(models.Model):
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name='resultados', verbose_name='Requisição')
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame')
	resultado = models.TextField(null=True, blank=True, verbose_name="Resultado")
	unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidade')
	valor_referencia = models.CharField(max_length=64, blank=True, verbose_name='Valor de referência')
	data_insercao = models.DateTimeField(auto_now=True, verbose_name='Data de inserção')
	validado = models.BooleanField(default=False, verbose_name='Validado')
	validado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='resultados_validados', on_delete=models.SET_NULL, verbose_name='Validado por')
	data_validacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de validação')

	class Meta:
		verbose_name = "Resultado de Exame"
		verbose_name_plural = "Resultados de Exames"
		unique_together = (('requisicao', 'exame'),)
		ordering = ['requisicao', 'exame']

	def save(self, *args, **kwargs):
		if self.exame:
			if not self.unidade:
				self.unidade = self.exame.unidade
			if not self.valor_referencia:
				self.valor_referencia = self.exame.valor_ref
		if self.validado and not self.data_validacao:
			self.data_validacao = timezone.now()
		super().save(*args, **kwargs)

	def is_valid_display(self):
		return format_html('<b style="color:{};">{}</b>', 'green' if self.validado else 'red', 'Sim' if self.validado else 'Não')
	is_valid_display.short_description = "Validado"

	def formatted_data_insercao(self):
		return self.data_insercao.strftime("%d/%m/%Y %H:%M") if self.data_insercao else "—"
	formatted_data_insercao.short_description = "Inserido em"

	def __str__(self):
		return f"Resultado: {self.requisicao} - {self.exame}"


# -------------------- Campos dinâmicos por exame -----------------
class ExameCampoResultado(models.Model):
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name='campos')
	nome_campo = models.CharField(max_length=255)
	tipo_campo = models.CharField(max_length=50, choices=[('text', 'Texto'), ('number', 'Número'), ('bool', 'Sim/Não')])
	obrigatorio = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.exame.nome} | {self.nome_campo}"


# -------------------- ResultadoItem -------------------------
class ResultadoItem(models.Model):
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name='resultado_items')
	exame_campo = models.ForeignKey(ExameCampoResultado, on_delete=models.CASCADE, verbose_name='Campo do exame')
	resultado = models.CharField(max_length=128, blank=True)
	unidade = models.CharField(max_length=32, blank=True)
	valor_referencia = models.CharField(max_length=64, blank=True)

	def save(self, *args, **kwargs):
		if self.exame_campo and self.exame_campo.exame:
			self.unidade = self.exame_campo.exame.unidade or self.unidade
			self.valor_referencia = self.exame_campo.exame.valor_ref or self.valor_referencia
		super().save(*args, **kwargs)

	def __str__(self):
		# Corrigido: usar campo existente 'resultado' em vez de 'valor'
		return f"{self.exame_campo.exame.nome} | {self.exame_campo.nome_campo} | {self.resultado or '—'}"
