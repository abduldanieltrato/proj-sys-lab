from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
from django.shortcuts import redirect

from .models import Paciente, Exame, RequisicaoAnalise, ItemRequisicao, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# -------------------- Paciente -------------------- #
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
	list_display = ('nome', 'genero', 'telefone', 'proveniencia', 'nacionalidade', 'numero_identificacao', 'created_at')
	search_fields = ('nome', 'telefone', 'numero_identificacao')
	list_filter = ('genero', 'nacionalidade', 'proveniencia')
	readonly_fields = ('created_at',)
	ordering = ('nome',)

# -------------------- Exame -------------------- #
@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
	list_display = ('nome', 'unidade', 'valor_referencia', 'trl_horas', 'ativo')
	search_fields = ('nome',)
	list_filter = ('ativo',)
	ordering = ('nome',)

# -------------------- Inline de Itens da Requisição -------------------- #
class ItemRequisicaoInline(admin.TabularInline):
	model = ItemRequisicao
	extra = 5
	max_num = 50

# -------------------- Formulário Admin da Requisição -------------------- #
class RequisicaoAnaliseAdminForm(forms.ModelForm):
	class Meta:
		model = RequisicaoAnalise
		fields = '__all__'
		widgets = {
			'exames': forms.CheckboxSelectMultiple(),
		}

# -------------------- Admin da Requisição -------------------- #
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
	list_display = ('id', 'paciente', 'analista', 'data_solicitacao')
	search_fields = ('paciente__nome', 'paciente__numero_identificacao', 'analista__username')
	list_filter = ('data_solicitacao',)
	autocomplete_fields = ('paciente', 'analista')
	inlines = [ItemRequisicaoInline]
	readonly_fields = ('data_solicitacao',)
	actions = ['action_gerar_pdf_requisicao']


	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		# Cria ItemRequisicao para cada exame selecionado
		for exame in obj.exames.all():
			ItemRequisicao.objects.get_or_create(requisicao=obj, exame=exame)

	def action_gerar_pdf_requisicao(self, request, queryset):
		if queryset.count() != 1:
			self.message_user(request, "Selecione apenas uma requisição para gerar PDF.")
			return
		return gerar_pdf_requisicao(queryset.first())
	action_gerar_pdf_requisicao.short_description = "Gerar PDF da Requisição"

# -------------------- Admin de Resultados -------------------- #
@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
	list_display = (
		'requisicao',
		'exame',
		'valor',
		'validado',
		'inserido_por',
		'data_insercao',
		'validado_por',
		'data_validacao',
		'status_validacao'
	)
	search_fields = (
		'requisicao__paciente__nome',
		'requisicao__paciente__numero_identificacao',
		'exame__nome',
		'inserido_por__username'
	)
	list_filter = ('validado', 'data_insercao', 'data_validacao')
	autocomplete_fields = ('requisicao', 'exame', 'inserido_por', 'validado_por')
	readonly_fields = ('data_insercao', 'data_validacao')
	actions = ['validar_resultados', 'action_gerar_pdf_resultados']

	def status_validacao(self, obj):
		if obj.validado:
			return format_html('<span style="color: green;">✔ Validado</span>')
		return format_html('<span style="color: red;">✘ Não validado</span>')
	status_validacao.short_description = 'Status'

	def validar_resultados(self, request, queryset):
		count = 0
		for resultado in queryset:
			if resultado.valor and not resultado.validado:
				resultado.validado = True
				resultado.validado_por = request.user
				resultado.data_validacao = timezone.now()
				resultado.save()
				count += 1
		self.message_user(request, f"{count} resultado(s) validado(s) com sucesso.")
	validar_resultados.short_description = "Validar resultados selecionados"

	def action_gerar_pdf_resultados(self, request, queryset):
		requisicoes = set(r.requisicao for r in queryset)
		if len(requisicoes) != 1:
			self.message_user(request, "Selecione resultados de uma única requisição para gerar o PDF.")
			return
		return gerar_pdf_resultados(list(requisicoes)[0])
	action_gerar_pdf_resultados.short_description = "Gerar PDF dos resultados selecionados"
