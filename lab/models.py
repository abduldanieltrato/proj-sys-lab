from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone

# ==========================================================
# -------------------- PACIENTE ----------------------------
# ==========================================================

from datetime import date
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField


class Paciente(models.Model):

	# -------------------- PROVENIÊNCIA --------------------
	class Proveniencia(models.TextChoices):
		SUR = 'Serviço de Urgência de Reanimação', 'Serviço de Urgência de Reanimação'
		PED = 'Pediatria', 'Pediatria'
		CIR = 'Cirurgia', 'Cirurgia'
		GIN = 'Ginecologia', 'Ginecologia'
		OBST = 'Obstetricia', 'Obstetricia'
		UROL = 'Urologia', 'Urologia'
		MED_I = 'Medicina Homem', 'Medicina Homem'
		MED_II = 'Medicina Mulher', 'Medicina Mulher'
		OFT = 'Oftalmologia', 'Oftalmologia'
		C_EXT = 'Consulta Externa', 'Consulta Externa'
		DENT = 'Dentisteria', 'Dentisteria'
		LAB = 'Laboratório', 'Laboratório'
		RADIO = 'Radiologia', 'Radiologia'
		OUT = 'Outros', 'Outros'

	# -------------------- CAMPOS PRINCIPAIS --------------------
	nid = models.CharField(
		primary_key=True,
		max_length=12,
		editable=False,
		verbose_name='NID',
		help_text='Número de Identificação do Paciente',
		unique=True
	)
	nome = models.CharField(
		max_length=255,
		verbose_name='Nome',
		help_text='Nome completo do paciente'
	)
	email = models.EmailField(
		blank=True,
		verbose_name='Email',
		help_text='Endereço de email do paciente'
	)
	data_nascimento = models.DateField(
		null=True,
		blank=True,
		verbose_name='Data de Nascimento',
		help_text='Data de nascimento do paciente'
	)
	genero = models.CharField(
		max_length=32,
		choices=[('M', 'Masculino'), ('F', 'Feminino')],
		verbose_name='Sexo',
		blank=True,
		null=True,
		help_text='Gênero do paciente'
	)
	telefone = PhoneNumberField(
		region='MZ',
		blank=True,
		null=True,
		verbose_name='Telefone',
		help_text='Número de telefone do paciente'
	)
	residencia = models.CharField(
		max_length=255,
		blank=True,
		verbose_name='Residência',
		help_text='Endereço de residência do paciente'
	)
	proveniencia = models.CharField(
		max_length=128,
		blank=True,
		choices=Proveniencia.choices,
		default=Proveniencia.PED,
		verbose_name='Proveniência',
		help_text='Unidade de proveniência do paciente'
	)
	nacionalidade = CountryField(
		blank=True,
		null=True,
		default='MZ',
		verbose_name='Nacionalidade',
		help_text='Nacionalidade do paciente'
	)
	numero_id = models.CharField(
		max_length=64,
		unique=True,
		verbose_name='Identidade', 
        help_text='Número do documento de identidade do paciente: B.I., Passaporte, etc.',
        blank=True,
	)
	historico_medico = models.TextField(
		blank=True,
		null=True,
		verbose_name='Histórico Médico',
        help_text='Histórico médico relevante do paciente'
	)
	created_at = models.DateTimeField(
		auto_now_add=True,
		verbose_name='Entrada',
		help_text='Data e hora de entrada do registo do paciente'
	)

	# -------------------- MÉTODOS DE MODELO --------------------
	def save(self, *args, **kwargs):
		if not self.nid:
			hoje_str = date.today().strftime("%Y%m%d")
			contador = Paciente.objects.filter(created_at__date=date.today()).count() + 1
			self.nid = f"{hoje_str}{contador:04d}"
		super().save(*args, **kwargs)

	@property
	def idade(self):
		if not self.data_nascimento:
			return None
		hoje = date.today()
		idade = hoje.year - self.data_nascimento.year
		if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
			idade -= 1
		return idade

	def idade_display(self):
		if self.idade is None:
			return "—"

		if self.idade < 2:
			hoje = date.today()
			dias_totais = (hoje - self.data_nascimento).days
			anos = dias_totais // 365
			meses = (dias_totais % 365) // 30
			dias = dias_totais % 30

			if anos > 0:
				return f"{anos} ano{'s' if anos > 1 else ''}, {meses} mês{'es' if meses != 1 else ''} e {dias} dia{'s' if dias != 1 else ''}"
			elif meses > 0:
				return f"{meses} mês{'es' if meses != 1 else ''} e {dias} dia{'s' if dias != 1 else ''}"
			else:
				return f"{dias} dia{'s' if dias != 1 else ''}"

		return f"{self.idade} ano{'s' if self.idade > 1 else ''}"

	idade_display.short_description = "Idade"

	def data_entrada(self):
		return self.created_at.strftime("%d/%m/%Y") if self.created_at else "—"

	data_entrada.short_description = "Entrada"

	def __str__(self):
		return f"{self.nome} ({self.nid})"

	# -------------------- META --------------------
	class Meta:
		verbose_name = "Paciente"
		verbose_name_plural = "Pacientes"
		ordering = ['-created_at']


