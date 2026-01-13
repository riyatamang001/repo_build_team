from django.urls import path
from . import views

urlpatterns = [
    path('', views.assessment_home, name='assessment_home'),
    path('take/<int:assessment_id>/', views.take_assessment, name='take_assessment'),
    path('api/create/', views.create_assessment_api, name='create_assessment_api'),
]
