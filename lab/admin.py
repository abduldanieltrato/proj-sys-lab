# ===========================================
# admin.py — Sistema de Gestão Laboratorial
# ===========================================

import io
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse

# Imports internos
from .models import Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# ==========================================================
# -------------------- PACIENTE -----------------------------
# ==========================================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de pacientes."""
    list_display = (
        'nome', 'genero', 'idade_display', 'telefone', 'proveniencia',
        'nacionalidade', 'numero_id', 'created_at'
    )
    search_fields = ('nome', 'telefone', 'numero_id')
    list_filter = ('genero', 'nacionalidade', 'proveniencia')
    readonly_fields = ('created_at',)
    ordering = ('nome',)
    list_per_page = 25
    fieldsets = (
        ('Identificação', {'fields': ('id', 'nome', 'numero_id', 'data_nascimento', 'genero')}),
        ('Contacto & Residência', {'fields': ('telefone', 'residencia', 'nacionalidade')}),
        ('Informações Clínicas', {'fields': ('proveniencia', 'historico_medico', 'created_at')}),
    )

    def get_queryset(self, request):
        """Evita carregar campos pesados desnecessários no admin."""
        return super().get_queryset(request).defer('historico_medico')


# ==========================================================
# -------------------- EXAME -------------------------------
# ==========================================================
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de exames laboratoriais."""
    list_display = ('id', 'nome', 'unidade', 'valor_ref', 'trl_horas', 'tempo_resposta_display')
    search_fields = ('nome',)
    list_filter = ('trl_horas',)
    ordering = ('nome',)
    list_per_page = 30


# ==========================================================
# -------------------- ITEM REQUISIÇÃO (INLINE) -------------
# ==========================================================
class ItemRequisicaoInline(admin.TabularInline):
    """Inline de itens de requisição (exames) para RequisicaoAnalise."""
    model = ItemRequisicao
    extra = 5
    max_num = 50
    autocomplete_fields = ['exame']
    show_change_link = True
    verbose_name = "Item (Exame)"
    verbose_name_plural = "Itens (Exames)"


# ==========================================================
# -------------------- FORMULÁRIO CUSTOMIZADO ---------------
# ==========================================================
class RequisicaoAnaliseAdminForm(forms.ModelForm):
    """Form customizado para RequisicaoAnalise usando checkbox múltiplo para exames."""
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {'exames': forms.CheckboxSelectMultiple()}


# ==========================================================
# -------------------- REQUISIÇÃO DE ANÁLISES ---------------
# ==========================================================
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de requisições de análises clínicas."""
    form = RequisicaoAnaliseAdminForm
    inlines = [ItemRequisicaoInline]
    list_display = ('id', 'paciente', 'exames_count_display', 'analista', 'observacoes_short')
    search_fields = ('paciente__nome', 'paciente__numero_id', 'analista__username')
    list_filter = ('analista', 'paciente')
    autocomplete_fields = ('paciente', 'analista')
    readonly_fields = ('analista',)
    list_select_related = ('paciente', 'analista')
    actions = ['baixar_pdf_requisicao']
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        """Define o analista automaticamente e cria itens de requisição."""
        obj.analista = obj.analista or request.user
        super().save_model(request, obj, form, change)
        for exame in obj.exames.all():
            ItemRequisicao.objects.get_or_create(requisicao=obj, exame=exame)

    def exames_count_display(self, obj):
        """Exibe quantidade de exames associados à requisição."""
        return obj.exames_count
    exames_count_display.short_description = "Qtd. Exames"

    def observacoes_short(self, obj):
        """Exibe observações resumidas."""
        return obj.observacoes_short()
    observacoes_short.short_description = "Observações"

    def baixar_pdf_requisicao(self, request, queryset):
        """Ação para gerar PDF da requisição selecionada."""
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas uma requisição para baixar o PDF.")
            return None
        requisicao = queryset.first()
        pdf_content = gerar_pdf_requisicao(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="requisicao_{requisicao.id}.pdf"'
        return response
    baixar_pdf_requisicao.short_description = "Baixar PDF da requisição selecionada"


# ==========================================================
# -------------------- RESULTADOS ---------------------------
# ==========================================================
@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de resultados laboratoriais."""
    list_display = (
        'requisicao', 'exame', 'valor', 'unidade', 'valor_referencia',
        'is_valid_display', 'inserido_por', 'formatted_data_insercao',
        'validado_por', 'data_validacao',
    )
    search_fields = (
        'requisicao__paciente__nome', 'requisicao__paciente__numero_id', 
        'nome_completo', 'exame__nome', 'inserido_por__username'
    )
    list_filter = ('validado', 'data_insercao', 'data_validacao')
    autocomplete_fields = ('requisicao', 'exame', 'inserido_por', 'validado_por')
    readonly_fields = ('data_insercao', 'data_validacao', 'nome_completo')
    actions = ['validar_resultados', 'baixar_pdf_resultados']
    list_select_related = ('requisicao', 'exame', 'inserido_por', 'validado_por')
    list_per_page = 40

    def validar_resultados(self, request, queryset):
        """Valida resultados com valor preenchido e marca usuário como responsável pela validação."""
        count = 0
        for res in queryset:
            if res.valor and not res.validado:
                res.validado = True
                res.validado_por = request.user
                res.data_validacao = timezone.now()
                res.save()
                count += 1
        self.message_user(request, f"{count} resultado(s) validado(s) com sucesso.")
    validar_resultados.short_description = "Validar resultados selecionados"

    def baixar_pdf_resultados(self, request, queryset):
        """Gera PDF de resultados de uma requisição."""
        requisicoes = set(r.requisicao for r in queryset)
        if len(requisicoes) != 1:
            self.message_user(request, "Selecione resultados de uma única requisição para baixar o PDF.")
            return None
        requisicao = list(requisicoes)[0]
        pdf_content = gerar_pdf_resultados(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resultados_{requisicao.id}.pdf"'
        return response
    baixar_pdf_resultados.short_description = "Baixar PDF dos resultados selecionados"
