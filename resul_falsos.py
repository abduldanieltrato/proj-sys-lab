#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme o seu projeto
django.setup()

from lab.models import RequisicaoAnalise, ResultadoItem, ExameCampo
from django.contrib.auth import get_user_model

fake = Faker('pt_PT')
Faker.seed(4)
random.seed(4)
User = get_user_model()

def gerar_resultados_para_requisicoes(limit=None):
    reqs = RequisicaoAnalise.objects.all().order_by('-created_at')
    if limit:
        reqs = reqs[:limit]
    total_criados = 0
    print(f"🧾 Gerando resultados para {reqs.count()} requisições...")
    for req in reqs:
        # para cada exame vinculado, criar ResultadoItem para cada campo do exame
        exames = req.exames.all()
        for exame in exames:
            campos = exame.campos.all()
            for campo in campos:
                # get_or_create evita duplicação se o script for rodado novamente
                obj, created = ResultadoItem.objects.get_or_create(
                    requisicao=req,
                    exame_campo=campo,
                    defaults={
                        'resultado': "",
                        'validado': False
                    }
                )
                if created:
                    # salvar garante que o id_custom seja gerado se usar o mixin
                    obj.save()
                    total_criados += 1
    print(f"✅ {total_criados} ResultadoItem criados/garantidos. Total de resultados na base: {ResultadoItem.objects.count()}")

if __name__ == "__main__":
    gerar_resultados_para_requisicoes(limit=None)  # passe um int para limitar (ex: 500)
