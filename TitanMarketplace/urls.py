
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name="mainpage"),
    path('set-language/', views.set_language, name='set_language'),
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('about/', views.about, name="about"),
    re_path(r'^shop/', include(('shop.urls', 'shop'), namespace='shop')),
    path('profiles/', include('profiles.urls')),
    # path(r'markdownx/', include('markdownx.urls')),
    path('order/', include('order.urls')),
    path('tfidf/', include('tfidf.urls')),
    path('matrixfactorization/', include('matrixfactorization.urls')),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
