# skills/urls.py
from django.urls import path
from . import views

app_name = "skills"

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('add/', views.add_skill, name='add_skill'),
    path('submit-assessment/', views.submit_assessment, name='submit_assessment'),
]
