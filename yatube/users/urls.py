from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.SignUp.as_view(), name="signup")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
