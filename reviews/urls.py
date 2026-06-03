from django.urls import re_path
from .import views
app_name = "reviews"
urlpatterns = [
    re_path(r'^$',views.review_list,name='review_list'),
    re_path(r'^review/(?P<review_id>[0-9]+)/$', views.review_detail, name='review_detail'),
    re_path(r'^wine$', views.wine_list, name='wine_list'),
    re_path(r'^wine/(?P<wine_id>[0-9]+)/$', views.wine_detail, name='wine_detail'),
    re_path(r'^wine/(?P<wine_id>[0-9]+)/add_review/$', views.add_review, name='add_review'),
    re_path(r'^review/user/(?P<username>\w+)/$',views.user_review_list,name='user_review_list'),
    re_path(r'^review/user/$',views.user_review_list,name='user_review_list'),
    re_path(r'^recommendation/$', views.user_recommendation_list, name='user_recommendation_list'),
]
