from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("privacy/", views.privacy_policy, name="privacy"),
    path("cookies/", views.cookie_policy, name="cookies"),
]
