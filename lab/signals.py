"""
Sinais automáticos do sistema AnaBioLink
Autor: Trato
Versão: 3.0
Descrição: Automatiza criação de resultados, histórico e sincronização
de estados entre modelos de análises laboratoriais.
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from .models import RequisicaoAnalise, ResultadoItem, HistoricoOperacao


# ========================== REQUISIÇÃO ANALISE ==========================
@receiver(post_save, sender=RequisicaoAnalise)
def criar_resultados_apos_requisicao(sender, instance, created, **kwargs):
    """
    Ao criar uma nova requisição, gerar automaticamente
    todos os campos de resultados associados aos exames incluídos.
    """
    if created:
        for exame in instance.exames.all():
            for campo in exame.campos.all():
                ResultadoItem.objects.get_or_create(
                    requisicao=instance,
                    exame_campo=campo,
                    defaults={
                        "unidade": campo.unidade,
                        "valor_referencia": campo.valor_referencia,
                    },
                )
        HistoricoOperacao.objects.create(
            utilizador=instance.analista,
            requisicao=instance,
            acao="Criação de Requisição",
            detalhes=f"Requisição criada para {instance.paciente.nome}.",
        )


# ========================== ATUALIZAÇÃO DE EXAMES EM REQUISIÇÃO ==========================
@receiver(m2m_changed, sender=RequisicaoAnalise.exames.through)
def sincronizar_exames_requisicao(sender, instance, action, pk_set, **kwargs):
    """
    Mantém os resultados sincronizados com os exames da requisição.
    Cria novos ResultadoItem se novos exames forem adicionados.
    """
    if action == "post_add":
        for exame_id in pk_set:
            exame = instance.exames.get(pk=exame_id)
            for campo in exame.campos.all():
                ResultadoItem.objects.get_or_create(
                    requisicao=instance,
                    exame_campo=campo,
                    defaults={
                        "unidade": campo.unidade,
                        "valor_referencia": campo.valor_referencia,
                    },
                )
        HistoricoOperacao.objects.create(
            utilizador=instance.analista,
            requisicao=instance,
            acao="Adição de Exames",
            detalhes=f"Foram adicionados novos exames à requisição {instance.id}.",
        )

    elif action == "post_remove":
        # opcional: remover ResultadoItems de exames removidos
        HistoricoOperacao.objects.create(
            utilizador=instance.analista,
            requisicao=instance,
            acao="Remoção de Exames",
            detalhes=f"Um ou mais exames foram removidos da requisição {instance.id}.",
        )


# ========================== RESULTADO ITEM ==========================
@receiver(post_save, sender=ResultadoItem)
def registar_validacao(sender, instance, created, **kwargs):
    """
    Regista automaticamente no histórico cada resultado salvo ou validado.
    """
    if created:
        HistoricoOperacao.objects.create(
            utilizador=instance.requisicao.analista,
            requisicao=instance.requisicao,
            acao="Criação de Resultado",
            detalhes=f"Campo '{instance.exame_campo.nome_campo}' criado para {instance.requisicao.paciente.nome}.",
        )
    else:
        acao = "Validação de Resultado" if instance.validado else "Atualização de Resultado"
        detalhes = f"Campo '{instance.exame_campo.nome_campo}' atualizado."
        if instance.validado:
            detalhes += f" Validado por {instance.validado_por} em {timezone.localtime(instance.data_validacao).strftime('%d/%m/%Y %H:%M')}."
        HistoricoOperacao.objects.create(
            utilizador=instance.validado_por or instance.requisicao.analista,
            requisicao=instance.requisicao,
            acao=acao,
            detalhes=detalhes,
        )

    if instance.validado:
        HistoricoOperacao.objects.create(
            utilizador=instance.requisicao.analista,
            requisicao=instance.requisicao,
            acao="Validação de Resultado",
            detalhes=f"Campo '{instance.exame_campo.nome_campo}' validado por {instance.validado_por} em {timezone.localtime(instance.data_validacao).strftime('%d/%m/%Y %H:%M')}.",
        )