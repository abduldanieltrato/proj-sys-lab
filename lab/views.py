# ===========================================
# views.py — Sistema de Gestão Laboratorial
# ===========================================

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import RequisicaoAnalise, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados


# ==========================================================
# -------------------- VIEWS OPERACIONAIS -----------------
# ==========================================================

def inserir_resultados(request):
	"""
	View placeholder para inserção de resultados laboratoriais.
	Posteriormente poderá incluir formulário ou upload de dados.
	"""
	return render(request, "laboratorio/inserir_resultados.html", {})


def validar_resultados(request):
	"""
	Lista todos os resultados pendentes de validação.
	Permite que o analista valide manualmente cada exame.
	"""
	resultados = Resultado.objects.filter(validado=False).select_related("requisicao", "exame")
	contexto = {
		"resultados": resultados,
		"titulo_pagina": "Validação de Resultados Pendentes",
	}
	return render(request, "laboratorio/validar_resultados.html", contexto)


# ==========================================================
# -------------------- GERAÇÃO DE PDFs ---------------------
# ==========================================================

def pdf_requisicao(request, requisicao_id):
	"""
	Gera PDF institucional da requisição de análises clínicas.
	Inclui logotipo, cabeçalho, rodapé e marca d'água.
	"""
	requisicao = get_object_or_404(
		RequisicaoAnalise.objects.select_related("paciente"),
		id=requisicao_id
	)
	pdf_bytes = gerar_pdf_requisicao(requisicao)
	response = HttpResponse(pdf_bytes, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="requisicao_{requisicao.id}.pdf"'
	return response


def pdf_resultados(request, requisicao_id):
	"""
	Gera PDF com resultados laboratoriais de uma requisição.
	Inclui cabeçalho, rodapé, marca d'água e tabela de exames com resultados.
	"""
	requisicao = get_object_or_404(
		RequisicaoAnalise.objects.prefetch_related("resultados__exame").select_related("paciente"),
		id=requisicao_id
	)
	pdf_bytes = gerar_pdf_resultados(requisicao)
	response = HttpResponse(pdf_bytes, content_type="application/pdf")
	response["Content-Disposition"] = f'inline; filename="resultados_{requisicao.id}.pdf"'
	return response
