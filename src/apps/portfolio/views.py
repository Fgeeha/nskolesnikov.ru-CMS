"""Public portfolio views."""

from typing import Any

from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.portfolio.models import (
    Certificate,
    Education,
    Experience,
    MiniProject,
    Project,
    ProjectCategory,
    Skill,
    SkillCategory,
)

PROJECTS_PER_PAGE = 12


def about(request: HttpRequest) -> HttpResponse:
    """Extended profile page with the full skill matrix."""
    categories = SkillCategory.objects.prefetch_related(
        Prefetch("skills", queryset=Skill.objects.all())
    )
    context: dict[str, Any] = {
        "skill_categories": categories,
        "page_title": "Обо мне",
        "meta_description": "Специализация, стек технологий и подход к работе.",
    }
    return render(request, "portfolio/about.html", context)


def project_list(request: HttpRequest) -> HttpResponse:
    """Project catalogue with optional filtering by category slug."""
    projects = Project.objects.published().with_related()
    active_category = request.GET.get("category", "").strip()
    category = None
    if active_category:
        category = ProjectCategory.objects.filter(slug=active_category).first()
        if category is not None:
            projects = projects.filter(category=category)

    page = Paginator(projects, PROJECTS_PER_PAGE).get_page(request.GET.get("page"))
    context: dict[str, Any] = {
        "page_obj": page,
        "projects": page.object_list,
        "categories": ProjectCategory.objects.filter(projects__is_published=True).distinct(),
        "active_category": category,
        "page_title": "Проекты",
        "meta_description": "Каталог открытых проектов: backend, AI/ML, DevOps и инструменты.",
    }
    return render(request, "portfolio/project_list.html", context)


def project_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Single project page. Unpublished projects return 404."""
    project = get_object_or_404(Project.objects.published().with_related(), slug=slug)
    related = (
        Project.objects.published()
        .with_related()
        .filter(category=project.category)
        .exclude(pk=project.pk)[:3]
        if project.category_id
        else Project.objects.none()
    )
    context: dict[str, Any] = {
        "project": project,
        "related_projects": related,
        "page_title": project.seo_title or project.title,
        "meta_description": project.seo_description or project.summary,
    }
    return render(request, "portfolio/project_detail.html", context)


def mini_project_list(request: HttpRequest) -> HttpResponse:
    """Catalogue of small standalone web tools."""
    context: dict[str, Any] = {
        "mini_projects": MiniProject.objects.active().select_related("category"),
        "page_title": "Мини-проекты",
        "meta_description": "Небольшие веб-инструменты и эксперименты в браузере.",
    }
    return render(request, "portfolio/mini_project_list.html", context)


def resume(request: HttpRequest) -> HttpResponse:
    """Combined work experience, education and certificates."""
    context: dict[str, Any] = {
        "experiences": Experience.objects.prefetch_related("technologies"),
        "educations": Education.objects.all(),
        "certificates": Certificate.objects.all(),
        "page_title": "Опыт и образование",
        "meta_description": "Опыт работы, образование и сертификаты.",
    }
    return render(request, "portfolio/resume.html", context)
