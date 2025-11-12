# =====================================
# FORMS PERSONALIZADOS
# =====================================
from django import forms
from django.utils import timezone
from django_select2.forms import Select2MultipleWidget
from datetime import timedelta
from .models import Paciente, RequisicaoAnalise


# =====================================
# PACIENTE ADMIN FORM
# =====================================
class PacienteAdminForm(forms.ModelForm):
	"""Formulário customizado para o admin de Paciente, com data e hora separadas."""
	data_registo = forms.SplitDateTimeField(
		widget=forms.SplitDateTimeWidget(
			date_attrs={'type': 'date'},
			time_attrs={'type': 'time'}
		),
		initial=timezone.now
	)

	class Meta:
		model = Paciente
		fields = '__all__'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Cria opções rápidas para hoje e ontem (usado em lista <datalist>)
		hoje = timezone.now().date()
		ontem = hoje - timedelta(days=1)
		self.fields['data_registo'].widget.attrs['list'] = 'data_opcoes'


# =====================================
# REQUISIÇÃO DE ANÁLISE FORM
# =====================================
class RequisicaoAnaliseForm(forms.ModelForm):
	"""Formulário da Requisição de Análise com Select2 para múltiplos exames."""
	class Meta:
		model = RequisicaoAnalise
		fields = "__all__"
		widgets = {
			"exames": Select2MultipleWidget(attrs={
				"data-placeholder": "Selecione ou pesquise exames...",
				"style": "width: 100%; min-width: 300px;"
			}),
		}
