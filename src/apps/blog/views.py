"""Public blog views. Drafts are never reachable anonymously."""

from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.blog.models import Article, Category, Tag

ARTICLES_PER_PAGE = 10


def _render_list(
    request: HttpRequest,
    articles: Any,
    page_title: str,
    meta_description: str,
    **extra: Any,
) -> HttpResponse:
    page = Paginator(articles, ARTICLES_PER_PAGE).get_page(request.GET.get("page"))
    context: dict[str, Any] = {
        "page_obj": page,
        "articles": page.object_list,
        "categories": Category.objects.filter(articles__status="published").distinct(),
        "page_title": page_title,
        "meta_description": meta_description,
        **extra,
    }
    return render(request, "blog/article_list.html", context)


def article_list(request: HttpRequest) -> HttpResponse:
    return _render_list(
        request,
        Article.objects.published().with_related(),
        "Статьи",
        "Заметки о backend-разработке, AI/ML и инфраструктуре.",
    )


def category_detail(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug)
    return _render_list(
        request,
        Article.objects.published().with_related().filter(category=category),
        f"Статьи: {category.name}",
        category.description or f"Статьи в категории «{category.name}».",
        active_category=category,
    )


def tag_detail(request: HttpRequest, slug: str) -> HttpResponse:
    tag = get_object_or_404(Tag, slug=slug)
    return _render_list(
        request,
        Article.objects.published().with_related().filter(tags=tag),
        f"Статьи по тегу «{tag.name}»",
        f"Статьи, отмеченные тегом «{tag.name}».",
        active_tag=tag,
    )


def article_detail(request: HttpRequest, slug: str) -> HttpResponse:
    article = get_object_or_404(Article.objects.published().with_related(), slug=slug)
    context: dict[str, Any] = {
        "article": article,
        "related_articles": Article.objects.published()
        .with_related()
        .filter(category=article.category)
        .exclude(pk=article.pk)[:3]
        if article.category_id
        else Article.objects.none(),
        "page_title": article.seo_title or article.title,
        "meta_description": article.seo_description or article.excerpt,
    }
    return render(request, "blog/article_detail.html", context)
