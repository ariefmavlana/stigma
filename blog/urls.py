from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.post_list, name="post_list"),
    path("posts/<slug:slug>/", views.post_detail, name="post_detail"),
    path("category/<slug:slug>/", views.category_detail, name="category"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag"),
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
]
