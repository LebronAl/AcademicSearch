# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import Web.utils as utils
import Web.storage as storage
import json

hack = {'Scientistin':utils.findExpertsScientistin,'THUCloud':utils.findExpertsTHUCloud,'Acemap':utils.findExpertsAcemap}

s = storage.Storage()

def findExperts(request):
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
        else:
            return HttpResponse("Request url error!")
        para = json.loads(request.body.decode())
        results = {'resultForm':[]}
        result = s.get(para['condition'],index)
        if result != None:
            results['resultForm'] = result
        else:
            if len(para['sources']) == 1:
                result = hack[para['sources'][0]](para['condition'],index)
            elif len(para['sources']) == 2:
                result = [i for i in utils.merge2(hack[para['sources'][0]](para['condition'],index),hack[para['sources'][1]](para['condition'],index))]
            else:
                result = [i for i in utils.merge3(hack[para['sources'][0]](para['condition'],index),hack[para['sources'][1]](para['condition'],index),hack[para['sources'][2]](para['condition'],index))]
            s.add(para['condition'],index,result)
            results['resultForm'] = result   
        return JsonResponse(results)
    else:
        return HttpResponse("Request method error!")

def expertDetail(request):
    if request.method == 'POST':
        para = json.loads(request.body.decode())
        result = {'resultForm':[]}
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")
