from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
#    url(r'myloginapi', views.myloginapi, name='myloginapi'),
#    url(r'myregisterapi', views.myRegisterapi, name='myregisterapi'),
     url(r'test', views.test, name='test'),
]
