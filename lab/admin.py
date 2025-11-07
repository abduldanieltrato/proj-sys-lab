# admin.py
from django.contrib import admin
from django import forms
from django.http import HttpResponse, JsonResponse
from django.utils.html import format_html
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import (
	Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem, HistoricoOperacao
)
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# =====================================
# PACIENTE ADMIN
# =====================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
	list_display = ('id','nome','numero_id','idade','genero','proveniencia','data_registo_formatada')
	search_fields = ('id','nome','numero_id','contacto','proveniencia')
	list_filter = ('genero','proveniencia','data_registo')
	readonly_fields = ('data_registo','idade','genero','proveniencia','contacto')
	list_per_page = 50

	def idade(self, obj):
		return obj.idade()
	idade.short_description = "Idade"

	def data_registo_formatada(self, obj):
		return obj.data_registo.strftime("%d/%m/%Y às %H:%M")
	data_registo_formatada.short_description = "Data de Registo"


# =====================================
# EXAME ADMIN
# =====================================
class ExameCampoInline(admin.TabularInline):
	model = ExameCampo
	extra = 1
	fields = ('nome_campo','tipo','unidade','valor_referencia','ordem')
	ordering = ['ordem']

@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
	list_display = ('nome','codigo','setor','metodo','trl_horas','activo')
	list_filter = ('setor','metodo','activo')
	search_fields = ('nome','codigo','setor','metodo')
	inlines = [ExameCampoInline]
	list_per_page = 50


# =====================================
# RESULTADO ITEM INLINE PARA REQUISIÇÃO
# =====================================
class ResultadoItemInline(admin.TabularInline):
	model = ResultadoItem
	extra = 0
	fields = ('exame_campo','resultado','unidade','valor_referencia','validado','acoes')
	readonly_fields = ('unidade','valor_referencia','acoes')
	can_delete = False

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.select_related('exame_campo','exame_campo__exame','requisicao').order_by('exame_campo__exame__nome','exame_campo__ordem')

	def acoes(self, obj):
		if not obj.id:
			return ""
		return format_html(
			'<button class="button save" data-action="save" data-id="{}">💾</button>'
			'<button class="button validate" data-action="validate" data-id="{}">✅</button>'
			'<button class="button remove" data-action="remove" data-id="{}">🗑</button>',
			obj.id,obj.id,obj.id
		)
	acoes.short_description = "Ações"


# =====================================
# FORMULÁRIO PERSONALIZADO PARA REQUISIÇÃO
# =====================================
class RequisicaoAnaliseForm(forms.ModelForm):
	class Meta:
		model = RequisicaoAnalise
		fields = '__all__'
		widgets = {'exames': forms.CheckboxSelectMultiple()}


# =====================================
# REQUISIÇÃO DE ANÁLISE ADMIN
# =====================================
@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
	form = RequisicaoAnaliseForm
	inlines = [ResultadoItemInline]
	list_display = ('id','paciente','status','analista','created_at')
	search_fields = ('id','paciente__nome','paciente__numero_id')
	list_filter = ('status','analista','created_at')
	autocomplete_fields = ('paciente','analista')
	readonly_fields = ('created_at','updated_at','analista')
	actions = ['gerar_pdf_requisicao','gerar_pdf_resultados']
	list_per_page = 25
	ordering = ['-id','-created_at']
	change_form_template = "admin/requisicao_analise_changeform.html"

	def save_model(self, request, obj, form, change):
		# Atribui analista automaticamente
		if not obj.analista:
			obj.analista = request.user
		super().save_model(request,obj,form,change)

	def save_related(self, request, form, formsets, change):
		super().save_related(request,form,formsets,change)
		# Cria resultados automáticos para todos os campos de todos exames
		form.instance.criar_resultados_automaticos()


	# =====================================
	# AÇÕES DE PDF
	# =====================================
	def gerar_pdf_requisicao(self, request, queryset):
		if queryset.count() != 1:
			self.message_user(request,"Selecione apenas uma requisição.",level='warning')
			return
		req = queryset.first()
		pdf_content, filename = gerar_pdf_requisicao(req)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="{filename}"'
		return response
	gerar_pdf_requisicao.short_description = "Baixar PDF da Requisição"

	def gerar_pdf_resultados(self, request, queryset):
		if queryset.count() != 1:
			self.message_user(request,"Selecione apenas uma requisição.",level='warning')
			return
		req = queryset.first()
		pdf_content, filename = gerar_pdf_resultados(req)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="{filename}"'
		return response
	gerar_pdf_resultados.short_description = "Baixar PDF de Resultados"


# =====================================
# RESULTADO ITEM ADMIN (AJAX)
# =====================================
@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
	list_display = ('id','requisicao','exame_campo','resultado','validado','data_validacao')
	search_fields = ('requisicao__paciente__nome','exame_campo__nome_campo','resultado')
	list_filter = ('validado','exame_campo__exame')
	readonly_fields = ('data_validacao',)
	ordering = ['requisicao','exame_campo']
	list_per_page = 30

	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path('<int:pk>/update/', self.admin_site.admin_view(self.update_resultado), name='update_resultado'),
			path('<int:pk>/validate/', self.admin_site.admin_view(self.validate_resultado), name='validate_resultado'),
			path('<int:pk>/delete/', self.admin_site.admin_view(self.delete_resultado), name='delete_resultado'),
		]
		return custom_urls + urls

	@method_decorator(csrf_exempt)
	def update_resultado(self, request, pk):
		obj = get_object_or_404(ResultadoItem, pk=pk)
		obj.resultado = request.POST.get('resultado', obj.resultado)
		obj.save()
		return JsonResponse({'status':'ok'})

	@method_decorator(csrf_exempt)
	def validate_resultado(self, request, pk):
		obj = get_object_or_404(ResultadoItem, pk=pk)
		obj.validar(usuario=request.user)
		return JsonResponse({'status':'ok'})

	@method_decorator(csrf_exempt)
	def delete_resultado(self, request, pk):
		obj = get_object_or_404(ResultadoItem, pk=pk)
		obj.delete()
		return JsonResponse({'status':'ok'})


# =====================================
# HISTÓRICO ADMIN
# =====================================
@admin.register(HistoricoOperacao)
class HistoricoOperacaoAdmin(admin.ModelAdmin):
	list_display = ('id','acao','utilizador','requisicao','data')
	search_fields = ('acao','utilizador__username','requisicao__paciente__nome')
	list_filter = ('acao','utilizador')
	readonly_fields = ('data',)
	ordering = ['-id','-data']
	list_per_page = 40


# =====================================
# SIDEBAR HABILITADO
# =====================================
admin.site.enable_nav_sidebar = True
