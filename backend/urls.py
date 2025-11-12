from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	# -------------------- ADMIN --------------------
	path("admin/", admin.site.urls),
 
	path("select2/", include("django_select2.urls")),

	# -------------------- APLICATIVOS --------------------
	path("", include("lab.urls")),

	# -------------------- INTERNACIONALIZAÇÃO --------------------
	path("i18n/", include("django.conf.urls.i18n")),
]

# -------------------- ARQUIVOS ESTÁTICOS E MÍDIA --------------------
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
