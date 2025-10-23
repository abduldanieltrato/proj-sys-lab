from django.urls import path
from . import views

app_name = "lab"

urlpatterns = [
    # Inserção de resultados de exames
    path('resultados/', views.inserir_resultados, name='inserir_resultados'),

    # Validação de resultados
    path('validacao/', views.validar_resultados, name='validar_resultados'),

    # Geração de PDF de uma requisição específica
    path('requisicao/<int:requisicao_id>/pdf/', views.pdf_requisicao, name='pdf_requisicao'),

    # Geração de PDF de resultados de uma requisição
    path('resultados/<int:requisicao_id>/pdf/', views.pdf_resultados, name='pdf_resultados'),
]
