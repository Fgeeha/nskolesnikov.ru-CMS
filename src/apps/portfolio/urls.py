from django.urls import path

from apps.portfolio import views

app_name = "portfolio"

urlpatterns = [
    path("about/", views.about, name="about"),
    path("projects/", views.project_list, name="project-list"),
    path("projects/<slug:slug>/", views.project_detail, name="project-detail"),
    path("tools/", views.mini_project_list, name="mini-project-list"),
    path("resume/", views.resume, name="resume"),
]
