from django.contrib import admin
from django.urls import path, include, re_path
from . import views

from django.conf import settings
from django.conf.urls.static import static
app_name = 'tfidf'

urlpatterns = [
    path('recommendation/', views.recommendation, name='recommendation'),
    re_path(r'^recommendations/', views.recommendation, name='recommendation'),
    path('detail/<int:id>', views.detail, name='detail'),
    path('home', views.post_list, name='home'),
    re_path(r'^cosrecommendations/', views.get_suggestions, name='cosrecommendation'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