# ==========================================================
# -------------------- DESIGNACAO --------------------------
# ==========================================================
class Designacao(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Designação")
    descricao = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Designação"
        verbose_name_plural = "Designações"
        ordering = ['nome']

    def __str__(self):
        return self.nome

# ==========================================================
# -------------------- METODO ------------------------------
# ==========================================================
class Metodo(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Método")
    class Meta:
        verbose_name = "Método"
        verbose_name_plural = "Métodos"
        ordering = ['nome']
    def __str__(self):
        return self.nome

# ==========================================================
# -------------------- EXAME -------------------------------
# ==========================================================
class Exame(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Exame')
    descricao = models.TextField(blank=True, help_text="Descrição do exame", verbose_name='Descrição')
    valor_ref = models.CharField(max_length=64, blank=True, verbose_name='Referência')
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidades')
    trl_horas = models.PositiveIntegerField(default=24, verbose_name='TRL (horas)')
    designacao = models.ForeignKey(
        Designacao,
        on_delete=models.PROTECT,
        related_name="exames",
        verbose_name="Sector de Análise",
        help_text="Sector de análise ao qual o exame pertence"
    )
    metodo = models.ForeignKey(
        Metodo,
        on_delete=models.PROTECT,
        related_name="exames",
        verbose_name="Método",
        blank=True,
        null=True, 
        help_text="Método utilizado para realizar o exame, exemplo: Enzimático, Colorimétrico, etc."
    )
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames Disponíveis no Laboratório"
        ordering = ['designacao__nome', 'nome']
    def __str__(self):
        if self.metodo:
            return f"{self.nome} ({self.designacao} - {self.metodo})"
        return f"{self.nome} ({self.designacao})"
    def display_valor_ref(self):
        return self.valor_ref or "—"
    display_valor_ref.short_description = "Valor de referência"
    def tempo_resposta_display(self):
        return f"{self.trl_horas} hora{'s' if self.trl_horas != 1 else ''}"
    tempo_resposta_display.short_description = "TRL"

# ==========================================================
# -------------------- REQUISIÇÃO DE ANÁLISES --------------
# ==========================================================
class RequisicaoAnalise(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, verbose_name="Paciente", related_name='requisicoes', help_text="Paciente ao qual a requisição pertence")
    exames = models.ManyToManyField('Exame', through='ItemRequisicao', blank=True, verbose_name='Exames requisitados', help_text='Exames incluídos nesta requisição', related_name='requisicoes')
    analista = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Técnico de Laboratório', help_text='Técnico de laboratório que criou a requisição', related_name='requisicoes_criadas')
    observacoes = models.TextField(blank=True, verbose_name="Observações adicionais", help_text="Observações adicionais sobre a requisição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em', help_text='Data e hora de criação da requisição', db_index=True)

    @property
    def exames_list(self):
        return Exame.objects.filter(itemrequisicao__requisicao=self)

    @property
    def exames_count(self):
        return self.exames_list.count()

    def exames_summary(self):
        names = list(self.exames_list.values_list('nome', flat=True))
        count = self.exames_count
        if not names:
            return "—"
        summary = ", ".join(names)
        return f"{summary} ({count} exame{'s' if count != 1 else ''})"
    exames_summary.short_description = "Exames requisitados"

    def observacoes_short(self):
        return (self.observacoes[:80] + '…') if self.observacoes and len(self.observacoes) > 80 else (self.observacoes or "—")
    observacoes_short.short_description = "Observações"

    def __str__(self):
        return f"Req - #{self.paciente.nid} — {self.paciente.nome}"

    class Meta:
        verbose_name = "Requisição de Análises"
        verbose_name_plural = "Requisições de Análises"
        ordering = ['-created_at']

# ==========================================================
# -------------------- ITEM REQUISIÇÃO ---------------------
# ==========================================================
class ItemRequisicao(models.Model):
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, verbose_name='Requisição', related_name='itens', help_text='Requisição à qual este item pertence')
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame', help_text='Exame incluído nesta requisição', related_name='itens_requisicao')

    def __str__(self):
        return f"{self.requisicao} | {self.exame}"

    class Meta:
        verbose_name = "Item de Requisição"
        verbose_name_plural = "Itens de Requisições"

# ==========================================================
# -------------------- RESULTADO ---------------------------
# ==========================================================
class Resultado(models.Model):
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name='resultados', verbose_name='Requisição', help_text='Requisição à qual este resultado pertence', db_index=True)
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame', help_text='Exame ao qual este resultado pertence', db_index=True)
    resultado = models.TextField(null=True, blank=True, verbose_name="Resultado", help_text="Valor do resultado do exame, observações ou interpretação")
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidade', help_text='Unidade de medida do resultado')
    valor_referencia = models.CharField(max_length=64, blank=True, verbose_name='Valor de referência', help_text='Valor de referência do exame')
    data_insercao = models.DateTimeField(auto_now=True, verbose_name='Data de inserção', help_text='Data e hora de inserção do resultado')
    validado = models.BooleanField(default=False, verbose_name='Validado', help_text='Indica se o resultado foi validado')
    validado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='resultados_validados', on_delete=models.SET_NULL, verbose_name='Validado por', help_text='Usuário que validou o resultado')
    data_validacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de validação', help_text='Data e hora da validação do resultado')

    class Meta:
        verbose_name = "Resultado de Exame"
        verbose_name_plural = "Resultados de Exames"
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

# ==========================================================
# -------------------- Campos dinâmicos por exame ----------
# ==========================================================
class ExameCampoResultado(models.Model):
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name='campos', verbose_name='Exame', help_text='Exame ao qual este campo pertence', db_index=True)
    nome_campo = models.CharField(max_length=255, verbose_name='Nome do campo', help_text='Nome do campo de resultado do exame', db_index=True, unique=True)
    tipo_campo = models.CharField(max_length=50, choices=[('text', 'Texto'), ('number', 'Número'), ('bool', 'Sim/Não'), ('date', 'Data'), ('datetime', 'Data/Hora'), ('percent', 'Porcentagem')], verbose_name='Tipo de campo', help_text='Tipo de dado do campo de resultado')
    obrigatorio = models.BooleanField(default=True, verbose_name='Obrigatório', help_text='Indica se o campo é obrigatório')

    def __str__(self):
        return f"{self.exame.nome} | {self.nome_campo}"

