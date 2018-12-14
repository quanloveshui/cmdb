#encoding: utf-8

from django.urls import path

from . import views

app_name = 'host'

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/', views.delete, name='delete'),
    path('add/', views.add, name='add'),
    path('edit/(?P<id>\d+)/', views.edit, name='edit'),
    path('update/(?P<id>\d+)/', views.update, name='update'),
    path('addresult/', views.addresult, name='addresult'),
    path('detalinfo/(?P<id>\d+)/', views.detalinfo, name='detalinfo'),
]
