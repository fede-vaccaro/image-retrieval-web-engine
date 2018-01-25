from django.conf.urls import url
from . import views

urlpatterns = [
    # post views
    url(r'^add_image/', views.add_image, name='add_image'),
    url(r'^image_list/', views.image_list, name='image_list'),
    url(r'^query/', views.query, name='search'),
    url(r'^sorted/(?P<image_path>[-\w]+)/$', views.image_sorted, name='sorted'),
]
