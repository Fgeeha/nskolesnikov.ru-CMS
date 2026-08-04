"""CMS plugins: registration, rendering and data selection."""

import pytest
from cms.api import add_plugin, create_page
from cms.models import PageContent, Placeholder
from cms.plugin_pool import plugin_pool
from django.test import RequestFactory

pytestmark = pytest.mark.django_db

REGISTERED = [
    "HeroPlugin",
    "AboutPlugin",
    "SkillCategoriesPlugin",
    "FeaturedSkillsPlugin",
    "FeaturedProjectsPlugin",
    "MiniProjectsPlugin",
    "ExperiencePlugin",
    "EducationPlugin",
    "SocialLinksPlugin",
    "LatestArticlesPlugin",
    "ContactBlockPlugin",
    "CtaPlugin",
]


@pytest.fixture
def placeholder(db) -> Placeholder:
    """A placeholder attached to a real CMS page content object."""
    page = create_page(title="Тест", template="cms/home.html", language="ru", slug="test-page")
    page_content = PageContent.admin_manager.get(page=page, language="ru")
    page_content.rescan_placeholders()
    return Placeholder.objects.get_for_obj(page_content).get(slot="sections")


def render_plugin(placeholder: Placeholder, plugin_type: str, **data) -> str:
    """Render one plugin the way the CMS renderer does and return its HTML."""
    instance = add_plugin(placeholder, plugin_type, "ru", **data)
    plugin_class = plugin_pool.get_plugin(plugin_type)
    plugin = plugin_class(plugin_class.model, admin_site=None)

    request = RequestFactory().get("/")
    request.user = None
    context = {"request": request}
    context = plugin.render(context, instance, placeholder)

    from django.template.loader import render_to_string

    return render_to_string(plugin.render_template, context)


@pytest.mark.parametrize("plugin_type", REGISTERED)
def test_plugin_is_registered(plugin_type):
    assert plugin_pool.get_plugin(plugin_type) is not None


class TestPluginRendering:
    def test_hero_falls_back_to_profile(self, placeholder, profile):
        html = render_plugin(placeholder, "HeroPlugin")
        assert profile.full_name in html
        assert profile.headline in html

    def test_hero_overrides_win(self, placeholder, profile):
        html = render_plugin(placeholder, "HeroPlugin", title="Собственный заголовок")
        assert "Собственный заголовок" in html
        assert profile.full_name not in html

    def test_about_uses_biography(self, placeholder, profile):
        html = render_plugin(placeholder, "AboutPlugin", text_source="biography")
        assert profile.biography in html

    def test_about_uses_summary(self, placeholder, profile):
        html = render_plugin(placeholder, "AboutPlugin", text_source="summary")
        assert profile.summary in html

    def test_featured_skills_lists_featured_only(self, placeholder, skill, skill_category):
        from apps.portfolio.models import Skill

        Skill.objects.create(name="Скрытый", category=skill_category, is_featured=False)
        html = render_plugin(placeholder, "FeaturedSkillsPlugin")
        assert skill.name in html
        assert "Скрытый" not in html

    def test_featured_projects_hides_unpublished(self, placeholder, project, draft_project):
        draft_project.is_featured = True
        draft_project.save(update_fields=["is_featured"])
        html = render_plugin(placeholder, "FeaturedProjectsPlugin")
        assert project.title in html
        assert draft_project.title not in html

    def test_featured_projects_respects_limit(self, placeholder, project, project_category):
        from apps.portfolio.models import Project

        Project.objects.create(
            title="Второй избранный",
            slug="second-featured",
            summary="s",
            category=project_category,
            is_featured=True,
        )
        html = render_plugin(placeholder, "FeaturedProjectsPlugin", limit=1)
        assert html.count('class="card card--project"') == 1

    def test_skill_categories_shows_all_when_unselected(self, placeholder, skill):
        html = render_plugin(placeholder, "SkillCategoriesPlugin")
        assert skill.name in html

    def test_mini_projects_hides_inactive(self, placeholder, mini_project):
        from apps.portfolio.models import MiniProject

        MiniProject.objects.create(
            title="Выключен", slug="off", summary="s", url="https://example.com", is_active=False
        )
        html = render_plugin(placeholder, "MiniProjectsPlugin")
        assert mini_project.title in html
        assert "Выключен" not in html

    def test_experience_renders_technologies(self, placeholder, experience, skill):
        html = render_plugin(placeholder, "ExperiencePlugin", show_technologies=True)
        assert experience.position in html
        assert skill.name in html

    def test_education_hides_certificates_by_default(self, placeholder, education):
        html = render_plugin(placeholder, "EducationPlugin")
        assert education.program in html
        assert "Сертификаты" not in html

    def test_social_links_shows_visible_only(self, placeholder, social_link):
        from apps.portfolio.models import SocialLink

        SocialLink.objects.create(name="Скрытая", url="https://example.com", is_visible=False)
        html = render_plugin(placeholder, "SocialLinksPlugin")
        assert social_link.name in html
        assert "Скрытая" not in html

    def test_latest_articles_hides_drafts(self, placeholder, article, draft_article):
        html = render_plugin(placeholder, "LatestArticlesPlugin")
        assert article.title in html
        assert draft_article.title not in html

    def test_contact_block_can_hide_the_form(self, placeholder, profile):
        assert "<form" not in render_plugin(placeholder, "ContactBlockPlugin", show_form=False)

    def test_cta_renders_button(self, placeholder):
        html = render_plugin(
            placeholder, "CtaPlugin", button_label="Написать", button_url="/contacts/"
        )
        assert 'href="/contacts/"' in html
        assert "Написать" in html


class TestPluginCopyRelations:
    def test_skill_categories_selection_survives_copy(self, placeholder, skill_category):
        from apps.portfolio.models import SkillCategoriesPluginModel

        original = add_plugin(placeholder, "SkillCategoriesPlugin", "ru")
        original.categories.add(skill_category)

        copy = SkillCategoriesPluginModel.objects.create(
            placeholder=placeholder, plugin_type="SkillCategoriesPlugin", language="ru", position=2
        )
        copy.copy_relations(original)

        assert list(copy.categories.all()) == [skill_category]
