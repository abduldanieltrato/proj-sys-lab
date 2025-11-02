from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import Group
from .models import (
    Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado,
    Designacao, Metodo
)
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# ==========================================================
# -------------------- PACIENTE ---------------------------
# ==========================================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'idade_display', 'data_entrada', 'residencia', 'proveniencia')
    search_fields = ('nome', 'numero_id', 'telefone')
    list_filter = ('genero', 'nacionalidade', 'proveniencia')
    ordering = ('nome',)
    list_per_page = 25
    readonly_fields = ('created_at',)

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        user = request.user
        return (
            user.is_superuser or
            user.groups.filter(name__in=['Administrador', 'Administrativo', 'Técnico de Laboratório']).exists()
        )

    def has_change_permission(self, request, obj=None):
        user = request.user
        return (
            user.is_superuser or
            user.groups.filter(name__in=['Administrador', 'Administrativo', 'Técnico de Laboratório']).exists()
        )

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name='Administrador').exists()


# ==========================================================
# -------------------- DESIGNACAO & METODO ----------------
# ==========================================================
@admin.register(Designacao)
class DesignacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']

@admin.register(Metodo)
class MetodoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome']


# ==========================================================
# -------------------- EXAME ------------------------------
# ==========================================================
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ['nome', 'designacao', 'metodo', 'display_valor_ref', 'tempo_resposta_display']
    list_filter = ['designacao', 'metodo']
    search_fields = ['nome', 'descricao']
    fieldsets = (
        ("Informações Gerais", {"fields": ("nome", "designacao", "metodo", "descricao")}),
        ("Dados Técnicos", {"fields": ("valor_ref", "unidade", "trl_horas"), "classes": ("collapse",)}),
    )


# ==========================================================
# -------------------- ITEM REQUISIÇÃO --------------------
# ==========================================================
class ItemRequisicaoInline(admin.TabularInline):
    model = ItemRequisicao
    extra = 1
    autocomplete_fields = ['exame']
    show_change_link = True
    verbose_name = "Exame"
    verbose_name_plural = "Itens de Exames"


# ==========================================================
# -------------------- FORMULÁRIO CUSTOMIZADO -------------
# ==========================================================
class RequisicaoAnaliseAdminForm(forms.ModelForm):
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {
            'exames': forms.CheckboxSelectMultiple()
        }


# ==========================================================
# -------------------- REQUISIÇÃO DE ANÁLISES -------------
# ==========================================================
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
    form = RequisicaoAnaliseAdminForm
    inlines = [ItemRequisicaoInline]
    list_display = ('id', 'paciente', 'exames_count', 'analista', 'observacoes_short')
    search_fields = ('paciente__nome', 'paciente__numero_id', 'analista__username')
    list_filter = ('analista', 'paciente')
    autocomplete_fields = ('paciente', 'analista')
    readonly_fields = ('analista',)
    actions = ['baixar_pdf_requisicao']
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not obj.analista:
            obj.analista = request.user
        super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        user = request.user
        return (
            user.is_superuser or
            user.groups.filter(name__in=['Administrador', 'Administrativo', 'Técnico de Laboratório']).exists()
        )

    def has_change_permission(self, request, obj=None):
        user = request.user
        return (
            user.is_superuser or
            user.groups.filter(name__in=['Administrador', 'Administrativo', 'Técnico de Laboratório']).exists()
        )

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name='Administrador').exists()

    def baixar_pdf_requisicao(self, request, queryset):
        if queryset.count() != 1:
            return
        requisicao = queryset.first()
        pdf_content, filename = gerar_pdf_requisicao(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    baixar_pdf_requisicao.short_description = "Baixar PDF da requisição selecionada"


# ==========================================================
# -------------------- RESULTADO ---------------------------
# ==========================================================
@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = (
        'requisicao', 'exame', 'resultado', 'unidade', 'valor_referencia',
        'is_valid_display', 'formatted_data_insercao',
        'validado_por', 'data_validacao'
    )
    search_fields = ('requisicao__paciente__nome', 'requisicao__paciente__numero_id', 'exame__nome')
    list_filter = ('validado', 'data_insercao', 'data_validacao')
    autocomplete_fields = ('requisicao', 'exame')
    readonly_fields = ('data_insercao', 'data_validacao')
    actions = ['validar_resultados', 'baixar_pdf_resultados']
    list_per_page = 40

    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

    def has_add_permission(self, request):
        user = request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'Técnico de Laboratório']).exists()

    def has_change_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name__in=['Administrador', 'Técnico de Laboratório']).exists()

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name='Administrador').exists()

    def validar_resultados(self, request, queryset):
        for res in queryset:
            if res.resultado and not res.validado:
                res.validado = True
                res.data_validacao = timezone.now()
                res.save()
    validar_resultados.short_description = "Validar resultados selecionados"

    def baixar_pdf_resultados(self, request, queryset):
        requisicoes = set(r.requisicao for r in queryset)
        if len(requisicoes) != 1:
            return
        requisicao = list(requisicoes)[0]
        pdf_content, filename = gerar_pdf_resultados(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    baixar_pdf_resultados.short_description = "Baixar PDF dos resultados selecionados"
