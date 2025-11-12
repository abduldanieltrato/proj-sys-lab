#!/usr/bin/env python3
import os
import django
import random
from faker import Faker
from django.utils import timezone
from django.db import transaction

# ===================== CONFIG DJANGO =====================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # ajuste se necessário
django.setup()

# ===================== IMPORT MODELS =====================
from lab.models import (
    Paciente, Exame, ExameCampo, RequisicaoAnalise, ResultadoItem, gerar_codigo
)

# ===================== CONFIGURAÇÃO =====================
fake = Faker('pt_PT')
Faker_seed = 0
Faker.seed(Faker_seed)

QTD_REQUISICOES = 500    # ajuste: quantas requisições quer criar
MIN_EXAMES = 1           # exames por requisição (mín)
MAX_EXAMES = 4           # exames por requisição (máx)
BATCH_RES_CREATE = 500   # tamanho do batch para bulk_create de ResultadoItem
USAR_PACIENTES_EXISTENTES = True  # se False, criar pacientes novos (não implementado aqui)

# ===================== PREPARA SEQUÊNCIAS DIÁRIAS =====================
hoje_str = timezone.now().strftime("%Y%m%d")

# pega a última ordem já usada para REQ hoje
ultimo_req = RequisicaoAnalise.objects.filter(id_custom__startswith=f"REQ{hoje_str}") \
    .order_by("id_custom").last()
if ultimo_req and hasattr(ultimo_req, "id_custom"):
    seq_req = int(ultimo_req.id_custom[-4:])
else:
    seq_req = 0

# pega a última ordem já usada para RES hoje
ultimo_res = ResultadoItem.objects.filter(id_custom__startswith=f"RES{hoje_str}") \
    .order_by("id_custom").last()
if ultimo_res and hasattr(ultimo_res, "id_custom"):
    seq_res = int(ultimo_res.id_custom[-4:])
else:
    seq_res = 0

# lista de exames disponíveis (IDs)
exames_all = list(Exame.objects.values_list("id", flat=True))
if not exames_all:
    raise SystemExit("Não há exames na base. Gere exames primeiro.")

# lista de pacientes disponíveis
pacientes_all = list(Paciente.objects.all())
if not pacientes_all:
    raise SystemExit("Não há pacientes na base. Gere pacientes primeiro.")

print(f"Iniciando criação de {QTD_REQUISICOES} requisições — {len(exames_all)} exames disponíveis, {len(pacientes_all)} pacientes disponíveis.")
resultado_items_buffer = []

created_reqs = []

# ================ GERAR REQUISIÇÕES (salvar cada para permitir M2M) ================
for i in range(1, QTD_REQUISICOES + 1):
    seq_req += 1
    id_req = f"REQ{hoje_str}{seq_req:04d}"

    # escolher paciente aleatório
    paciente = random.choice(pacientes_all)

    # criar e salvar requisição
    with transaction.atomic():
        req = RequisicaoAnalise(
            id_custom=id_req,
            paciente=paciente,
            status="PEND"
        )
        # se tiver campos obrigatórios adicionais, ajuste aqui
        req.save()  # necessário para permitir .exames.add()

        # selecionar exames aleatórios
        n_exames = random.randint(MIN_EXAMES, MAX_EXAMES)
        exames_ids = random.sample(exames_all, k=min(n_exames, len(exames_all)))
        req.exames.add(*exames_ids)

        created_reqs.append(req)

    # --- criar ResultadoItem para cada campo de cada exame desta requisição ---
    # Obtem campos das pesquisas (ExameCampo) para os exames selecionados
    campos_qs = ExameCampo.objects.filter(exame_id__in=exames_ids).select_related("exame")
    for campo in campos_qs:
        seq_res += 1
        id_res = f"RES{hoje_str}{seq_res:04d}"
        # cria instância em memória (não salva ainda)
        ri = ResultadoItem(
            id_custom=id_res,
            requisicao=req,
            exame_campo=campo,
            resultado="",      # pode popular com fake se desejar
            validado=False
        )
        resultado_items_buffer.append(ri)

    # bulk create em lotes para performance
    if len(resultado_items_buffer) >= BATCH_RES_CREATE:
        ResultadoItem.objects.bulk_create(resultado_items_buffer)
        resultado_items_buffer = []

# inserir os restantes
if resultado_items_buffer:
    ResultadoItem.objects.bulk_create(resultado_items_buffer)
    resultado_items_buffer = []

print(f"Concluído: {len(created_reqs)} requisições criadas com seus resultados correspondentes.")
