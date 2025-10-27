# ===========================================
# admin.py — Sistema de Gestão Laboratorial
# ===========================================

import io
from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils import timezone

from .models import Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# ==========================================================
# -------------------- PACIENTE -----------------------------
# ==========================================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'genero', 'idade_display', 'telefone', 'proveniencia',
                    'nacionalidade', 'numero_id', 'created_at')
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
        qs = super().get_queryset(request).defer('historico_medico')
        user = request.user
        if user.groups.filter(name="Tecnico").exists():
            # Técnico só vê pacientes vinculados a suas requisições
            qs = qs.filter(requisicaoanalise__analista=user).distinct()
        return qs

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if user.groups.filter(name="Tecnico").exists():
            return [f.name for f in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)

    def get_fieldsets(self, request, obj=None):
        user = request.user
        if user.groups.filter(name="Tecnico").exists():
            return (('Identificação', {'fields': ('nome', 'numero_id', 'genero')}),)
        return super().get_fieldsets(request, obj)

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao"]).exists():
            return True
        if user.groups.filter(name="Tecnico").exists():
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        user = request.user
        return user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao"]).exists()

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name="Administrador").exists()


# ==========================================================
# -------------------- EXAME -------------------------------
# ==========================================================
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'unidade', 'valor_ref', 'trl_horas', 'tempo_resposta_display')
    search_fields = ('nome',)
    list_filter = ('trl_horas',)
    ordering = ('nome',)
    list_per_page = 30

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        if not (user.is_superuser or user.groups.filter(name="Administrador").exists()):
            return [f.name for f in self.model._meta.fields]
        return []

    def get_actions(self, request):
        actions = super().get_actions(request)
        user = request.user
        if not (user.is_superuser or user.groups.filter(name="Administrador").exists()):
            actions.pop('delete_selected', None)
        return actions

    def has_change_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name="Administrador").exists()

    def has_add_permission(self, request):
        return self.has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request)


# ==========================================================
# -------------------- ITEM REQUISIÇÃO (INLINE) -------------
# ==========================================================
class ItemRequisicaoInline(admin.TabularInline):
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
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {'exames': forms.CheckboxSelectMultiple()}


# ==========================================================
# -------------------- REQUISIÇÃO DE ANÁLISES ---------------
# ==========================================================
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.groups.filter(name="Tecnico").exists():
            qs = qs.filter(analista=user)
        return qs

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao", "Tecnico"]).exists():
            return True
        return False

    def has_add_permission(self, request):
        user = request.user
        return user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao", "Tecnico"]).exists()

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.groups.filter(name__in=["Administrador", "Tecnico"]).exists():
            return True
        return False

    def save_model(self, request, obj, form, change):
        obj.analista = obj.analista or request.user
        super().save_model(request, obj, form, change)
        for exame in obj.exames.all():
            ItemRequisicao.objects.get_or_create(requisicao=obj, exame=exame)

    def exames_count_display(self, obj):
        return obj.exames_count
    exames_count_display.short_description = "Qtd. Exames"

    def observacoes_short(self, obj):
        return obj.observacoes_short()
    observacoes_short.short_description = "Observações"

    def baixar_pdf_requisicao(self, request, queryset):
        if queryset.count() != 1:
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.groups.filter(name="Tecnico").exists():
            qs = qs.filter(inserido_por=user)
        return qs

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.groups.filter(name="Administrador").exists():
            return True
        if user.groups.filter(name="Tecnico").exists():
            if obj is None:
                return True
            if obj.inserido_por == user and not obj.validado:
                return True
            return False
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        return user.is_superuser or user.groups.filter(name="Administrador").exists()

    def has_add_permission(self, request):
        user = request.user
        return user.groups.filter(name__in=["Tecnico", "Administrador"]).exists()

    def validar_resultados(self, request, queryset):
        for res in queryset:
            if res.valor and not res.validado:
                res.validado = True
                res.validado_por = request.user
                res.data_validacao = timezone.now()
                res.save()
    validar_resultados.short_description = "Validar resultados selecionados"

    def baixar_pdf_resultados(self, request, queryset):
        requisicoes = set(r.requisicao for r in queryset)
        if len(requisicoes) != 1:
            return None
        requisicao = list(requisicoes)[0]
        pdf_content = gerar_pdf_resultados(requisicao)
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resultados_{requisicao.id}.pdf"'
        return response
    baixar_pdf_resultados.short_description = "Baixar PDF dos resultados selecionados"
