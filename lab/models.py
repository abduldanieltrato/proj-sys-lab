"""
Modelos centrais do sistema AnaBioLink - Sistema de Gestão Laboratorial
Autor: Trato
Versão: 3.0
Descrição: Estrutura de dados principal com propriedades inteligentes, consistência automática
e documentação otimizada para manutenção a longo prazo.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings


def get_user():
    """
    Retorna o modelo de usuário do Django.

    Returns:
        django.contrib.auth.models.User: O modelo de usuário do Django.
    """
    return get_user_model()


"""
O modelo de usuário do Django.
"""
User = get_user_model()


# =========================
# PACIENTE
# =========================
class Paciente(models.Model):
    """
    Registo de pacientes atendidos no laboratório.
    """
    nome = models.CharField("Nome completo", max_length=120)
    numero_id = models.CharField("Nº Documento", max_length=50, unique=True)
    data_nascimento = models.DateField("Data de nascimento", null=True, blank=True)
    genero = models.CharField("Gênero", max_length=10, choices=[("M", "Masculino"), ("F", "Feminino")], blank=True)
    contacto = models.CharField("Contacto", max_length=30, blank=True)
    proveniencia = models.CharField("Proveniência", max_length=80, blank=True)
    data_registo = models.DateTimeField("Data de registo", auto_now_add=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.numero_id})"

    def idade_display(self):
        """Calcula idade do paciente em anos."""
        if not self.data_nascimento:
            return "—"
        return int((timezone.now().date() - self.data_nascimento).days / 365.25)


# =========================
# EXAME
# =========================
class Exame(models.Model):
    """Catálogo geral de exames realizados no laboratório."""
    nome = models.CharField("Nome do exame", max_length=100, unique=True)
    codigo = models.CharField("Código", max_length=20, unique=True)
    descricao = models.TextField("Descrição", blank=True)
    trl_horas = models.PositiveIntegerField("Tempo de resposta (h)", default=24)
    activo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =========================
# CAMPOS DE EXAME
# =========================
class ExameCampo(models.Model):
    """Campos configuráveis para cada exame (definem o tipo de resultado)."""
    TIPO_RESULTADO = [
        ("NUM", "Numérico"),
        ("TXT", "Texto"),
        ("PRC", "Percentagem"),
        ("CHC", "Escolha"),
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
        ordering = ["exame", "ordem"]

    def __str__(self):
        return f"{self.exame.nome} → {self.nome_campo}"


# =========================
# REQUISIÇÃO DE ANÁLISES
# =========================
class RequisicaoAnalise(models.Model):
    """Requisição de exames feita para um paciente."""
    STATUS = [
        ("PEND", "Pendente"),
        ("PROC", "Em processamento"),
        ("CONC", "Concluída"),
        ("VAL", "Validada"),
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

    @property
    def exames_list(self):
        """Lista simples dos exames incluídos."""
        return list(self.exames.all())

    def marcar_concluida(self):
        """Atualiza estado para concluída."""
        self.status = "CONC"
        self.save()

    def marcar_validada(self):
        """Atualiza estado para validada."""
        self.status = "VAL"
        self.save()


# =========================
# RESULTADOS
# =========================
class ResultadoItem(models.Model):
    """Resultado individual de um campo pertencente a uma requisição."""
    requisicao = models.ForeignKey(RequisicaoAnalise, on_delete=models.CASCADE, related_name="resultados")
    exame_campo = models.ForeignKey(ExameCampo, on_delete=models.CASCADE, related_name="resultados")
    resultado = models.CharField("Resultado", max_length=120, blank=True)
    unidade = models.CharField("Unidade", max_length=20, blank=True)
    valor_referencia = models.CharField("Valor referência", max_length=80, blank=True)
    validado = models.BooleanField("Validado", default=False)
    validado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="validacoes_resultado")
    data_validacao = models.DateTimeField("Data de validação", null=True, blank=True)

    class Meta:
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ["requisicao", "exame_campo"]

    def __str__(self):
        return f"{self.requisicao} → {self.exame_campo.nome_campo}"

    def validar(self, usuario):
        """Marca o resultado como validado e regista o utilizador."""
        self.validado = True
        self.validado_por = usuario
        self.data_validacao = timezone.now()
        self.save()


# =========================
# HISTÓRICO E LOG
# =========================
class HistoricoOperacao(models.Model):
    """Registo de alterações e ações realizadas em requisições e resultados."""
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