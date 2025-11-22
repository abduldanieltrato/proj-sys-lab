# lab/serializers.py
from rest_framework import serializers
from .models import Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class ExameCampoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExameCampo
        fields = '__all__'

class ExameSerializer(serializers.ModelSerializer):
    campos = ExameCampoSerializer(many=True, read_only=True, source='examecampo_set')
    class Meta:
        model = Exame
        fields = '__all__'

class ResultadoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoItem
        fields = '__all__'

class RequisicaoAnaliseSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer(read_only=True)
    exames = ExameSerializer(many=True, read_only=True)
    resultados = ResultadoItemSerializer(many=True, read_only=True, source='resultadoitem_set')

    class Meta:
        model = RequisicaoAnalise
        fields = '__all__'
