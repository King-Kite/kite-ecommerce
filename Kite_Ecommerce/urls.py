from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include




admin.site.site_header = "Kite Administration"
admin.site.site_title = "Kite Administration Portal"
admin.site.index_title = "Kite Administration Portal"


urlpatterns = [
    path('admin/', include('admin_honeypot.urls')),
    path('secret/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('captcha/', include('captcha.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
