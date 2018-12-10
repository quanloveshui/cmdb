from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path(r'', views.ansible_index,name='ansible_index'),
    path(r'result/', views.ansible_api,name='ansible_api'),
    path(r'listhost/', views.display,name='display'),
]
