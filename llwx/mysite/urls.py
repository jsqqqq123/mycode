"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import index, agentlist, oplists, searchuser, charge, addcharge, getuser, getqcorde, mysetting, xiafen, reducecharge, addrobot, robot, robotset, ubi, cbi, bacchange, message_set, changepd, cbiubi


urlpatterns = [
    path(r'accounts/', include('django.contrib.auth.urls')),
#    path(r'autowechat/', include('autowechat.urls')),
    path(r'chat/', include('chat.urls')),
    path(r'myauth/', include('myauth.urls')),
    path(r'admin/', admin.site.urls),
    path(r'myapi/', include('myapi.urls')),
#    path(r'tfball/', include('tfball.urls')),
    url(r'^$', index, name='index'),
    url(r'^agent/$', agentlist, name='agent'),
    url(r'^oplists/$', oplists, name='oplists'),
    url(r'^searchuser/$', searchuser, name='searchuser'),
    url(r'^charge/$', charge, name='charge'),
    url(r'^addcharge/$', addcharge, name='addcharge'),
    url(r'^getuser/$', getuser, name='addcharge'),
    url(r'^getqcorde/$', getqcorde, name='getqcorde'),
    url(r'^xiafen/$', xiafen, name='xiafen'),
    url(r'^reducecharge/$', reducecharge, name='reducecharge'),
    url(r'^robot/$', robot, name='robot'),
    url(r'^addrobot/$', addrobot, name='addrobot'),
    url(r'^robotset/$', robotset, name='robotset'),
    url(r'^ubi/$', ubi, name='ubi'),
    url(r'^cbi/$', cbi, name='cbi'),
    url(r'^mysetting/$', mysetting, name='mysetting'),
    url(r'^bacchange/$', bacchange, name='bacchange'),
    url(r'^message_set/$', message_set, name='message_set'),
    url(r'^changepd/$', changepd, name='changepd'),
    url(r'^crontab/cbiubi/', cbiubi, name='cbiubi'),
]
