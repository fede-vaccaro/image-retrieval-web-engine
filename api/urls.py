from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^image_upload/', csrf_exempt(views.ImageUploadView.as_view())),
    url(r'^query/', views.query),
    url(r'^image_list/', views.image_list),
    url(r'^get_image/(?P<pk>[-\w]+)/$', views.get_image)
]
