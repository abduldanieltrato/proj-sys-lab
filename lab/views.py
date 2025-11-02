from django.shortcuts import get_object_or_404, render
from .models import RequisicaoAnalise, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# -------------------- VIEWS OPERACIONAIS -----------------

def inserir_resultados(request):
    """
    View placeholder para inserção de resultados laboratoriais.
    """
    return render(request, "laboratorio/inserir_resultados.html", {})


def validar_resultados(request):
    """
    Lista todos os resultados pendentes de validação.
    """
    resultados = Resultado.objects.filter(validado=False).select_related("requisicao", "exame")
    contexto = {
        "resultados": resultados,
        "titulo_pagina": "Validação de Resultados Pendentes",
    }
    return render(request, "laboratorio/validar_resultados.html", contexto)


# -------------------- GERAÇÃO DE PDFs ---------------------

def pdf_requisicao(request, requisicao_id):
    """
    Gera PDF institucional da requisição de análises clínicas.
    """
    requisicao = get_object_or_404(
        RequisicaoAnalise.objects.select_related("paciente"),
        id=requisicao_id
    )
    return gerar_pdf_requisicao(requisicao)


def pdf_resultados(request, requisicao_id):
    """
    Gera PDF com resultados laboratoriais de uma requisição.
    """
    requisicao = get_object_or_404(
        RequisicaoAnalise.objects.prefetch_related("resultados__exame").select_related("paciente"),
        id=requisicao_id
    )
    return gerar_pdf_resultados(requisicao)
