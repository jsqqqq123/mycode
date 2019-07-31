from django.shortcuts import render

# Create your views here.
#-*-  coding:utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
import subprocess
import json
import time
import os



@login_required
def index(req):
    chat_enable_list = ['one', 'two', 'three']
    return render(req, 'autowechat/index.html', {'chat_enable_list': chat_enable_list})



def test(req):
    return render(req, 'autowechat/test.html')


@api_view(['GET', 'POST'])
def jwttest(req):
    return HttpResponse("this page need token!")


def index_2(req):
    mypids = req.session.get('pid', {})
    request_pid = req.POST.get('request_id')
    print(request_pid)
    child1 = subprocess.Popen('/root/anaconda3/bin/python /home/mycode/itchattest.py', shell=True)
    print(child1)
    mypids[request_pid] = child1.pid
    time.sleep(1)
    return HttpResponse(json.dumps(mypids))


def get_enable_list(req):
    my_btton_list = ['first_1', 'first_2']
    return HttpResponse(json.dumps(my_btton_list))