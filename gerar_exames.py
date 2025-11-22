#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme o seu projeto
django.setup()

from lab.models import Exame

fake = Faker('pt_PT')
Faker.seed(1)
random.seed(1)

METODOS = [m[0] for m in Exame.MetodoExame.choices]
SETORES = [s[0] for s in Exame.SetorExame.choices]

def gerar_exames(qtd=200):
    print(f"🔬 Gerando {qtd} exames...")
    exist_count = Exame.objects.count()
    for i in range(1, qtd + 1):
        nome = f"{fake.word().capitalize()} {fake.word().capitalize()}"
        codigo = f"EX{exist_count + i:05d}"
        trl = random.choice([12, 24, 48, 72])
        metodo = random.choice(METODOS)
        setor = random.choice(SETORES)
        exame = Exame(
            nome=nome,
            codigo=codigo,
            trl_horas=trl,
            metodo=metodo,
            setor=setor,
            activo=True
        )
        try:
            exame.save()
        except Exception as e:
            # se nome/código duplicado, altera ligeiramente e tenta de novo
            exame.nome = f"{nome}-{i}"
            exame.codigo = f"{codigo}-{i}"
            exame.save()
    print(f"✅ {qtd} exames gerados. Total na base: {Exame.objects.count()}")

if __name__ == "__main__":
    gerar_exames(200)
