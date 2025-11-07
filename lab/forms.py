from django import forms
from django.contrib import admin
from .models import Paciente
from datetime import datetime, timedelta

# Form customizado para o admin
class PacienteAdminForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'

    data_registo = forms.SplitDateTimeField(
        widget=forms.SplitDateTimeWidget(
            date_attrs={'type': 'date'},  # permite selecionar o dia
            time_attrs={'type': 'time'}   # permite selecionar a hora
        ),
        initial=datetime.now
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cria opções rápidas para hoje e ontem usando select
        hoje = datetime.now().date()
        ontem = hoje - timedelta(days=1)

        self.fields['data_registo'].widget.attrs['list'] = 'data_opcoes'
