from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Xato qo‘shimchalari
handler404 = 'mainSystem.views.custom_error_view'
handler500 = 'mainSystem.views.custom_error_view'
handler403 = 'mainSystem.views.custom_error_view'
handler400 = 'mainSystem.views.custom_error_view'

urlpatterns = [
    path('boshqaruv/', admin.site.urls),
    path('', include("mainSystem.urls"))
]

# Faqat sinov uchun: `serve` orqali statik va media fayllarga kirish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]
