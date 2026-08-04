"""Public views: status codes, visibility rules and SEO markup."""

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestPortfolioViews:
    def test_about_page_renders_skills(self, client, content, skill):
        response = client.get(reverse("portfolio:about"))
        assert response.status_code == 200
        assert skill.name in response.content.decode()

    def test_project_list_hides_unpublished(self, client, content, project, draft_project):
        body = client.get(reverse("portfolio:project-list")).content.decode()
        assert project.title in body
        assert draft_project.title not in body

    def test_project_list_filters_by_category(self, client, content, project, project_category):
        response = client.get(
            reverse("portfolio:project-list"), {"category": project_category.slug}
        )
        assert response.status_code == 200
        assert response.context["active_category"] == project_category

    def test_unknown_category_filter_shows_everything(self, client, content, project):
        response = client.get(reverse("portfolio:project-list"), {"category": "nope"})
        assert response.status_code == 200
        assert response.context["active_category"] is None
        assert project.title in response.content.decode()

    def test_project_detail_renders(self, client, content, project):
        response = client.get(project.get_absolute_url())
        assert response.status_code == 200
        assert project.summary in response.content.decode()

    def test_unpublished_project_detail_is_404(self, client, content, draft_project):
        assert client.get(draft_project.get_absolute_url()).status_code == 404

    def test_mini_project_list(self, client, content, mini_project):
        response = client.get(reverse("portfolio:mini-project-list"))
        assert response.status_code == 200
        assert mini_project.title in response.content.decode()

    def test_inactive_mini_project_is_hidden(self, client, content, mini_project):
        mini_project.is_active = False
        mini_project.save(update_fields=["is_active"])
        body = client.get(reverse("portfolio:mini-project-list")).content.decode()
        assert mini_project.title not in body

    def test_resume_lists_experience_and_education(self, client, content, experience, education):
        body = client.get(reverse("portfolio:resume")).content.decode()
        assert experience.position in body
        assert education.program in body


class TestBlogViews:
    def test_list_hides_drafts(self, client, content, article, draft_article):
        body = client.get(reverse("blog:article-list")).content.decode()
        assert article.title in body
        assert draft_article.title not in body

    def test_detail_renders(self, client, content, article):
        response = client.get(article.get_absolute_url())
        assert response.status_code == 200
        assert article.excerpt in response.content.decode()

    def test_draft_detail_is_404(self, client, content, draft_article):
        assert client.get(draft_article.get_absolute_url()).status_code == 404

    def test_category_page(self, client, content, article, blog_category):
        response = client.get(blog_category.get_absolute_url())
        assert response.status_code == 200
        assert article.title in response.content.decode()

    def test_tag_page(self, client, content, article, tag):
        response = client.get(tag.get_absolute_url())
        assert response.status_code == 200
        assert article.title in response.content.decode()

    def test_unknown_category_is_404(self, client, content):
        assert client.get("/blog/category/nope/").status_code == 404


class TestSeoMarkup:
    def test_canonical_and_description_present(self, client, content, project):
        body = client.get(project.get_absolute_url()).content.decode()
        canonical = f'<link rel="canonical" href="https://testserver{project.get_absolute_url()}"'
        assert canonical in body
        assert f'<meta name="description" content="{project.summary}"' in body

    def test_open_graph_tags_present(self, client, content):
        body = client.get(reverse("portfolio:project-list")).content.decode()
        assert 'property="og:title"' in body
        assert 'property="og:url"' in body
        assert 'name="twitter:card"' in body

    def test_single_h1_per_page(self, client, content, article):
        body = client.get(article.get_absolute_url()).content.decode()
        assert body.count("<h1") == 1

    def test_article_page_embeds_blogposting(self, client, content, article):
        assert "BlogPosting" in client.get(article.get_absolute_url()).content.decode()


class TestErrorPages:
    def test_unknown_url_returns_404(self, client, content):
        response = client.get("/definitely-missing/")
        assert response.status_code == 404
        assert "Страница не найдена" in response.content.decode()
