#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme o seu projeto
django.setup()

from lab.models import Exame, ExameCampo

fake = Faker('pt_PT')
Faker.seed(2)
random.seed(2)

POTENCIAS = [p[0] for p in ExameCampo._meta.get_field('potencia').choices] if ExameCampo._meta.get_field('potencia').choices else ["x1"]
UNIDADES = ["mg/dL", "g/L", "U/L", "mmol/L", ""]

def gerar_campos_por_exame(min_campos=2, max_campos=6):
    exames = list(Exame.objects.all())
    if not exames:
        print("⚠️ Nenhum Exame encontrado. Rode gerar_exames primeiro.")
        return
    total = 0
    print(f"🧷 Gerando campos para {len(exames)} exames...")
    for exame in exames:
        qtd = random.randint(min_campos, max_campos)
        for ordem in range(1, qtd + 1):
            nome_campo = f"{fake.word().capitalize()} {ordem}"
            tipo = random.choice(["NUM", "TXT"])
            potencia = random.choice(POTENCIAS) if POTENCIAS else ""
            unidade = random.choice(UNIDADES)
            valor_ref = "" if tipo == "TXT" else f"{random.randint(0, 100)} - {random.randint(101, 500)}"
            campo = ExameCampo(
                exame=exame,
                nome_campo=nome_campo,
                tipo=tipo,
                potencia=potencia,
                unidade=unidade,
                valor_referencia=valor_ref,
                ordem=ordem
            )
            campo.save()
            total += 1
    print(f"✅ {total} campos criados. Média por exame: {total/len(exames):.2f}")

if __name__ == "__main__":
    gerar_campos_por_exame(2, 6)
