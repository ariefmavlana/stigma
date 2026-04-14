from django.urls import path
from . import views

app_name = "ai_crew"

urlpatterns = [
    path("generate/", views.generate_view, name="generate"),
    path("generate/status/<str:task_id>/", views.task_status_view, name="task_status"),
]
