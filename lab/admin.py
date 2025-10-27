# ===========================================
# admin.py — Sistema de Gestão Laboratorial
# Autor: Trato
# Versão: Produção — Permissões refinadas por grupo
# ===========================================

from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.utils import timezone
from django.contrib.auth.models import Group
from .models import Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# ==========================================================
# -------------------- PACIENTE -----------------------------
# ==========================================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
	list_display = ('id', 'nome', 'genero', 'idade_display', 'telefone', 'proveniencia', 'nacionalidade', 'numero_id', 'created_at')
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
# -------------------- EXAME -------------------------------
# ==========================================================
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
	list_display = ('id', 'nome', 'descricao', 'valor_ref', 'unidade', 'trl_horas', 'tempo_resposta_display')
	search_fields = ('nome', 'descricao')
	ordering = ('nome',)
	list_per_page = 30

	def has_view_permission(self, request, obj=None):
		return request.user.is_authenticated

	def has_add_permission(self, request):
		user = request.user
		# Apenas administrador pode criar exames
		return user.is_superuser or user.groups.filter(name='Administrador').exists()

	def has_change_permission(self, request, obj=None):
		user = request.user
		# Apenas administrador pode editar exames
		return user.is_superuser or user.groups.filter(name='Administrador').exists()

	def has_delete_permission(self, request, obj=None):
		user = request.user
		# Apenas administrador pode excluir exames
		return user.is_superuser or user.groups.filter(name='Administrador').exists()


# ==========================================================
# -------------------- ITEM REQUISIÇÃO ----------------------
# ==========================================================
class ItemRequisicaoInline(admin.TabularInline):
	model = ItemRequisicao
	extra = 3
	autocomplete_fields = ['exame']
	show_change_link = True
	verbose_name = "Item de Exame"
	verbose_name_plural = "Itens de Exame"


# ==========================================================
# -------------------- FORMULÁRIO CUSTOMIZADO ---------------
# ==========================================================
class RequisicaoAnaliseAdminForm(forms.ModelForm):
	class Meta:
		model = RequisicaoAnalise
		fields = '__all__'
		widgets = {
			'exames': forms.CheckboxSelectMultiple()
		}


# ==========================================================
# -------------------- REQUISIÇÃO DE ANÁLISES ---------------
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
		pdf_content = gerar_pdf_requisicao(requisicao)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="requisicao_{requisicao.id}.pdf"'
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
	autocomplete_fields = ('requisicao', 'exame', 'validado_por')
	readonly_fields = ('data_insercao', 'data_validacao')
	actions = ['validar_resultados', 'baixar_pdf_resultados']
	list_per_page = 40

	def has_view_permission(self, request, obj=None):
		return request.user.is_authenticated

	def has_add_permission(self, request):
		user = request.user
		# Técnicos e administradores podem adicionar
		return user.is_superuser or user.groups.filter(name__in=['Administrador', 'Técnico de Laboratório']).exists()

	def has_change_permission(self, request, obj=None):
		user = request.user
		# Técnicos e administradores podem editar
		return user.is_superuser or user.groups.filter(name__in=['Administrador', 'Técnico de Laboratório']).exists()

	def has_delete_permission(self, request, obj=None):
		user = request.user
		return user.is_superuser or user.groups.filter(name='Administrador').exists()

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
			return
		requisicao = list(requisicoes)[0]
		pdf_content = gerar_pdf_resultados(requisicao)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="resultados_{requisicao.id}.pdf"'
		return response
	baixar_pdf_resultados.short_description = "Baixar PDF dos resultados selecionados"
