from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def teste(request):
    return Response({"mensagem": "Django funcionando!"})

# lab/api_views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem
from .serializers import (
    PacienteSerializer, ExameSerializer, ExameCampoSerializer,
    RequisicaoAnaliseSerializer, ResultadoItemSerializer
)

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

class ExameCampoViewSet(viewsets.ModelViewSet):
    queryset = ExameCampo.objects.all()
    serializer_class = ExameCampoSerializer

class ExameViewSet(viewsets.ModelViewSet):
    queryset = Exame.objects.all()
    serializer_class = ExameSerializer

class ResultadoItemViewSet(viewsets.ModelViewSet):
    queryset = ResultadoItem.objects.all()
    serializer_class = ResultadoItemSerializer

class RequisicaoAnaliseViewSet(viewsets.ModelViewSet):
    queryset = RequisicaoAnalise.objects.all()
    serializer_class = RequisicaoAnaliseSerializer
