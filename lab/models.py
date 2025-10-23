# ===========================================
# models.py — Sistema de Gestão Laboratorial
# Autor: Trato
# Objetivo: Modelos otimizados (UX + lógica)
# Sem alterações estruturais no DB (no migrations)
# ===========================================

from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html


# ==========================================================
# -------------------- Paciente -----------------------------
# ==========================================================
class Paciente(models.Model):
	"""
	Entidade que representa um paciente atendido no laboratório.
	Contém informações pessoais, de contacto e proveniência clínica.
	"""

	class Proveniencia(models.TextChoices):
		BS = 'BS', 'Banco de Socorros'
		AMB = 'AMB', 'Ambulatório'
		SUR = 'SUR', 'Serviço de Urgência de Reanimação'
		PED = 'PED', 'Pediatria'
		CIR = 'CIR', 'Cirurgia'
		GIN = 'GIN', 'Ginecologia'
		OBST = 'OBST', 'Obstetrícia'
		UROL = 'UROL', 'Urologia'
		MED_I = 'MED_I', 'Medicina Homem'
		MED_II = 'MED_II', 'Medicina Mulher'
		OFT = 'OFT', 'Oftalmologia'
		C_EXT = 'C.EXT', 'Consulta Externa'

	id = models.BigIntegerField(primary_key=True, verbose_name='Número de entrada')
	nome = models.CharField(max_length=255, verbose_name='Nome do paciente')
	data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de nascimento')
	genero = models.CharField(
		max_length=32,
		choices=[('M', 'Masculino'), ('F', 'Feminino')],
		verbose_name='Gênero'
	)
	telefone = models.CharField(max_length=32, blank=True, verbose_name='Número de celular')
	residencia = models.CharField(max_length=255, blank=True, verbose_name='Residência')
	proveniencia = models.CharField(max_length=128, blank=True, verbose_name='Sector de proveniência')
	nacionalidade = models.CharField(max_length=64, blank=True, verbose_name='País de origem')
	numero_id = models.CharField(max_length=64, unique=True, verbose_name='Documento de Identificação')
	historico_medico = models.TextField(blank=True, null=True, verbose_name='Histórico médico')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Horário de entrada')

	# ----------------- Métodos utilitários ----------------- #

	@property
	def idade(self):
		"""Calcula idade com base na data de nascimento."""
		if not self.data_nascimento:
			return None
		hoje = date.today()
		return hoje.year - self.data_nascimento.year - (
			(hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
		)

	def clean(self):
		"""Validação de integridade lógica."""
		if self.data_nascimento and self.data_nascimento > date.today():
			raise ValidationError("A data de nascimento não pode ser no futuro.")

	def resumo(self):
		"""Retorna resumo textual para visualização em admin/templates."""
		return f"{self.nome} ({self.numero_id}) — {self.residencia or 'Local não especificado'}"
	resumo.short_description = "Resumo do Paciente"

	def idade_display(self):
		"""Exibe idade formatada para admin/list_display."""
		return f"{self.idade} anos" if self.idade is not None else "—"
	idade_display.short_description = "Idade"

	def __str__(self):
		"""Representação legível do paciente."""
		idade_txt = f" - Idade: {self.idade} anos" if self.idade else ""
		return f"{self.id} — {self.nome}{idade_txt}"

	class Meta:
		verbose_name = "Paciente"
		verbose_name_plural = "Pacientes"
		ordering = ['nome']


# ==========================================================
# -------------------- Exame -------------------------------
# ==========================================================
class Exame(models.Model):
	"""
	Modela os tipos de exames laboratoriais disponíveis.
	Define nome, descrição, valor de referência e unidade de medida.
	"""

	id = models.IntegerField(primary_key=True)
	nome = models.CharField(max_length=255, verbose_name='Nome do exame')
	descricao = models.TextField(blank=True, help_text="Descrição detalhada do exame", verbose_name='Descrição do exame')
	valor_ref = models.CharField(max_length=64, blank=True, verbose_name='Valor de referência')
	unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidade de medida')
	trl_horas = models.PositiveIntegerField(default=24, verbose_name='Tempo de resposta (horas)')

	class Meta:
		verbose_name = "Exame"
		verbose_name_plural = "Exames"
		ordering = ['nome']

	def __str__(self):
		return f'#{self.id} - {self.nome}'

	def display_valor_ref(self):
		"""Retorna o valor de referência formatado para exibição."""
		return self.valor_ref or "—"
	display_valor_ref.short_description = "Valor de referência"

	def tempo_resposta_display(self):
		"""Apresentação legível do tempo de resposta."""
		return f"{self.trl_horas}h"
	tempo_resposta_display.short_description = "TAT (Turnaround Time)"


# ==========================================================
# -------------------- Requisição de Análises --------------
# ==========================================================
class RequisicaoAnalise(models.Model):
	"""
	Representa uma requisição de análises laboratoriais associada a um paciente.
	Cada requisição pode conter múltiplos exames.
	"""

	paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente")
	exames = models.ManyToManyField('Exame', through='ItemRequisicao', blank=True, verbose_name='Exames requisitados')
	analista = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		verbose_name='Técnico de Laboratório'
	)
	observacoes = models.TextField(blank=True, verbose_name="Observações adicionais")

	# ----------------- Métodos inteligentes ----------------- #

	@property
	def exames_list(self):
		"""Retorna queryset de exames vinculados (via tabela intermediária)."""
		return Exame.objects.filter(itemrequisicao__requisicao=self)

	@property
	def exames_count(self):
		"""Retorna contagem de exames requisitados."""
		return self.exames_list.count()

	def exames_summary(self):
		"""Resumo textual dos exames requisitados (limitado a 5 nomes)."""
		names = list(self.exames_list.values_list('nome', flat=True)[:5])
		summary = ", ".join(names)
		if self.exames_count > 5:
			summary += " …"
		return summary or "—"
	exames_summary.short_description = "Resumo dos Exames"

	def observacoes_short(self):
		"""Trunca observações longas para exibição compacta."""
		return (self.observacoes[:80] + '…') if self.observacoes and len(self.observacoes) > 80 else (self.observacoes or "—")
	observacoes_short.short_description = "Observações"

	def __str__(self):
		return f"Req - #{self.id} — {self.paciente.nome}"

	class Meta:
		verbose_name = "Requisição de Análises"
		verbose_name_plural = "Requisições de Análises"
		ordering = ['-id']


