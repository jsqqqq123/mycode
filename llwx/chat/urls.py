from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^test/$', views.test, name='test'),
    url(r'^room/(?P<room_name>[^/]+)/$', views.room, name='room'),
    url(r'^admin/(?P<room_name>[^/]+)/$', views.admin, name='admin'),
    url(r'^adminchat/$', views.adminchat, name='adminchat'),
    url(r'^adminchat/getjunum/',views.juNumber, name='junumber'),
    url(r'^adminchat/getroomjunum/',views.getroomjunum, name='getroomjunum')
]
