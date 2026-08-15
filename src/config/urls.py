"""Root URL configuration.

Application sections live on stable prefixes; django CMS owns everything else
through its catch-all pattern, so editors can add pages without code changes.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import SITEMAPS
from apps.core.views import health, robots_txt

handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"

urlpatterns = [
    path("health/", health, name="health"),
    path("robots.txt", robots_txt, name="robots-txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("admin/", admin.site.urls),
    path("filer/", include("filer.urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

# Russian is the primary language and stays unprefixed; /en/ is ready to be
# switched on by publishing the English page tree.
urlpatterns += i18n_patterns(
    path("", include("apps.portfolio.urls", namespace="portfolio")),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("contacts/", include("apps.contact.urls", namespace="contact")),
    path("", include("apps.core.urls", namespace="core")),
    path("", include("cms.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
