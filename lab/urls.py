from django.urls import path
from . import views

app_name = "lab"

urlpatterns = [
    # ==================== RESULTADOS ====================
    path(
        "requisicao/<int:requisicao_id>/inserir-resultados/",
        views.inserir_resultados,
        name="inserir_resultados"
    ),
    path(
        "requisicao/<int:requisicao_id>/preencher-resultados/",
        views.preencher_resultados,
        name="preencher_resultados"
    ),
    path(
        "requisicao/<int:requisicao_id>/revisar-resultados/",
        views.revisar_resultados,
        name="revisar_resultados"
    ),
    path(
        "requisicao/<int:requisicao_id>/validar-resultados/",
        views.validar_resultados_view,
        name="validar_resultados"
    ),

    # ==================== GERAÇÃO DE PDF ====================
    path(
        "requisicao/<int:requisicao_id>/pdf/",
        views.pdf_requisicao,
        name="pdf_requisicao"
    ),
    path(
        "resultados/<int:requisicao_id>/pdf/",
        views.pdf_resultados,
        name="pdf_resultados"
    ),
]
