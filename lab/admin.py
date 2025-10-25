# ===========================================
# admin.py — Sistema de Gestão Laboratorial
# ===========================================

import io
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

# Imports internos
from .models import Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

from django.contrib import admin, messages
from .models import Paciente

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

	# ✏️ Permissão de edição
	def has_change_permission(self, request, obj=None):
		user = request.user

		# Administrador edita tudo
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True

		# Recepção pode editar tudo
		if user.groups.filter(name="Recepcao").exists():
			return True

		# Técnico só pode visualizar
		if user.groups.filter(name="Tecnico").exists():
			messages.warning(request, "⚠️ Técnicos não podem editar dados de pacientes.")
			return False

		# Bloqueio padrão
		return super().has_change_permission(request, obj)

	# ➕ Permissão de criação
	def has_add_permission(self, request):
		user = request.user

		# Administrador e Recepção podem cadastrar
		if user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao"]).exists():
			return True

		messages.error(request, "🚫 Apenas a recepção e o administrador podem cadastrar pacientes.")
		return False

	# ❌ Bloqueio de exclusão
	def has_delete_permission(self, request, obj=None):
		user = request.user

		# Apenas administrador pode eliminar
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True

		# Recepção é bloqueada
		if user.groups.filter(name="Recepcao").exists():
			messages.error(request, "🚫 Ação proibida: a recepção não pode eliminar registros de pacientes.")
			return False

		# Técnico também não pode
		if user.groups.filter(name="Tecnico").exists():
			messages.error(request, "🚫 Técnicos não têm permissão para eliminar pacientes.")
			return False

		return super().has_delete_permission(request, obj)


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

	# Campos somente leitura para quem não é administrador
	def get_readonly_fields(self, request, obj=None):
		user = request.user
		if not (user.is_superuser or user.groups.filter(name="Administrador").exists()):
			return [f.name for f in self.model._meta.fields]  # todos campos readonly
		return []

	# Remove ações não permitidas
	def get_actions(self, request):
		actions = super().get_actions(request)
		user = request.user
		if not (user.is_superuser or user.groups.filter(name="Administrador").exists()):
			# Remove ação de deletar
			if 'delete_selected' in actions:
				del actions['delete_selected']
		return actions

	# Permissão de edição granular
	def has_change_permission(self, request, obj=None):
		user = request.user
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True
		return False

	# Permissão de criação
	def has_add_permission(self, request):
		user = request.user
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True
		return False

	# Permissão de exclusão
	def has_delete_permission(self, request, obj=None):
		user = request.user
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True
		return False


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

	# 🔒 Queryset: todos veem todas requisições
	def get_queryset(self, request):
		return super().get_queryset(request)

	# ✏️ Permissão de edição granular
	def has_change_permission(self, request, obj=None):
		user = request.user

		# Administrador: edita tudo
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True

		# Recepção: pode editar qualquer requisição
		if user.groups.filter(name="Recepcao").exists():
			return True

		# Técnico: pode editar qualquer requisição da equipa laboratorial
		if user.groups.filter(name="Tecnico").exists():
			return True

		return super().has_change_permission(request, obj)

	# ➕ Permissão de criação
	def has_add_permission(self, request):
		user = request.user

		# Administrador, Recepção e Técnico podem criar
		if user.is_superuser or user.groups.filter(name__in=["Administrador", "Recepcao", "Tecnico"]).exists():
			return True

		messages.error(
			request,
			"🚫 Você não tem permissão para criar requisições."
		)
		return False

	# ❌ Bloqueio de exclusão
	def has_delete_permission(self, request, obj=None):
		user = request.user

		# Administrador: acesso total
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True

		# Técnico: pode deletar (equipa laboratorial)
		if user.groups.filter(name="Tecnico").exists():
			return True

		# Recepção: não pode deletar
		if user.groups.filter(name="Recepcao").exists():
			messages.error(
				request,
				"🚫 A recepção não pode excluir requisições."
			)
			return False

		return super().has_delete_permission(request, obj)

	# 💾 Salvamento automático: define analista e cria itens de requisição
	def save_model(self, request, obj, form, change):
		obj.analista = obj.analista or request.user
		super().save_model(request, obj, form, change)
		for exame in obj.exames.all():
			ItemRequisicao.objects.get_or_create(requisicao=obj, exame=exame)

	# 📊 Exibição de contagem de exames
	def exames_count_display(self, obj):
		return obj.exames_count
	exames_count_display.short_description = "Qtd. Exames"

	# ✂️ Exibição resumida de observações
	def observacoes_short(self, obj):
		return obj.observacoes_short()
	observacoes_short.short_description = "Observações"

	# 📄 Ação customizada: baixar PDF da requisição
	def baixar_pdf_requisicao(self, request, queryset):
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
from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Resultado
from .utils.pdf_generator import gerar_pdf_resultados

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

	# 🔒 Queryset: técnico vê todos resultados, mas só pode editar os próprios não validados
	def get_queryset(self, request):
		return super().get_queryset(request)

	# ✏️ Permissão de edição granular
	def has_change_permission(self, request, obj=None):
		user = request.user

		# Administrador tem acesso total
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True

		# Técnico: só edita os próprios resultados e não validados
		if user.groups.filter(name="Tecnico").exists():
			if obj is None:
				return True
			if obj.inserido_por == user and not obj.validado:
				return True
			messages.warning(
				request,
				"⚠️ Ação bloqueada: técnicos só podem editar resultados que inseriram e que ainda não foram validados."
			)
			return False

		# Recepção não tem permissão
		if user.groups.filter(name="Recepcao").exists():
			messages.error(
				request,
				"🚫 Acesso negado: a recepção não tem permissão para alterar resultados."
			)
			return False

		return super().has_change_permission(request, obj)

	# 🚫 Bloqueio de exclusão
	def has_delete_permission(self, request, obj=None):
		user = request.user
		if user.is_superuser or user.groups.filter(name="Administrador").exists():
			return True
		messages.error(request, "🚫 Apenas o administrador pode eliminar resultados.")
		return False

	# 🧱 Criação de novos registros
	def has_add_permission(self, request):
		user = request.user
		if user.groups.filter(name__in=["Tecnico", "Administrador"]).exists():
			return True
		messages.warning(request, "🚫 Recepção não pode criar resultados laboratoriais.")
		return False

	# ✅ Ação customizada: validar resultados
	def validar_resultados(self, request, queryset):
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

	# ✅ Ação customizada: baixar PDF de resultados
	def baixar_pdf_resultados(self, request, queryset):
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
