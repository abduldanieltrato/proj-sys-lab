from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import RequisicaoAnalise, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# Inserção de resultados - versão inicial
def inserir_resultados(request):
	# Apenas exibe uma página de placeholder
	return render(request, "laboratorio/inserir_resultados.html", {})

# Validação de resultados - versão inicial
def validar_resultados(request):
	# Lista resultados pendentes
	resultados = Resultado.objects.filter(validado=False)
	return render(request, "laboratorio/validar_resultados.html", {"resultados": resultados})

# Geração de PDF de uma requisição específica
def pdf_requisicao(request, requisicao_id):
	requisicao = get_object_or_404(RequisicaoAnalise, id=requisicao_id)
	return gerar_pdf_requisicao(requisicao)

# Geração de PDF de resultados de uma requisição
def pdf_resultados(request, requisicao_id):
	requisicao = get_object_or_404(RequisicaoAnalise, id=requisicao_id)
	return gerar_pdf_resultados(requisicao)
