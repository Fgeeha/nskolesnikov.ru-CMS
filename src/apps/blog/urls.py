from django.urls import path

from apps.blog import views
from apps.blog.feeds import LatestArticlesFeed

app_name = "blog"

urlpatterns = [
    path("", views.article_list, name="article-list"),
    path("feed/", LatestArticlesFeed(), name="feed"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag"),
    path("<slug:slug>/", views.article_detail, name="article-detail"),
]
