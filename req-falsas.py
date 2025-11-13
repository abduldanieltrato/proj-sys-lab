#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste conforme o seu projeto
django.setup()

from lab.models import RequisicaoAnalise, Paciente, Exame
from django.contrib.auth import get_user_model

fake = Faker('pt_PT')
Faker.seed(3)
random.seed(3)
User = get_user_model()

def pegar_usuario_default():
    # tenta pegar um usuário existente (admin), senão None
    u = User.objects.first()
    return u

def gerar_requisicoes(qtd=2000, min_exames=1, max_exames=4):
    pacientes = list(Paciente.objects.all())
    exames = list(Exame.objects.filter(activo=True))
    if not pacientes:
        print("⚠️ Nenhum Paciente encontrado. Rode gerar_pacientes primeiro.")
        return
    if not exames:
        print("⚠️ Nenhum Exame ativo encontrado. Rode gerar_exames primeiro.")
        return

    analista_default = pegar_usuario_default()
    print(f"📦 Gerando {qtd} requisições para {len(pacientes)} pacientes e {len(exames)} exames ativos...")
    total = 0
    hoje_str = timezone.now().strftime("%Y%m%d")
    # obter o último id_custom do dia (para evitar colisão)
    ultimo = RequisicaoAnalise.objects.filter(id_custom__startswith=f"REQ{hoje_str}").order_by('id_custom').last()
    ultima_ordem = int(ultimo.id_custom[-4:]) if ultimo and ultimo.id_custom else 0

    for i in range(1, qtd + 1):
        paciente = random.choice(pacientes)
        num_exames = random.randint(min_exames, max_exames)
        escolhidos = random.sample(exames, k=min(num_exames, len(exames)))
        requisicao = RequisicaoAnalise(
            paciente=paciente,
            analista=analista_default,
            observacoes=fake.sentence(nb_words=6),
            status="PEND"
        )
        # salva para gerar id_custom via mixin
        requisicao.save()
        # adiciona exames many2many
        requisicao.exames.set(escolhidos)
        requisicao.save()
        total += 1
    print(f"✅ {total} requisições criadas. Total na base: {RequisicaoAnalise.objects.count()}")

if __name__ == "__main__":
    gerar_requisicoes(2000, 1, 4)
