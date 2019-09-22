# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import Web.utils as utils
import json

hack = {
    'name':{'Scientistin':utils.findExpertsByNameScientistin,'THUCloud':utils.findExpertsByNameTHUCloud,'Acemap':utils.findExpertsByNameAcemap},
    'domain':{'Scientistin':utils.findExpertsByDomainScientistin,'THUCloud':utils.findExpertsByDomainTHUCloud,'Acemap':utils.findExpertsByDomainAcemap},
    'project':{'Scientistin':utils.findExpertsByProjectScientistin,'THUCloud':utils.findExpertsByProjectTHUCloud,'Acemap':utils.findExpertsByProjectAcemap},
    'patent':{'Scientistin':utils.findExpertsByPatentScientistin,'THUCloud':utils.findExpertsByPatentTHUCloud,'Acemap':utils.findExpertsByPatentAcemap},  
    'paper':{'Scientistin':utils.findExpertsByPaperScientistin,'THUCloud':utils.findExpertsByPaperTHUCloud,'Acemap':utils.findExpertsByPaperAcemap},          
}

def findExperts(request):
    if request.method == 'POST':
        if(request.path == '/api/find-experts-by-name'):
            index = 'name'
        elif (request.path == '/api/find-experts-by-domain'):
            index = 'domain'
        elif (request.path == '/api/find-experts-by-project'):
            index = 'project'
        elif (request.path == '/api/find-experts-by-patent'):
            index = 'patent'
        elif (request.path == '/api/find-experts-by-paper'):
            index = 'paper'
        else:
            return HttpResponse("Request url error!")
        para = json.loads(request.body.decode())
        result = {'resultForm':[]}
        for i in para["sources"]:
            result['resultForm'].extend(hack[index][i](para[index]))
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")

def expertDetail(request):
    if request.method == 'POST':
        para = json.loads(request.body.decode())
        result = {'resultForm':[]}
        return JsonResponse(result)
    else:
        return HttpResponse("Request method error!")
