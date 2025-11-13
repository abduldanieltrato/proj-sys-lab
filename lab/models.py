from email.policy import default
from sys import prefix
from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError
from django.utils import timezone
from datetime import date
User = get_user_model()

# =====================================
# UTILITÁRIO DE GERAÇÃO DE CÓDIGO
# =====================================
def gerar_codigo(prefixo, modelo):
    hoje = timezone.now().strftime("%Y%m%d")
    ultimo = modelo.objects.filter(id_custom__startswith=f"{prefixo}{hoje}").order_by('id_custom').last()
    if ultimo and ultimo.id_custom:
        ultimo_num = int(ultimo.id_custom[-4:])
        nova_ordem = ultimo_num + 1
    else:
        nova_ordem = 1
    return f"{prefixo}{hoje}{nova_ordem:04d}"

# =====================================
# MIXIN PARA ID CUSTOM
# =====================================
class CustomIDMixin(models.Model):
    prefixo = None
    id_custom = models.CharField('Ordem de Trabalho', max_length=20, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id_custom and self.prefixo:
            self.id_custom = gerar_codigo(self.prefixo, self.__class__)
        super().save(*args, **kwargs)

# =====================================
# PACIENTE
# =====================================
class Paciente(CustomIDMixin):
    prefixo = "PAC"

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
    numero_id = models.CharField("Número de B.I/Passaporte", max_length=50, unique=True)
    data_nascimento = models.DateField("Data de nascimento", null=True, blank=True)
    genero = models.CharField("Gênero", max_length=10, choices=[("M","Masculino"),("F","Feminino")], blank=True)
    contacto = models.CharField("Telefone", max_length=30, blank=True, null=True)
    proveniencia = models.CharField("Proveniência", max_length=50, choices=Proveniencia.choices, default=Proveniencia.OUTRO, blank=True)
    email = models.EmailField("Email", blank=True, null=True, unique=True, default=None )
    data_registo = models.DateTimeField("Data de registo", auto_now_add=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.id_custom})"

    def idade(self):
        if not self.data_nascimento:
            return "—"
        delta = (date.today() - self.data_nascimento).days
        anos = delta // 365
        if anos >= 2: return f"{anos} anos"
        meses = delta // 30
        if meses >= 2: return f"{meses} meses"
        return f"{delta} dias"

# =====================================
# EXAME
# =====================================
class Exame(models.Model):
    class MetodoExame(models.TextChoices):
        ENZIMATICO = "Enzimático", "Enzimático"
        COLORIMETRICO = "Colorimétrico", "Colorimétrico"
        HISTOLOGICO = "Histológico", "Histológico"
        MICROSCOPICO = "Microscópico", "Microscópico"
        CITOMETRIA_DE_FLUXO = "Citometria de Fluxo", "Citometria de Fluxo"
        QUIMICO = "Químico", "Químico"
        CITOLOGICO = "Citoológico", "Citoológico"
        ESPECTROFOTOMETRICO = "Espectrofotométrico", "Espectrofotométrico"
        CULTURA = "Cultura", "Cultura"
        IMUNOLOGICO = "Imunológico", "Imunológico"
        ELISA = "ELISA", "ELISA"
        PCR = "PCR / Reação em Cadeia da Polimerase", "PCR / Reação em Cadeia da Polimerase"
        OUTRO = "Outro", "Outro"

    class SetorExame(models.TextChoices):
        HEMATOLOGIA = "Hematologia", "Hematologia"
        SEROLOGIA = "Serologia", "Serologia"
        ANATOMIA_PATHOLOGICA = "Anatomia Páthologica", "Anatomia Páthologica"
        BIOQUIMICA = "Bioquímica", "Bioquímica"
        MICROBIOLOGIA = "Microbiologia", "Microbiologia"
        IMUNOLOGIA = "Imunologia", "Imunologia"
        PARASITOLOGIA = "Parasitologia", "Parasitologia"
        BANCO_DE_SANGUE = "Banco de Sangue", "Banco de Sangue"
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
# CAMPO DE EXAME
# =====================================
class ExameCampo(models.Model):
    TIPO_RESULTADO = [
        ("NUM", "Numérico"),
        ("TXT", "Texto"),
    ]

    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name="campos")
    nome_campo = models.CharField("indicador", max_length=80)
    tipo = models.CharField("resultado", max_length=3, choices=TIPO_RESULTADO, default="NUM")
    potencia = models.CharField("potência", default="x1000000", max_length=8, blank=True, choices=[("x100000", "x1000000"), ("x1000", "x1000"), ("x1000", "x1000"), ("x1000000", "x1000000")])
    unidade = models.CharField("unidade S.I.", max_length=8, blank=True)
    valor_referencia = models.CharField("Valor de referência", max_length=80, blank=True)
    ordem = models.PositiveIntegerField("Ordem", default=1)

    class Meta:
        verbose_name = "Campo de Exame"
        verbose_name_plural = "Campos de Exame"
        ordering = ["exame","ordem"]

    def __str__(self):
        return f"{self.exame.nome} → {self.nome_campo}"


