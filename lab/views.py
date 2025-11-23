from django.shortcuts import get_object_or_404, render, redirect
from django import forms
from django.db import transaction
from django.http import HttpResponse
from .models import RequisicaoAnalise, ResultadoItem, ExameCampo
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# lab/views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem
from .serializers import (
    PacienteSerializer,
    ExameSerializer,
    ExameCampoSerializer,
    RequisicaoAnaliseSerializer,
    ResultadoItemSerializer,
)
import io
from reportlab.pdfgen import canvas

# ====================== PACIENTES ======================
class PacienteList(generics.ListCreateAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class PacienteDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

# ====================== EXAMES ======================
class ExameList(generics.ListCreateAPIView):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer

class ExameDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer

# ====================== EXAME CAMPOS ======================
class ExameCampoList(generics.ListCreateAPIView):
    queryset = ExameCampo.objects.all()
    serializer_class = ExameCampoSerializer

class ExameCampoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExameCampo.objects.all()
    serializer_class = ExameCampoSerializer

# ====================== REQUISIÇÕES ======================
class RequisicaoList(generics.ListCreateAPIView):
    queryset = RequisicaoAnalise.objects.all()
    serializer_class = RequisicaoAnaliseSerializer

class RequisicaoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = RequisicaoAnalise.objects.all()
    serializer_class = RequisicaoAnaliseSerializer

# PDF de requisição
class RequisicaoPdf(APIView):
    def get(self, request, pk):
        requisicao = RequisicaoAnalise.objects.get(pk=pk)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"Requisição ID: {requisicao.id}")
        p.drawString(100, 730, f"Paciente: {requisicao.paciente.nome}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

# ====================== RESULTADOS ======================
class ResultadoList(generics.ListCreateAPIView):
    queryset = ResultadoItem.objects.all()
    serializer_class = ResultadoItemSerializer

class ResultadoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResultadoItem.objects.all()
    serializer_class = ResultadoItemSerializer

# PDF de resultado
class ResultadoPdf(APIView):
    def get(self, request, pk):
        resultado = ResultadoItem.objects.get(pk=pk)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, f"Resultado ID: {resultado.id}")
        p.drawString(100, 730, f"Paciente: {resultado.paciente.nome}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')



# ========================== FORMULÁRIO DINÂMICO ==========================
class ResultadosDinamicosForm(forms.Form):
	"""
	Formulário gerado dinamicamente com base nos campos dos exames
	associados à requisição.
	"""
	def __init__(self, resultado_items_qs, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for ri in resultado_items_qs:
			field_name = f"ri_{ri.id}"
			label = f"{ri.exame_campo.exame.nome} — {ri.exame_campo.nome_campo}"

			tipo = ri.exame_campo.tipo
			if tipo == "NUM":
				field = forms.DecimalField(label=label, required=False)
			elif tipo == "PRC":
				field = forms.DecimalField(label=label, required=False, min_value=0, max_value=100)
			elif tipo == "CHC":
				field = forms.ChoiceField(label=label, required=False,
					choices=[("Positivo", "Positivo"), ("Negativo", "Negativo")])
			else:
				field = forms.CharField(label=label, required=False)

			field.initial = ri.resultado
			self.fields[field_name] = field


# ========================== PREENCHIMENTO DE RESULTADOS ==========================
def preencher_resultados(request, requisicao_id):
	"""
	Exibe apenas os campos dos exames selecionados na requisição
	e permite preencher os valores.
	"""
	requisicao = get_object_or_404(RequisicaoAnalise, id=requisicao_id)

	# Filtra apenas os exames escolhidos
	exames_selecionados = requisicao.exames.all()
	exames_campos = ExameCampo.objects.filter(exame__in=exames_selecionados)

	# Cria ou obtém ResultadoItem apenas para esses exames_campos
	for campo in exames_campos:
		ResultadoItem.objects.get_or_create(
			requisicao=requisicao,
			exame_campo=campo
		)

	# Agora busca apenas os resultados coerentes
	resultado_items = ResultadoItem.objects.filter(
		requisicao=requisicao,
		exame_campo__in=exames_campos
	).select_related('exame_campo', 'exame_campo__exame')

	if request.method == "POST":
		form = ResultadosDinamicosForm(resultado_items, request.POST)
		if form.is_valid():
			with transaction.atomic():
				for ri in resultado_items:
					key = f"ri_{ri.id}"
					ri.resultado = form.cleaned_data.get(key, "")
					ri.save()
			return redirect("lab:revisar_resultados", requisicao_id=requisicao.id)
	else:
		form = ResultadosDinamicosForm(resultado_items)

	# Agrupa por exame
	grouped = {}
	for ri in resultado_items:
		grouped.setdefault(ri.exame_campo.exame.nome, []).append(ri)

	return render(request, "lab/preencher_resultados.html", {
		"requisicao": requisicao,
		"form": form,
		"grouped": grouped,
	})


# ========================== REVISÃO DE RESULTADOS ==========================
def revisar_resultados(request, requisicao_id):
	"""
	Mostra todos os resultados preenchidos antes da validação.
	"""
	requisicao = get_object_or_404(RequisicaoAnalise, id=requisicao_id)
	resultado_items = ResultadoItem.objects.filter(
		requisicao=requisicao,
		exame_campo__exame__in=requisicao.exames.all()
	).select_related('exame_campo', 'exame_campo__exame')

	grouped = {}
	for ri in resultado_items:
		grouped.setdefault(ri.exame_campo.exame.nome, []).append(ri)

	return render(request, "lab/revisar_resultados.html", {
		"requisicao": requisicao,
		"grouped": grouped,
	})


# ========================== VALIDAÇÃO DE RESULTADOS ==========================
def validar_resultados_view(request, requisicao_id):
	"""
	Marca todos os resultados como validados pelo utilizador autenticado.
	"""
	requisicao = get_object_or_404(RequisicaoAnalise, id=requisicao_id)
	resultado_items = ResultadoItem.objects.filter(
		requisicao=requisicao,
		exame_campo__exame__in=requisicao.exames.all()
	)

	if request.method == "POST":
		with transaction.atomic():
			for ri in resultado_items:
				ri.validar(request.user)
			requisicao.marcar_validada()
		return redirect("admin:lab_requisicaoanalise_changelist")

	grouped = {}
	for ri in resultado_items:
		grouped.setdefault(ri.exame_campo.exame.nome, []).append(ri)

	return render(request, "lab/revisar_resultados.html", {
		"requisicao": requisicao,
		"grouped": grouped,
	})


# ========================== GERAÇÃO DE PDFs ==========================
def pdf_requisicao(request, requisicao_id):
	"""
	Gera o PDF institucional da requisição de análises clínicas.
	Apenas inclui os exames realmente selecionados.
	"""
	requisicao = get_object_or_404(
		RequisicaoAnalise.objects.select_related("paciente"),
		id=requisicao_id
	)
	pdf_bytes, filename = gerar_pdf_requisicao(requisicao)
	response = HttpResponse(pdf_bytes, content_type="application/pdf")
	response["Content-Disposition"] = f'attachment; filename="{filename}"'
	return response


def pdf_resultados(request, requisicao_id):
	"""
	Gera o PDF com resultados laboratoriais validados da requisição.
	Só mostra os resultados de exames que foram validados.
	"""
	requisicao = get_object_or_404(
		RequisicaoAnalise.objects.select_related("paciente"),
		id=requisicao_id
	)
	pdf_bytes, filename = gerar_pdf_resultados(requisicao, apenas_validados=True)
	response = HttpResponse(pdf_bytes, content_type="application/pdf")
	response["Content-Disposition"] = f'attachment; filename="{filename}"'
	return response


def inserir_resultados(request):
	return render(request, 'lab/inserir_resultados.html')

