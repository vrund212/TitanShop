from . import views
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'shop'


urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('about/', views.about, name="about"),
    path('assistant/', views.shopping_assistant, name='assistant'),
    re_path(r'^', include('django.contrib.auth.urls')),
    re_path(r'^oauth/', include('social_django.urls', namespace="social")),
    re_path(r'product_list/', views.product_list_category, name="list"),
    re_path(r'index/', views.index, name="shophome"),
    re_path(r'^$', views.index, name='product_list'),
    re_path(r'search/', views.search_list, name='query'),
    re_path(r'search-suggestions/', views.search_suggestions, name='search_suggestions'),
    # path('electronics/', views.electronics, name='query'),
    re_path(r'trending/', views.search_list, name='trending'),
    re_path(r'^(?P<category_slug>[-\w]+)/$', views.product_list_category, name='product_list_by_category'),
    re_path(r'^(?P<id>\d+)/(?P<slug>[-\w]+)/$', views.product_detail, name='product_detail'),
    re_path(r'^cat/(?P<subcategory_slug>[-\w]+)/$', views.product_list_subcategory, name='product_list_by_subcategory'),

    re_path(r'r/reviewlist/', views.review_list, name='review_list'),
    re_path(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    re_path(r'^product$', views.product_list, name='product_list'),
    re_path(r'^product/(?P<product_id>[0-9]+)/$', views.product_detail, name='product_detail'),
    re_path(r'^product/(?P<product_id>[0-9]+)/add_review/$', views.add_review, name='add_review'),
    re_path(r'^review/user/(?P<username>\w+)/$',views.user_review_list,name='user_review_list'),
    re_path(r'^review/user/$', views.user_review_list, name='user_review_list'),
    re_path(r'r/recommendation/', views.user_recommendation_list, name='user_recommendation_list'),



]

