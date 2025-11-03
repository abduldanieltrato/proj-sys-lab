from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.utils import timezone


# ==========================================================
# -------------------- PACIENTE ----------------------------
# ==========================================================
class Paciente(models.Model):
    nid = models.CharField(primary_key=True, max_length=12, editable=False, verbose_name='nid')
    nome = models.CharField(max_length=255, verbose_name='Nome')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='data de nascimento')
    genero = models.CharField(max_length=32, choices=[('M', 'Masculino'), ('F', 'Feminino')], verbose_name='sexo')
    telefone = models.CharField(max_length=32, blank=True, verbose_name='Telefone')
    residencia = models.CharField(max_length=255, blank=True, verbose_name='residência')
    proveniencia = models.CharField(max_length=128, blank=True, verbose_name='proveniência')
    nacionalidade = models.CharField(max_length=64, blank=True, verbose_name='Nacionalidade')
    numero_id = models.CharField(max_length=64, unique=True, verbose_name='Identidade')
    historico_medico = models.TextField(blank=True, null=True, verbose_name='Histórico')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Entrada')

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.nid:
            hoje_str = date.today().strftime("%Y%m%d")  # YYYYMMDD
            contador = Paciente.objects.filter(created_at__date=date.today()).count() + 1
            self.nid = f"{hoje_str}{contador:04d}"  # Ex: 20251102 + 0001
        super().save(*args, **kwargs)

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        hoje = date.today()
        idade_em_anos = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade_em_anos -= 1
        return idade_em_anos

    def idade_display(self):
        if self.idade is None:
            return "—"
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

    def data_entrada(self):
        return self.created_at.strftime("%d/%m/%Y") if self.created_at else "—"
    data_entrada.short_description = "Entrada"

    def __str__(self):
        return f"{self.nome}"


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
    descricao = models.TextField(blank=True, verbose_name="Descrição")

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
    # id automático (AutoField) será criado automaticamente pelo Django
    nome = models.CharField(max_length=255, verbose_name='Exame')
    descricao = models.TextField(blank=True, help_text="Descrição do exame", verbose_name='Descrição')
    valor_ref = models.CharField(max_length=64, blank=True, verbose_name='Referência')
    unidade = models.CharField(max_length=32, blank=True, verbose_name='Unidades')
    trl_horas = models.PositiveIntegerField(default=24, verbose_name='TRL (horas)')

    designacao = models.ForeignKey(
        Designacao,
        on_delete=models.PROTECT,
        related_name="exames",
        verbose_name="Designação"
    )

    metodo = models.ForeignKey(
        Metodo,
        on_delete=models.PROTECT,
        related_name="exames",
        verbose_name="Método",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
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
        # mostrar nid do paciente (Paciente.__str__ já mostra nome (nid))
        return f"Req - #{self.paciente.nid} — {self.paciente.nome}"

    class Meta:
        verbose_name = "Requisição de Análises"
        verbose_name_plural = "Requisições de Análises"
        ordering = ['-created_at']


# ==========================================================
# -------------------- ITEM REQUISIÇÃO ---------------------
# ==========================================================
class ItemRequisicao(models.Model):
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, verbose_name='Requisição')
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, verbose_name='Exame')

    def __str__(self):
        return f"{self.requisicao} | {self.exame}"

    class Meta:
        verbose_name = "Item de Requisição"
        verbose_name_plural = "Itens de Requisição"


# ==========================================================
# -------------------- RESULTADO ---------------------------
# ==========================================================
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


# ==========================================================
# -------------------- Campos dinâmicos por exame ----------
# ==========================================================
class ExameCampoResultado(models.Model):
    exame = models.ForeignKey(Exame, on_delete=models.CASCADE, related_name='campos')
    nome_campo = models.CharField(max_length=255)
    tipo_campo = models.CharField(max_length=50, choices=[('text', 'Texto'), ('number', 'Número'), ('bool', 'Sim/Não')])
    obrigatorio = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.exame.nome} | {self.nome_campo}"


# ==========================================================
# -------------------- ResultadoItem -----------------------
# ==========================================================
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
        # retorno string legível
        return f"{self.requisicao} | {self.exame_campo.exame.nome} | {self.exame_campo.nome_campo}"
