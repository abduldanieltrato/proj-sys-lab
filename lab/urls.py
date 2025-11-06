from django.urls import path
from . import views

app_name = "lab"

urlpatterns = [
	# -------------------- INSERÇÃO E VALIDAÇÃO --------------------
	path("inserir-resultados/<int:requisicao_id>/", views.inserir_resultados, name="inserir_resultados"),
	path("validar-resultados/", views.validar_resultados, name="validar_resultados"),

	# -------------------- GERAÇÃO DE PDF ---------------------------
	path("requisicao/<int:requisicao_id>/pdf/", views.pdf_requisicao, name="pdf_requisicao"),
	path("resultados/<int:requisicao_id>/pdf/", views.pdf_resultados, name="pdf_resultados"),
]
