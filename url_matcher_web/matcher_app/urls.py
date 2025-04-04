from django.urls import path
from . import views

app_name = 'matcher_app'

urlpatterns = [
    path('', views.upload_csv, name='upload_csv'),
    path('results/<str:job_id>/', views.results, name='results'),
]