# =====================================
# REQUISIÇÃO DE ANÁLISE
# =====================================
class RequisicaoAnalise(CustomIDMixin):
    prefixo = "REQ"

    STATUS = [
        ("PEND","Pendente"),
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
        return f"{self.id_custom} - {self.paciente}"

    def criar_resultados_automaticos(self):
        for exame in self.exames.all():
            for campo in exame.campos.all():
                ResultadoItem.objects.get_or_create(
                    requisicao=self,
                    exame_campo=campo
                )

    @property
    def total_resultados(self):
        return self.resultados.count()

    @property
    def pendentes(self):
        return self.resultados.filter(validado=False).count()

    @property
    def validados(self):
        return self.resultados.filter(validado=True).count()

# =====================================
# RESULTADO DE EXAME
# =====================================
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class ResultadoItem(CustomIDMixin):
	prefixo = "RES"

	requisicao = models.ForeignKey(
		RequisicaoAnalise,
		on_delete=models.CASCADE,
		related_name="resultados"
	)
	exame_campo = models.ForeignKey(
		ExameCampo,
		on_delete=models.CASCADE,
		related_name="resultados",
		verbose_name="Exame"
	)
	resultado = models.CharField("Resultado", max_length=120, blank=True)

	unidade = models.ForeignKey(
		ExameCampo,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="resultados_unidade",
		verbose_name="Unidade"
	)
	referencia = models.ForeignKey(
		ExameCampo,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="resultados_referencia",
		verbose_name="Referência"
	)

	validado = models.BooleanField("Validado", default=False)
	validado_por = models.ForeignKey(
		User,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="validacoes_resultado"
	)
	data_validacao = models.DateTimeField("Data de validação", null=True, blank=True)

	class Meta:
		verbose_name = "Resultado"
		verbose_name_plural = "Resultados"
		ordering = ["requisicao", "exame_campo"]

	def __str__(self):
		return f"{self.id_custom} - {self.exame_campo.nome_campo}"

	# ========================== MÉTODOS AUXILIARES ==========================
	def validar(self, usuario):
		"""Marca o resultado como validado."""
		self.validado = True
		self.validado_por = usuario
		self.data_validacao = timezone.now()
		self.save(update_fields=["validado", "validado_por", "data_validacao"])

	def unidade_display(self):
		"""Retorna a unidade do exame campo principal (ou do FK unidade)."""
		if self.unidade and self.unidade.unidade:
			return self.unidade.unidade
		return self.exame_campo.unidade or "—"
	unidade_display.short_description = "Unidade"

	def referencia_display(self):
		"""Retorna o valor de referência do exame campo principal (ou do FK referência)."""
		if self.referencia and self.referencia.valor_referencia:
			return self.referencia.valor_referencia
		return self.exame_campo.valor_referencia or "—"
	referencia_display.short_description = "Valor de Referência"

	def exame_nome(self):
		"""Retorna o nome do exame principal para exibição no admin."""
		return self.exame_campo.exame.nome
	exame_nome.short_description = "Exame"

	def campo_nome(self):
		"""Retorna o nome do parâmetro do exame."""
		return self.exame_campo.nome_campo
	campo_nome.short_description = "Campo"

