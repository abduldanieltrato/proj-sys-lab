# Django Admin Templates, URLs e CSS Personalizado (pt-MZ)

Abaixo estão todos os ficheiros integrados com o **Django Admin (Jazzmin)**, incluindo o novo **CSS personalizado** para realçar secções de exames e melhorar a experiência visual.

---

## `lab/urls.py`

```python
from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    path('requisicao/<int:requisicao_id>/preencher-resultados/', views.preencher_resultados, name='preencher_resultados'),
    path('requisicao/<int:requisicao_id>/revisar-resultados/', views.revisar_resultados, name='revisar_resultados'),
    path('requisicao/<int:requisicao_id>/validar-resultados/', views.validar_resultados_view, name='validar_resultados'),
]
```

---

## `lab/templates/lab/preencher_resultados.html`

```html
{% extends 'admin/base_site.html' %}
{% load static %}

{% block extrastyle %}
<link rel="stylesheet" href="{% static 'lab/css/resultados_admin.css' %}">
{% endblock %}

{% block title %}Preencher Resultados — {{ requisicao }}{% endblock %}

{% block content %}
<div class="content" style="max-width: 90%; margin: auto;">
  <h1>Preencher Resultados — Requisição #{{ requisicao.id }}</h1>
  <p><strong>Paciente:</strong> {{ requisicao.paciente.nome }} | <strong>ID:</strong> {{ requisicao.paciente.numero_id }}</p>
  <hr>

  <form method="post" novalidate>
    {% csrf_token %}
    <div class="module">
      {% for exame, itens in grouped.items %}
        <fieldset class="exame-bloco">
          <legend>🧪 {{ exame }}</legend>
          {% for ri in itens %}
            <div class="form-row">
              {{ form.ri_{{ ri.id }}.label_tag }}
              {{ form.ri_{{ ri.id }} }}
              {% if form.ri_{{ ri.id }}.help_text %}
                <p class="help">{{ form.ri_{{ ri.id }}.help_text }}</p>
              {% endif %}
              {% if form.ri_{{ ri.id }}.errors %}
                <div class="errors">{{ form.ri_{{ ri.id }}.errors }}</div>
              {% endif %}
            </div>
          {% endfor %}
        </fieldset>
      {% endfor %}
    </div>

    <div class="botoes-acao">
      <button type="submit" class="button default botao-verde">💾 Gravar Resultados</button>
      <a href="{% url 'lab:revisar_resultados' requisicao.id %}" class="button botao-azul">🔍 Revisar Resultados</a>
      <a href="/admin/lab/requisicaoanalise/" class="button cancel-link">⬅️ Voltar ao Painel</a>
    </div>
  </form>
</div>
{% endblock %}
```

---

## `lab/templates/lab/revisar_resultados.html`

```html
{% extends 'admin/base_site.html' %}
{% load static %}

{% block extrastyle %}
<link rel="stylesheet" href="{% static 'lab/css/resultados_admin.css' %}">
{% endblock %}

{% block title %}Revisar Resultados — {{ requisicao }}{% endblock %}

{% block content %}
<div class="content" style="max-width: 90%; margin: auto;">
  <h1>Revisar Resultados — Requisição #{{ requisicao.id }}</h1>
  <p><strong>Paciente:</strong> {{ requisicao.paciente.nome }} | <strong>ID:</strong> {{ requisicao.paciente.numero_id }}</p>
  <p><strong>Status:</strong> {{ requisicao.get_status_display }}</p>
  <hr>

  {% for exame, itens in grouped.items %}
    <fieldset class="exame-bloco">
      <legend>🧪 {{ exame }}</legend>
      <table class="tabela-resultados">
        <thead>
          <tr>
            <th>Campo</th>
            <th>Resultado</th>
            <th>Unidade</th>
            <th>Valor de Referência</th>
          </tr>
        </thead>
        <tbody>
          {% for ri in itens %}
          <tr>
            <td>{{ ri.exame_campo.nome_campo }}</td>
            <td>{{ ri.resultado|default:"—" }}</td>
            <td>{{ ri.unidade|default:"—" }}</td>
            <td>{{ ri.valor_referencia|default:"—" }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </fieldset>
  {% endfor %}

  <div class="botoes-acao">
    <a href="{% url 'lab:preencher_resultados' requisicao.id %}" class="button botao-amarelo">⬅️ Voltar a Editar</a>

    {% if request.user.is_superuser or request.user.groups.filter(name__in=['Administrador','Técnico de Laboratório']).exists %}
      <a href="{% url 'lab:validar_resultados' requisicao.id %}" class="button botao-verde">✅ Validar Resultados</a>
    {% endif %}

    <a href="/admin/lab/requisicaoanalise/" class="button cancel-link">🏠 Voltar ao Painel</a>
  </div>
</div>
{% endblock %}
```

---

## `lab/static/lab/css/resultados_admin.css`

```css
/* ============================
   Estilos personalizados para Jazzmin / Django Admin
   ============================ */

fieldset.exame-bloco {
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 15px 20px;
  margin-bottom: 25px;
  background-color: #fafafa;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

fieldset.exame-bloco legend {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  padding: 0 8px;
}

.tabela-resultados {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.tabela-resultados th {
  background-color: #3f51b5;
  color: white;
  text-align: left;
  padding: 8px;
}

.tabela-resultados td {
  border-bottom: 1px solid #ddd;
  padding: 6px 8px;
}

.tabela-resultados tr:nth-child(even) {
  background-color: #f9f9f9;
}

.botoes-acao {
  margin-top: 30px;
  display: flex;
  gap: 15px;
}

.botao-verde {
  background-color: #4CAF50 !important;
  color: white !important;
}

.botao-azul {
  background-color: #2196F3 !important;
  color: white !important;
}

.botao-amarelo {
  background-color: #FFC107 !important;
  color: black !important;
}

button.button:hover, a.button:hover {
  opacity: 0.9;
}
```

---

### ✅ Instruções
1. Cria a pasta `lab/static/lab/css/` e coloca o ficheiro `resultados_admin.css` lá dentro.  
2. Certifica-te que `STATICFILES_DIRS` no `settings.py` inclui o caminho da pasta `lab/static`.  
3. Reinicia o servidor e limpa o cache do navegador (para o CSS ser recarregado).  

Tudo agora fica visualmente integrado ao Django Admin, com estilo limpo, cores consistentes e botões de ação bem destacados.

