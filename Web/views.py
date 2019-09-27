# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
import Web.utils as utils
import Web.storage as storage
import json
import threading
import math
import operator


hack = {'Scientistin':utils.findExpertsScientistin,'THUCloud':utils.findExpertsTHUCloud,'Acemap':utils.findExpertsAcemap}
s = storage.Storage()

def findExperts(request):
    if request.user.is_authenticated:
        lock = threading.Lock()
        if request.method == 'POST':
            if request.path == '/api/find-experts-by-name':
                index = 'name'
            elif request.path == '/api/find-experts-by-domain':
                index = 'domain'
            elif request.path == '/api/find-experts-by-project':
                index = 'project'
            elif request.path == '/api/find-experts-by-patent':
                index = 'patent'
            elif request.path == '/api/find-experts-by-paper':
                index = 'paper'
            elif request.path == '/api/find-experts-by-tag':
                index = 'tag'
            elif request.path == '/api/find-experts-by-org':
                index = 'org'
            else:
                return HttpResponse("Request url error!")
            para = json.loads(request.body.decode())
            results = {'resultForm':[],'totalEntries':0,'currentPage':para['currentPage']}
            lock.acquire()
            result = s.get(para['condition'],index,para['sources'])
            lock.release()
            if result != None:
                start,end = utils.getStartAndEnd(para['size'],para['currentPage'],len(result))
                results['resultForm'] = result[start:end]
                results['totalEntries'] = len(result)
            else:
                if len(para['sources']) == 1:
                    result = hack[para['sources'][0]](para['condition'],index)
                elif len(para['sources']) == 2:
                    result = hack[para['sources'][0]](para['condition'],index)
                    result.extend(hack[para['sources'][1]](para['condition'],index))
                else:
                    result = hack[para['sources'][0]](para['condition'],index)
                    result.extend(hack[para['sources'][1]](para['condition'],index))
                    result.extend(hack[para['sources'][2]](para['condition'],index))           
                result = sorted(result,key=operator.itemgetter('originalrecommendation'),reverse=True)
                lock.acquire()    
                s.add(para['condition'],index,para['sources'],result)
                lock.release()
                start,end = utils.getStartAndEnd(para['size'],para['currentPage'],len(result))
                results['resultForm'] = result[start:end] 
                results['totalEntries'] = len(result)
            return JsonResponse(results)
        else:
            return HttpResponse("Request method error!")
    else:
        return HttpResponse("Please Login first!")

def expertDetail(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            para = json.loads(request.body.decode())
            result = {'expert':{}}
            if para["source"] == "Scientistin":
                result['expert'] = utils.expertsDetailScientistin(para['fetchId'])
            elif para["source"] == "THUCloud":
                result['expert'] = utils.expertsDetailTHUCloud(para['fetchId'])
            else:
                result['expert'] = utils.expertsDetailAcemap(para['fetchId'])
            return JsonResponse(result)
        else:
            return HttpResponse("Request method error!")
    else:
        return HttpResponse("Please Login first!")

def login(request):
    if request.method == 'POST':
        result = {"result":""}
        para = json.loads(request.body.decode())
        user = auth.authenticate(username=para['username'], password=para['password'])
        if user:
            auth.login(request, user)
            result["result"] = "登录成功"
        else:
            result["result"] = "登录失败"
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        result = {"result":"注销成功"}
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")

def register(request):
    if request.method == 'POST':
        result = {"result":""}
        para = json.loads(request.body.decode())
        try:
            _ = User.objects.get(username=para["username"])
            result["result"] = "用户名已存在"
        except:
            User.objects.create_user(username=para["username"], password=para["password"])
            result["result"] = "注册成功"
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")
