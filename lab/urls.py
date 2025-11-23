from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PacienteViewSet, ExameViewSet, ExameCampoViewSet,
    RequisicaoAnaliseViewSet, ResultadoItemViewSet
)
from . import views

app_name = "lab"

# ----------------- ROTAS DA API -----------------
router = DefaultRouter()
router.register(r'pacientes', PacienteViewSet)
router.register(r'exames', ExameViewSet)
router.register(r'examecampos', ExameCampoViewSet)
router.register(r'requisicoes', RequisicaoAnaliseViewSet)
router.register(r'resultados', ResultadoItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # todos os endpoints REST via ViewSets
]

# ----------------- ROTAS DE VIEWS NORMAIS / PDFs -----------------
urlpatterns += [
    # Requisições
    path("requisicao/<int:requisicao_id>/inserir-resultados/", views.inserir_resultados, name="inserir_resultados"),
    path("requisicao/<int:requisicao_id>/preencher-resultados/", views.preencher_resultados, name="preencher_resultados"),
    path("requisicao/<int:requisicao_id>/revisar-resultados/", views.revisar_resultados, name="revisar_resultados"),
    path("requisicao/<int:requisicao_id>/validar-resultados/", views.validar_resultados_view, name="validar_resultados"),
    path("requisicao/<int:requisicao_id>/pdf/", views.RequisicaoPdf.as_view(), name="pdf_requisicao"),
    # Resultados
    path("resultados/<int:resultado_id>/pdf/", views.ResultadoPdf.as_view(), name="pdf_resultados"),
]
