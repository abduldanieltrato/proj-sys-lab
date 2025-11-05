from django.shortcuts import get_object_or_404, render
from .models import RequisicaoAnalise, Resultado
from .utils.pdf_generator import gerar_pdf_requisicao, gerar_pdf_resultados

# -------------------- VIEWS OPERACIONAIS -----------------

def inserir_resultados(request, requisicao_id):
	req = get_object_or_404(RequisicaoAnalise, pk=requisicao_id)
	exames = req.exames.all()
	resultados_objs = []

	for exame in exames:
		resultado, created = Resultado.objects.get_or_create(requisicao=req, exame=exame)
		resultado.create_missing_result_items()
		resultados_objs.append(resultado)

	if request.method == "POST":
		for resultado in resultados_objs:
			for item in resultado.resultadoitem_set.all():
				valor = request.POST.get(f"item_{item.id}")
				if valor is not None:
					item.valor = valor
					item.save()

		return render(request, "lab/sucesso.html", {"mensagem": "Resultados salvos com sucesso!"})

	return render(request, "lab/inserir_resultados.html", {
		"requisicao": req,
		"resultados": resultados_objs,
	})


def validar_resultados(request):
	resultados = Resultado.objects.filter(validado=False).select_related("requisicao", "exame")

	if request.method == "POST":
		for resultado in resultados:
			if f"validar_{resultado.id}" in request.POST:
				resultado.validado = True
				resultado.save()

	return render(request, "lab/validar_resultados.html", {
		"resultados": resultados,
	})


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