# ==========================================================
# -------------------- ResultadoItem -----------------------
# ==========================================================
class ResultadoItem(models.Model):
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name='resultado_items', verbose_name='Requisição', help_text='Requisição à qual este resultado item pertence', db_index=True)
    exame_campo = models.ForeignKey(ExameCampoResultado, on_delete=models.CASCADE, verbose_name='Campo do exame', help_text='Campo de resultado do exame', db_index=True)
    resultado = models.CharField(max_length=128, blank=True, verbose_name='Resultado', help_text='Valor do resultado do campo do exame', db_index=True)
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidade', help_text='Unidade de medida do resultado')
    valor_referencia = models.CharField(max_length=64, blank=True, verbose_name='Valor de referência', help_text='Valor de referência do campo do exame')

    class Meta:
        verbose_name = "Item de Resultado de Exame"
        verbose_name_plural = "Itens de Resultados de Exames"
        ordering = ['requisicao', 'exame_campo']

    def save(self, *args, **kwargs):
        if self.exame_campo and self.exame_campo.exame:
            self.unidade = self.exame_campo.exame.unidade or self.unidade
            self.valor_referencia = self.exame_campo.exame.valor_ref or self.valor_referencia
        super().save(*args, **kwargs)

    def __str__(self):
        # retorno string legível
        return f"{self.requisicao} | {self.exame_campo.exame.nome} | {self.exame_campo.nome_campo}"