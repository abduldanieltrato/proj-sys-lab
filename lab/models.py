from datetime import date
from django.db import models
from django.conf import settings
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

# ==========================================================
# -------------------- PACIENTE ----------------------------
# ==========================================================
class Paciente(models.Model):
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

    nid = models.CharField(primary_key=True, max_length=12, editable=False, unique=True, verbose_name='NID')
    nome = models.CharField(max_length=255, verbose_name='Nome')
    email = models.EmailField(blank=True, verbose_name='Email')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')
    genero = models.CharField(max_length=32, choices=[('M', 'Masculino'), ('F', 'Feminino')], blank=True, null=True, verbose_name='Sexo')
    telefone = PhoneNumberField(region='MZ', blank=True, null=True, verbose_name='Telefone')
    residencia = models.CharField(max_length=255, blank=True, verbose_name='Residência')
    proveniencia = models.CharField(max_length=128, blank=True, choices=Proveniencia.choices, default=Proveniencia.PED, verbose_name='Proveniência')
    nacionalidade = CountryField(blank=True, null=True, default='MZ', verbose_name='Nacionalidade')
    numero_id = models.CharField(max_length=64, unique=True, blank=True, verbose_name='Identidade')
    historico_medico = models.TextField(blank=True, null=True, verbose_name='Histórico Médico')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Entrada')

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
    descricao = models.TextField(blank=True, verbose_name='Descrição')
    valor_ref = models.CharField(max_length=64, blank=True, verbose_name='Referência')
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidades')
    trl_horas = models.PositiveIntegerField(default=24, verbose_name='TRL (horas)')
    designacao = models.ForeignKey(Designacao, on_delete=models.PROTECT, related_name="exames", verbose_name="Sector de Análise")
    metodo = models.ForeignKey(Metodo, on_delete=models.PROTECT, related_name="exames", blank=True, null=True, verbose_name="Método")

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames Disponíveis"
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
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='requisicoes')
    exames = models.ManyToManyField('Exame', through='ItemRequisicao', blank=True, related_name='requisicoes')
    analista = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='requisicoes_criadas')
    observacoes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @property
    def exames_list(self):
        return Exame.objects.filter(itens_requisicao__requisicao=self)

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
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name='itens')
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name='itens_requisicao')

    def __str__(self):
        return f"{self.requisicao} | {self.exame}"

    class Meta:
        verbose_name = "Item de Requisição"
        verbose_name_plural = "Itens de Requisições"

# ==========================================================
# -------------------- EXAME CAMPO -------------------------
# ==========================================================
class ExameCampoResultado(models.Model):
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name='campos')
    nome_campo = models.CharField(max_length=255)
    tipo_campo = models.CharField(max_length=50, choices=[('text','Texto'),('number','Número'),('choice','Escolha'),('bool','Sim/Não'),('date','Data'),('datetime','Data/Hora'),('percent','Porcentagem')])
    obrigatorio = models.BooleanField(default=False)
    choices = models.TextField(blank=True)
    unidade = models.CharField(max_length=64, blank=True)
    valor_ref = models.CharField(max_length=128, blank=True)

    class Meta:
        unique_together = ('exame', 'nome_campo')
        verbose_name = "Campo do Exame"
        verbose_name_plural = "Campos do Exame"

    def __str__(self):
        return f"{self.exame.nome} | {self.nome_campo}"

# ==========================================================
# -------------------- RESULTADO --------------------------
# ==========================================================
class Resultado(models.Model):
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name="resultados")
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name="resultados")
    resultado = models.CharField(max_length=255, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    validado = models.BooleanField(default=False, verbose_name="Validado")
    validado_por = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    verbose_name="Validado por")
    data_validacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de validação")
    created_at = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("requisicao", "exame")
        verbose_name = "Resultado de Exame"
        verbose_name_plural = "Resultados de Exames"
        ordering = ['requisicao', 'exame']

    def __str__(self):
        return f"{self.exame.nome} - {self.requisicao.paciente.nome}"

    @property
    def unidade(self):
        return self.exame.unidade

    @property
    def valor_referencia(self):
        return self.exame.valor_ref

    def create_missing_result_items(self):
        existing_field_ids = set(self.itens.values_list('exame_campo_id', flat=True))
        to_create = [
            ResultadoItem(resultado=self, exame_campo=campo, unidade=campo.unidade or self.unidade, valor_referencia=campo.valor_ref or self.valor_referencia)
            for campo in self.exame.campos.all()
            if campo.id not in existing_field_ids
        ]
        if to_create:
            ResultadoItem.objects.bulk_create(to_create)

# ==========================================================
# -------------------- RESULTADO ITEM ---------------------
# ==========================================================
from django.db import models
from django.utils import timezone


class ResultadoItem(models.Model):
	resultado = models.ForeignKey(
		'Resultado',
		on_delete=models.CASCADE,
		related_name='itens'
	)
	exame_campo = models.ForeignKey(
		'ExameCampoResultado',
		on_delete=models.CASCADE,
		related_name='itens_resultado',
          
	)
	unidade = models.ForeignKey(
		'Exame',
		on_delete=models.CASCADE,
		related_name='resultadoitem_unidade'
	)
	valor_referencia = models.ForeignKey(
		'Exame',
		on_delete=models.CASCADE,
		related_name='resultadoitem_valor_referencia'
	)
	valor = models.CharField(max_length=50, blank=True, null=True)
	gravado_em = models.DateTimeField(null=True, blank=True)

	class Meta:
		unique_together = ('resultado', 'exame_campo')
		verbose_name = "Item de Resultado"
		verbose_name_plural = "Itens de Resultado"
		ordering = ['resultado']

	def save(self, *args, **kwargs):
		if self.valor and not self.gravado_em:
			self.gravado_em = timezone.now()
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.resultado} | {self.exame_campo.nome_campo} = {self.valor or '—'}"

	# ===================== MÉTODOS PARA ADMIN =====================
	def get_unidade(self):
		"""Retorna o nome da unidade associada ao exame."""
		return getattr(self.unidade.unidade, 'nome', '-')
	get_unidade.short_description = "Unidade"

	def get_valor_referencia(self):
		"""Retorna o valor de referência associado ao exame."""
		return getattr(self.valor_referencia.valor_ref, 'valor_ref', '-')
	get_valor_referencia.short_description = "Valor de Referência"
