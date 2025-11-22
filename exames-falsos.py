#!/usr/bin/env python3
import os
import django
import random
from faker import Faker

# =====================================
# CONFIGURAÇÃO DO DJANGO
# =====================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme seu projeto
django.setup()

from lab.models import Exame

# =====================================
# GERADOR DE EXAMES FALSOS
# =====================================
fake = Faker('pt_PT')
Faker.seed(0)

metodos = [m[0] for m in Exame.MetodoExame.choices]
setores = [s[0] for s in Exame.SetorExame.choices]

def gerar_exames(qtd=200):
    print(f"🧪 Gerando {qtd} exames falsos...")

    for i in range(1, qtd + 1):
        nome = f"{fake.word().capitalize()} Teste {i}"
        codigo = f"EX{i:04d}"
        metodo = random.choice(metodos)
        setor = random.choice(setores)
        trl_horas = random.choice([12, 24, 48, 72])
        activo = True

        # evita duplicatas
        if Exame.objects.filter(nome=nome).exists():
            continue

        exame = Exame(
            nome=nome,
            codigo=codigo,
            metodo=metodo,
            setor=setor,
            trl_horas=trl_horas,
            activo=activo
        )
        exame.save()

    print(f"✅ {Exame.objects.count()} exames na base.")

if __name__ == "__main__":
    gerar_exames(200)