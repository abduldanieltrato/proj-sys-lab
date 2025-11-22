# setup_groups_permissions.py
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lab.models import Paciente, Exame, RequisicaoAnalise, Resultado

# Definição de grupos e permissões
GRUPOS_PERMISSOES = {
    "Administrador": {
        "models": [Paciente, Exame, RequisicaoAnalise, Resultado],
        "perms": ["add", "change", "delete", "view"]
    },
    "Administrativo": {
        "models": [Paciente, RequisicaoAnalise],
        "perms": ["add", "change", "view"]
    },
    "Técnico de Laboratório": {
        "models": [Paciente, RequisicaoAnalise, Resultado],
        "perms": ["add", "change", "view"]
    },
}

for grupo_nome, info in GRUPOS_PERMISSOES.items():
    # Cria o grupo se não existir
    grupo, criado = Group.objects.get_or_create(name=grupo_nome)
    if criado:
        print(f"Grupo criado: {grupo_nome}")
    else:
        print(f"Grupo já existe: {grupo_nome}")

    # Limpa permissões existentes para garantir consistência
    grupo.permissions.clear()

    # Atribui permissões aos modelos
    for model in info["models"]:
        ct = ContentType.objects.get_for_model(model)
        for perm_codename in info["perms"]:
            perm = Permission.objects.get(codename=f"{perm_codename}_{model._meta.model_name}", content_type=ct)
            grupo.permissions.add(perm)
    print(f"Permissões atribuídas ao grupo: {grupo_nome}")
