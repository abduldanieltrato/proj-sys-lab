from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PacienteViewSet, ExameViewSet, ExameCampoViewSet,
    RequisicaoAnaliseViewSet, ResultadoItemViewSet
)
from . import views

app_name = "lab"

router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'exames', ExameViewSet)
router.register(r'examecampos', ExameCampoViewSet)
router.register(r'requisicoes', RequisicaoAnaliseViewSet)
router.register(r'resultados', ResultadoItemViewSet)

urlpatterns = [
    path('', include(router.urls)),  # raiz da API exposta
    # Rotas normais (views e PDFs)
    path("requisicao/<int:requisicao_id>/inserir-resultados/", views.inserir_resultados, name="inserir_resultados"),
    path("requisicao/<int:requisicao_id>/preencher-resultados/", views.preencher_resultados, name="preencher_resultados"),
    path("requisicao/<int:requisicao_id>/revisar-resultados/", views.revisar_resultados, name="revisar_resultados"),
    path("requisicao/<int:requisicao_id>/validar-resultados/", views.validar_resultados_view, name="validar_resultados"),
    path("requisicao/<int:requisicao_id>/pdf/", views.pdf_requisicao, name="pdf_requisicao"),
    path("resultados/<int:requisicao_id>/pdf/", views.pdf_resultados, name="pdf_resultados"),
]