# ==========================================================
# -------------------- Item da Requisição ------------------
# ==========================================================
class ItemRequisicao(models.Model):
	"""
	Tabela intermediária que vincula exames às requisições.
	"""
	requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, verbose_name='Requisição')
	exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame')

	def __str__(self):
		return f"{self.requisicao} | {self.exame}"

	class Meta:
		verbose_name = "Item de Requisição"
		verbose_name_plural = "Itens de Requisição"


# ==========================================================
# -------------------- Resultado ---------------------------
# ==========================================================
from django.db import models
from django.conf import settings
from django.utils.html import format_html
from django.utils import timezone
from .models import RequisicaoAnalise  # ajuste se necessário
from .models import Exame  # ajuste se necessário


class Resultado(models.Model):
    """
    Resultados laboratoriais de cada exame em uma requisição.
    Unidade e valor de referência são preenchidos automaticamente a partir do exame.
    """
    requisicao = models.ForeignKey(
        RequisicaoAnalise,
        on_delete=models.CASCADE,
        related_name='resultados',
        verbose_name='Requisição'
    )
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame')
    resultado = models.TextField(null=True, blank=True)
    valor = models.CharField(max_length=128, blank=True, verbose_name='Resultado analítico')
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidade')
    valor_referencia = models.CharField(max_length=64, blank=True, verbose_name='Valor de referência')
    inserido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='resultados_inseridos',
        on_delete=models.SET_NULL,
        verbose_name='Analista responsável'
    )
    data_insercao = models.DateTimeField(auto_now=True, verbose_name='Data de inserção')
    validado = models.BooleanField(default=False, verbose_name='Validado')
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='resultados_validados',
        on_delete=models.SET_NULL,
        verbose_name='Validado por'
    )
    data_validacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de validação')

    class Meta:
        verbose_name = "Resultado de Exame"
        verbose_name_plural = "Resultados de Exames"
        unique_together = (('requisicao', 'exame'),)
        ordering = ['requisicao', 'exame']

    # ----------------- Métodos auxiliares ----------------- #

    def save(self, *args, **kwargs):
        """Preenche automaticamente unidade e valor de referência do exame"""
        if self.exame:
            if not self.unidade:
                self.unidade = self.exame.unidade
            if not self.valor_referencia:
                self.valor_referencia = self.exame.valor_ref
        # Preenche data de validação se já estiver marcado como validado
        if self.validado and not self.data_validacao:
            self.data_validacao = timezone.now()
        super().save(*args, **kwargs)

    def is_valid_display(self):
        """Indicador visual no admin"""
        return format_html(
            '<b style="color:{};">{}</b>',
            'green' if self.validado else 'red',
            'Sim' if self.validado else 'Não'
        )
    is_valid_display.short_description = "Validado"

    def formatted_data_insercao(self):
        """Data de inserção formatada"""
        return self.data_insercao.strftime("%d/%m/%Y %H:%M") if self.data_insercao else "—"
    formatted_data_insercao.short_description = "Inserido em"

    def __str__(self):
        return f"Resultado: {self.requisicao} - {self.exame}"
