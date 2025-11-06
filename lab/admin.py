from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado,
    Designacao, Metodo, ExameCampoResultado, ResultadoItem
)
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# ========================== PACIENTE ==========================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nid', 'nome', 'idade_display', 'data_entrada', 'residencia', 'proveniencia')
    search_fields = ('nome', 'nid', 'numero_id', 'telefone')
    list_filter = ('genero', 'nacionalidade', 'proveniencia')
    readonly_fields = ('created_at',)
    list_per_page = 25

# ========================== DESIGNACAO & METODO ==========================
@admin.register(Designacao)
class DesignacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']

@admin.register(Metodo)
class MetodoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']

# ========================== EXAME ==========================
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ['nome', 'designacao', 'metodo', 'display_valor_ref', 'tempo_resposta_display']
    list_filter = ['designacao', 'metodo']
    search_fields = ['nome', 'descricao']

# ========================== ITEM REQUISICAO INLINE ==========================
class ItemRequisicaoInline(admin.TabularInline):
    model = ItemRequisicao
    extra = 1
    autocomplete_fields = ['exame']

# ========================== RESULTADO INLINE REFINADO ==========================
class ResultadoInline(admin.TabularInline):
    model = Resultado
    extra = 0
    readonly_fields = ('unidade', 'valor_referencia')
    fields = ('exame', 'unidade', 'valor_referencia', 'resultado', 'observacoes')
    can_delete = False

    def get_queryset(self, request):
        """
        Retorna resultados existentes ou cria instâncias em memória
        para todos os exames da requisição, sem salvar ainda.
        """
        qs = super().get_queryset(request)
        requisicao = getattr(self, 'parent_obj', None)
        if requisicao:
            existing = {r.exame_id: r for r in qs}
            # Criar instâncias temporárias para exames sem resultado
            for exame in requisicao.exames_list.all():
                if exame.id not in existing:
                    temp_result = Resultado(requisicao=requisicao, exame=exame)
                    qs |= Resultado.objects.none()  # só para permitir append sem salvar
                    temp_result._state.adding = True  # marca como novo objeto
                    qs = list(qs) + [temp_result]  # converte QuerySet em lista para exibir
        return qs

# ========================== REQUISICAO ANALISE ==========================
class RequisicaoAnaliseAdminForm(forms.ModelForm):
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {'exames': forms.CheckboxSelectMultiple()}

@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
    form = RequisicaoAnaliseAdminForm
    inlines = [ItemRequisicaoInline, ResultadoInline]
    list_display = ('paciente', 'exames_summary', 'analista', 'created_at')
    search_fields = ('paciente__nome', 'paciente__nid', 'analista__username')
    list_filter = ('analista', 'paciente')
    autocomplete_fields = ('paciente', 'analista')
    readonly_fields = ('analista',)
    actions = ['baixar_pdf_requisicao']
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not obj.analista:
            obj.analista = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        Salva resultados novos após salvar a requisição e inline.
        """
        super().save_related(request, form, formsets, change)
        requisicao = form.instance
        for exame in requisicao.exames_list.all():
            Resultado.objects.get_or_create(requisicao=requisicao, exame=exame)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        ResultadoInline.parent_obj = obj
        return form

    def baixar_pdf_requisicao(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas uma requisição.", level='warning')
            return
        requisicao = queryset.first()
        pdf_content, filename = gerar_pdf_requisicao(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    baixar_pdf_requisicao.short_description = "Baixar PDF da Requisição"

# ========================== EXAME CAMPO ==========================
@admin.register(ExameCampoResultado)
class ExameCampoResultadoAdmin(admin.ModelAdmin):
    list_display = ('exame', 'nome_campo', 'tipo_campo', 'obrigatorio')
    search_fields = ('exame__nome', 'nome_campo')
    list_filter = ('tipo_campo', 'obrigatorio')

# ========================== RESULTADO ITEM ==========================
from django.contrib import admin
from .models import ResultadoItem


@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
	list_display = (
		'resultado',
		'exame_campo',
		'valor',
		'get_unidade',
		'get_valor_referencia',
		'gravado_em',
	)
	search_fields = (
		'resultado__requisicao__paciente__nome',
		'exame_campo__nome_campo',
		'resultado__exame__nome',
	)
	list_filter = ('exame_campo__tipo_campo', 'resultado__requisicao__analista')
	readonly_fields = ('gravado_em',)
	list_per_page = 25
	ordering = ['resultado']

	fieldsets = (
		("Informações do Resultado", {
			'fields': ('resultado', 'exame_campo', 'valor')
		}),
		("Referências", {
			'fields': ('unidade', 'valor_referencia', 'gravado_em')
		}),
	)

	def has_add_permission(self, request):
		# Permitir adição apenas através das requisições
		return True

	def has_change_permission(self, request, obj=None):
		return True

	def has_delete_permission(self, request, obj=None):
		return True
