"""django CMS plugins that render existing portfolio data."""

from typing import Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from apps.portfolio.models import (
    AboutPluginModel,
    Certificate,
    DeveloperProfile,
    Education,
    EducationPluginModel,
    Experience,
    ExperiencePluginModel,
    FeaturedProjectsPluginModel,
    FeaturedSkillsPluginModel,
    HeroPluginModel,
    MiniProject,
    MiniProjectsPluginModel,
    Project,
    Skill,
    SkillCategoriesPluginModel,
    SkillCategory,
    SocialLink,
    SocialLinksPluginModel,
)

PLUGIN_MODULE = _("Портфолио")


@plugin_pool.register_plugin
class HeroPlugin(CMSPluginBase):
    model = HeroPluginModel
    name = _("Hero")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/hero.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: HeroPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        profile = DeveloperProfile.objects.first()
        context["profile"] = profile
        context["title"] = instance.title or (profile.full_name if profile else "")
        context["subtitle"] = instance.subtitle or (profile.headline if profile else "")
        context["intro"] = instance.intro or (profile.summary if profile else "")
        return context


@plugin_pool.register_plugin
class AboutPlugin(CMSPluginBase):
    model = AboutPluginModel
    name = _("Обо мне")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/about.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: AboutPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        profile = DeveloperProfile.objects.first()
        context["profile"] = profile
        if profile is None:
            context["body"] = ""
        elif instance.text_source == AboutPluginModel.TextSource.SUMMARY:
            context["body"] = profile.summary
        else:
            context["body"] = profile.biography or profile.summary
        return context


@plugin_pool.register_plugin
class SkillCategoriesPlugin(CMSPluginBase):
    model = SkillCategoriesPluginModel
    name = _("Категории навыков")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/skill_categories.html"
    filter_horizontal = ("categories",)
    cache = False

    def render(
        self, context: dict[str, Any], instance: SkillCategoriesPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        selected = instance.categories.all()
        categories = selected if selected.exists() else SkillCategory.objects.all()
        # One extra query for all skills instead of one per category.
        context["categories"] = categories.prefetch_related(
            Prefetch("skills", queryset=Skill.objects.all())
        )
        return context


@plugin_pool.register_plugin
class FeaturedSkillsPlugin(CMSPluginBase):
    model = FeaturedSkillsPluginModel
    name = _("Сетка избранных навыков")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/featured_skills.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: FeaturedSkillsPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        context["skills"] = Skill.objects.featured().select_related("category")[: instance.limit]
        return context


@plugin_pool.register_plugin
class FeaturedProjectsPlugin(CMSPluginBase):
    model = FeaturedProjectsPluginModel
    name = _("Избранные проекты")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/featured_projects.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: FeaturedProjectsPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        projects = Project.objects.published().with_related()
        if instance.only_featured:
            projects = projects.filter(is_featured=True)
        if instance.category_id:
            projects = projects.filter(category_id=instance.category_id)
        context["projects"] = projects[: instance.limit]
        return context


@plugin_pool.register_plugin
class MiniProjectsPlugin(CMSPluginBase):
    model = MiniProjectsPluginModel
    name = _("Мини-проекты")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/mini_projects.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: MiniProjectsPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        context["mini_projects"] = MiniProject.objects.active().select_related("category")[
            : instance.limit
        ]
        return context


@plugin_pool.register_plugin
class ExperiencePlugin(CMSPluginBase):
    model = ExperiencePluginModel
    name = _("Опыт работы")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/experience.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: ExperiencePluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        queryset = Experience.objects.all()
        if instance.show_technologies:
            queryset = queryset.prefetch_related("technologies")
        context["experiences"] = queryset[: instance.limit]
        return context


@plugin_pool.register_plugin
class EducationPlugin(CMSPluginBase):
    model = EducationPluginModel
    name = _("Образование")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/education.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: EducationPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        context["educations"] = Education.objects.all()[: instance.limit]
        context["certificates"] = (
            Certificate.objects.all() if instance.show_certificates else Certificate.objects.none()
        )
        return context


@plugin_pool.register_plugin
class SocialLinksPlugin(CMSPluginBase):
    model = SocialLinksPluginModel
    name = _("Социальные ссылки")
    module = PLUGIN_MODULE
    render_template = "portfolio/plugins/social_links.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: SocialLinksPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        context["links"] = SocialLink.objects.visible()
        return context
