from django.conf import settings
from django.conf.urls import handler400, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

handler400 = "posts.views.page_not_found"
handler500 = "posts.views.server_error"

urlpatterns = [
    path("admin/", admin.site.urls),
    path('about/', include('about.urls', namespace='about')),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("posts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
