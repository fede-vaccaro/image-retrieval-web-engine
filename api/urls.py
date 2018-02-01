from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^image_upload/', csrf_exempt(views.ImageUploadView.as_view())),
    url(r'^query_up/', views.query_up),
    # url(r'^image_list/', views.image_list),
    url(r'^image_list/', csrf_exempt(views.ImageListView.as_view())),
    url(r'^get_image/(?P<pk>[-\w]+)/$', views.get_image),
    # url(r'^explore/(?P<pk>[0-9]+)/$', views.explore),
    url(r'^explore/(?P<pk>[0-9]+)/$', csrf_exempt(views.ExploreView.as_view())),
    url(r'^query_get/(?P<img_name>[-\w]+)/$', csrf_exempt(views.QueryGetView.as_view())),
]
