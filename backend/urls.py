from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from django.conf.urls.static import static

urlpatterns = [
    # -------------------- ADMIN --------------------
    path("admin/", admin.site.urls),

    # -------------------- SELECT2 --------------------
    path("select2/", include("django_select2.urls")),

<<<<<<< HEAD
	# -------------------- INTERNACIONALIZAÇÃO --------------------
	path("i18n/", include("django.conf.urls.i18n")),
	path('', RedirectView.as_view(url='/admin/', permanent=False)),  # redireciona "/" para "/admin/"
    # outras rotas...
=======
    # -------------------- API NA RAIZ --------------------
    path("", include("lab.urls")),  # aqui a raiz já mostra os endpoints da API + views normais

    # -------------------- INTERNACIONALIZAÇÃO --------------------
    path("i18n/", include("django.conf.urls.i18n")),
>>>>>>> d92c9b3a48034f6de5ab86ced32b8135ce233787
]

# -------------------- ARQUIVOS ESTÁTICOS E MÍDIA --------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
