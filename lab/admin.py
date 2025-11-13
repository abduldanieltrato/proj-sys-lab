from encodings.punycode import T
from math import e
from django.contrib import admin
from django import forms
from django.http import HttpResponse
from django.core.exceptions import ValidationError

from .models import Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# =====================================
# PACIENTE ADMIN
# =====================================
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('id_custom', 'nome', 'numero_id', 'idade', 'genero', 'proveniencia', 'data_registo_formatada')
    search_fields = ('id_custom', 'nome', 'numero_id', 'contacto', 'proveniencia')
    list_filter = ('genero', 'proveniencia', 'data_registo')
    readonly_fields = ('data_registo', 'idade', )
    list_per_page = 350

    def idade(self, obj):
        return obj.idade()
    idade.short_description = "Idade"

    def data_registo_formatada(self, obj):
        return obj.data_registo.strftime("%d/%m/%Y às %H:%M")
    data_registo_formatada.short_description = "Data de Registo"

# =====================================
# EXAME ADMIN
# =====================================
class ExameCampoForm(forms.ModelForm):
    class Meta:
        model = ExameCampo
        fields = '__all__'


class ExameCampoInline(admin.TabularInline):
    model = ExameCampo
    form = ExameCampoForm
    extra = 0
    fields = ('nome_campo', 'tipo','potencia', 'unidade', 'valor_referencia', 'ordem')
    ordering = ['ordem']

@admin.register(Exame)
class ExameAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'setor', 'metodo', 'trl_horas', 'activo')
    list_filter = ('setor', 'metodo', 'activo')
    search_fields = ('nome', 'codigo', 'setor', 'metodo')
    inlines = [ExameCampoInline]
    list_per_page = 200


@admin.register(ResultadoItem)
class ResultadoItemAdmin(admin.ModelAdmin):
	list_display = ("id_custom", "exame_nome", "campo_nome", "resultado", "unidade_display", "referencia_display", "validado", "data_validacao")
	list_filter = ("validado", "data_validacao", "exame_campo__exame")
	search_fields = ("exame_campo__nome_campo", "exame_campo__exame__nome", "resultado")


# =====================================
# RESULTADO INLINE
# =====================================
class ResultadoItemInline(admin.TabularInline):
    model = ResultadoItem
    extra = 0
    fields = ('exame_campo', 'resultado', 'unidade_display', 'referencia_display', 'validado', 'validado_por', 'data_validacao')
    readonly_fields = ('validado_por', 'data_validacao', 'exame_campo')
    can_delete = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('exame_campo', 'exame_campo__exame')

# =====================================
# FORMULÁRIO REQUISIÇÃO
# =====================================
class RequisicaoAnaliseForm(forms.ModelForm):
    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
        widgets = {'exames': forms.CheckboxSelectMultiple()}


# =====================================
# REQUISIÇÃO ADMIN
# =====================================
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from .models import RequisicaoAnalise
from .forms import RequisicaoAnaliseForm
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


@admin.register(RequisicaoAnalise)
class RequisicaoAnaliseAdmin(admin.ModelAdmin):
	"""
	Admin personalizado para gestão de requisições de análises.
	Inclui geração automática de resultados, controle de analista
	e exportação de PDFs de requisição e resultados validados.
	"""

	form = RequisicaoAnaliseForm
	inlines = [ResultadoItemInline]

	# ==========================
	# LISTAGEM E FILTROS
	# ==========================
	list_display = ('id_custom', 'paciente', 'status', 'analista', 'created_at')
	search_fields = ('id_custom', 'paciente__nome', 'paciente__numero_id', 'exames__nome', 'status')
	list_filter = ('status', 'analista', 'created_at')
	ordering = ['-created_at']
	list_per_page = 500

	# ==========================
	# CAMPOS E FORMULÁRIOS
	# ==========================
	autocomplete_fields = ('paciente', 'analista')
	readonly_fields = ('paciente', 'created_at', 'updated_at', 'analista', 'status',)
	change_form_template = "admin/requisicao_analise_changeform.html"
	actions = ['gerar_pdf_requisicao', 'gerar_pdf_resultados']

	fieldsets = (
		("Informações Básicas", {
			"fields": ("paciente", "status", "analista", "observacoes")
		}),
		("Seleção de Exames", {
			"fields": ("exames",)
		}),
	)

	# ==========================
	# MÍDIA (CSS/JS)
	# ==========================
	class Media:
		css = {
			"all": ["django_select2/django_select2.css"]
		}
		js = ["django_select2/django_select2.js"]

	# ==========================
	# SALVAMENTO PERSONALIZADO
	# ==========================
	def save_model(self, request, obj, form, change):
		"""Define o analista automaticamente, se não informado."""
		if not obj.analista:
			obj.analista = request.user
		super().save_model(request, obj, form, change)

	def save_related(self, request, form, formsets, change):
		"""Cria resultados automaticamente após salvar os relacionamentos."""
		super().save_related(request, form, formsets, change)
		form.instance.criar_resultados_automaticos()

	# ==========================
	# AÇÕES DE PDF
	# ==========================
	def gerar_pdf_requisicao(self, request, queryset):
		"""Gera o PDF da requisição selecionada."""
		if queryset.count() != 1:
			self.message_user(request, "Selecione apenas uma requisição.", level='warning')
			return
		req = queryset.first()
		pdf_content, filename = gerar_pdf_requisicao(req)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="{filename}"'
		return response
	gerar_pdf_requisicao.short_description = "Baixar PDF da Requisição"

	def gerar_pdf_resultados(self, request, queryset):
		"""Gera o PDF dos resultados validados."""
		if queryset.count() != 1:
			self.message_user(request, "Selecione apenas uma requisição.", level='warning')
			return
		req = queryset.first()
		pdf_content, filename = gerar_pdf_resultados(req, apenas_validados=True)
		response = HttpResponse(pdf_content, content_type='application/pdf')
		response['Content-Disposition'] = f'attachment; filename="{filename}"'
		return response
	gerar_pdf_resultados.short_description = "Baixar PDF de Resultados"


# =====================================
# ADMIN CONFIG
# =====================================
admin.site.enable_nav_sidebar = True
admin.site.anabled_actions = ['pdf_requisicao', 'pdf_resultados']