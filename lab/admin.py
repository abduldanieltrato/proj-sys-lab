from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils import timezone
from .models import (
    Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem, HistoricoOperacao
)
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# ========================== PACIENTE ==========================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Gestão de pacientes."""
    list_display = ('nome', 'numero_id', 'idade_display', 'genero', 'proveniencia', 'data_registo')
    search_fields = ('nome', 'numero_id', 'contacto', 'proveniencia')
    list_filter = ('genero', 'proveniencia')
    readonly_fields = ('data_registo',)
    list_per_page = 25


# ========================== EXAME ==========================
class ExameCampoInline(admin.TabularInline):
    """Campos configuráveis dentro de cada exame."""
    model = ExameCampo
    extra = 1
    fields = ('nome_campo', 'tipo', 'unidade', 'valor_referencia', 'ordem')
    ordering = ['ordem']


@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    """Gestão de exames e seus campos de resultados."""
    list_display = ('nome', 'codigo', 'trl_horas', 'activo')
    list_filter = ('activo',)
    search_fields = ('nome', 'codigo')
    inlines = [ExameCampoInline]
    list_per_page = 25


# ========================== RESULTADO INLINE ==========================
class ResultadoItemInline(admin.TabularInline):
    """Resultados individuais de uma requisição."""
    model = ResultadoItem
    extra = 0
    fields = ('exame_campo', 'resultado', 'unidade', 'valor_referencia', 'validado', 'data_validacao')
    readonly_fields = ('unidade', 'valor_referencia', 'data_validacao')
    can_delete = False

    def get_queryset(self, request):
        """Exibe resultados existentes ordenados por exame."""
        qs = super().get_queryset(request)
        return qs.select_related('exame_campo', 'requisicao').order_by('exame_campo__exame__nome')


# ========================== FORMULÁRIO DE REQUISIÇÃO ==========================
class RequisicaoAnaliseForm(forms.ModelForm):
    """Formulário com seleção múltipla de exames."""
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {'exames': forms.CheckboxSelectMultiple()}


# ========================== REQUISIÇÃO DE ANÁLISE ==========================
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
    """Gestão de requisições de análises laboratoriais."""
    form = RequisicaoAnaliseForm
    inlines = [ResultadoItemInline]
    list_display = ('id', 'paciente', 'status', 'analista', 'created_at')
    search_fields = ('paciente__nome', 'paciente__numero_id')
    list_filter = ('status', 'analista', 'created_at')
    autocomplete_fields = ('paciente', 'analista')
    readonly_fields = ('created_at', 'updated_at', 'analista')
    actions = ['gerar_pdf_requisicao', 'gerar_pdf_resultados']
    list_per_page = 25
    ordering = ['-created_at']

    def save_model(self, request, obj, form, change):
        """Atribui o analista automaticamente se não existir."""
        if not obj.analista:
            obj.analista = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """Cria entradas de resultados automaticamente ao salvar uma requisição."""
        super().save_related(request, form, formsets, change)
        requisicao = form.instance
        for exame in requisicao.exames.all():
            for campo in exame.campos.all():
                ResultadoItem.objects.get_or_create(
                    requisicao=requisicao,
                    exame_campo=campo,
                    defaults={
                        'unidade': campo.unidade,
                        'valor_referencia': campo.valor_referencia,
                    }
                )

    # ========== AÇÕES DE ADMIN ==========
    def gerar_pdf_requisicao(self, request, queryset):
        """Gera o PDF da requisição selecionada."""
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas uma requisição.", level='warning')
            return
        requisicao = queryset.first()
        pdf_content, filename = gerar_pdf_requisicao(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        return response
    gerar_pdf_requisicao.short_description = "Baixar PDF da Requisição"

    def gerar_pdf_resultados(self, request, queryset):
        """Gera o PDF dos resultados validados."""
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas uma requisição.", level='warning')
            return
        requisicao = queryset.first()
        pdf_content, filename = gerar_pdf_resultados(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
        return response
    gerar_pdf_resultados.short_description = "Baixar PDF de Resultados"


# ========================== RESULTADOS ==========================
@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
    """Gestão de resultados unitários de cada exame."""
    list_display = ('requisicao', 'exame_campo', 'resultado', 'unidade', 'valor_referencia', 'validado', 'data_validacao')
    search_fields = ('requisicao__paciente__nome', 'exame_campo__nome_campo', 'resultado')
    list_filter = ('validado', 'exame_campo__exame')
    readonly_fields = ('data_validacao',)
    ordering = ['requisicao', 'exame_campo']
    list_per_page = 30


# ========================== HISTÓRICO ==========================
@admin.register(HistoricoOperacao)
class HistoricoOperacaoAdmin(admin.ModelAdmin):
    """Monitoramento das operações administrativas e técnicas."""
    list_display = ('acao', 'utilizador', 'requisicao', 'data')
    search_fields = ('acao', 'utilizador__username', 'requisicao__paciente__nome')
    list_filter = ('acao', 'utilizador')
    readonly_fields = ('data',)
    ordering = ['-data']
    list_per_page = 40
