#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone

# =====================================
# CONFIGURAÇÃO DO DJANGO
# =====================================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme o projeto
django.setup()

from lab.models import Paciente  # modelo

# =====================================
# GERADOR DE PACIENTES FALSOS
# =====================================
fake = Faker('pt_PT')
Faker.seed(0)

proveniencias = [p[0] for p in Paciente.Proveniencia.choices]
generos = ["M", "F"]

def gerar_pacientes(qtd=5000):
    print(f"🧬 Gerando {qtd} pacientes hipotéticos...")

    hoje_str = timezone.now().strftime("%Y%m%d")
    # último código do dia
    ultimo = Paciente.objects.filter(id_custom__startswith=f"PAC{hoje_str}") \
                             .order_by('id_custom').last()
    if ultimo:
        ultima_ordem = int(ultimo.id_custom[-4:])
    else:
        ultima_ordem = 0

    for i in range(1, qtd + 1):
        nome = f"{fake.first_name()} {fake.last_name()}"
        numero_id = f"ID{Paciente.objects.count() + i:06d}"
        data_nascimento = fake.date_of_birth(minimum_age=1, maximum_age=90)
        genero = random.choice(generos)
        contacto = f"+2588{random.randint(20000000, 99999999)}"
        proveniencia = random.choice(proveniencias)

        ordem = ultima_ordem + i
        id_custom = f"PAC{hoje_str}{ordem:04d}"

        paciente = Paciente(
            id_custom=id_custom,
            nome=nome,
            numero_id=numero_id,
            data_nascimento=data_nascimento,
            genero=genero,
            contacto=contacto,
            proveniencia=proveniencia,
        )
        paciente.save()

    print(f"✅ {qtd} pacientes gerados com sucesso.")
    print(f"📊 Total de pacientes na base: {Paciente.objects.count()}")


if __name__ == "__main__":
    gerar_pacientes(5000)
