from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

app_name = 'profiles'


urlpatterns = [
    path('<slug:profile_slug>/change-password/', views.change_password, name="change-password"),
    path('<slug:profile_slug>/edit/', views.edit_profile, name="edit-profile"),
    path('<slug:profile_slug>/', views.profile, name="profile"),
    path('', views.profiles, name="profiles"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



