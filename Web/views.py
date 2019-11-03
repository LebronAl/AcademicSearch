# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
import Web.utils as utils
import json
import math
import operator
import sqlite3


hack = {'Scientistin':utils.findExpertsScientistin,'THUCloud':utils.findExpertsTHUCloud,'Acemap':utils.findExpertsAcemap}

def findExperts(request):
    if request.user.is_authenticated:
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
            nameList = []
            result = []
            if len(para['sources']) == 1:
                result,nameList = hack[para['sources'][0]](para['condition'],index)
            elif len(para['sources']) == 2:
                result,nameList = hack[para['sources'][0]](para['condition'],index)
                r,a = hack[para['sources'][1]](para['condition'],index)
                result.extend(r)
                nameList = list(set(nameList).union(set(a)))
            else:
                result,nameList = hack[para['sources'][0]](para['condition'],index)
                r,a = hack[para['sources'][1]](para['condition'],index)
                result.extend(r)
                nameList = list(set(nameList).union(set(a)))
                r,a = hack[para['sources'][2]](para['condition'],index)
                result.extend(r)
                nameList = list(set(nameList).union(set(a)))           
            result = sorted(result,key=operator.itemgetter('originalrecommendation'),reverse=True)
            start,end = utils.getStartAndEnd(para['size'],para['currentPage'],len(result))
            results['nameList'] = nameList
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

def groupMatch(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            results = {"result":[]}
            para = json.loads(request.body.decode())
            MAX_EXPERT_NO = para["numberOfExpertsForEachProject"]
            MAX_ITEM_NO = para["maxNumberOfProjectsForEachExpert"]
            project = para["projects"]
            itemNumber = len(project)
            MAX_CONTAINER_NO = MAX_EXPERT_NO * int(itemNumber)
            count = 0
            items = []

            db = sqlite3.connect("./Web/THUCloud/thucloud.sqlite3")
            db_cousor = db.cursor()
            while(count < itemNumber):
                keywords = project[count]["keywords"]
                authors = project[count]["authors"]

                # 根据文章关键词查找相关专家，在查找的过程中可以计算关键词和专家的相关度
                all_experts = {}
                for k in keywords:
                    #single_keyword_experts = Inverted_index.objects.filter(keyword__contains = k)
                    db_cousor.execute('select * from inverted_index where keyword like "%' + k + '%"')
                    rs = db_cousor.fetchall()
                    single_keyword_experts = []
                    for r in rs:
                        single_keyword_experts.extend(r[2].split())
                    for e in single_keyword_experts:
                        if all_experts.__contains__(e):
                            all_experts[e] +=  float(1)/float(keywords.__len__())
                        else:
                            all_experts[e] = float(1)/float(keywords.__len__())
                sorted_experts = sorted(all_experts.items(), key=operator.itemgetter(1), reverse=True)
                sorted_experts = sorted_experts[0:MAX_CONTAINER_NO]


                #计算相关专家和文章作者的社交关系网
                recommendexperts = {}
                experts_for_sort = {}
                for se in sorted_experts:
                    relavance = 0
                    #计算推荐度：相关度 - 社交关系排斥度
                    recommendexperts[se[0]] = {'key_match':se[1],'rel_exclude':relavance,'recommend_degree':se[1]-relavance}
                    experts_for_sort[se[0]] = se[1]-relavance


                sorted_recommended_tuples = sorted(experts_for_sort.items(), key=operator.itemgetter(1), reverse=True)
                #进行归一化处理
                try:
                    MAX_RECOMMEND_DEGREE = sorted_recommended_tuples[0][1]
                except:
                    MAX_RECOMMEND_DEGREE = 1
                if MAX_RECOMMEND_DEGREE == 0:MAX_RECOMMEND_DEGREE = 1
                for expert in experts_for_sort:
                    experts_for_sort[expert] = float(experts_for_sort[expert])/float(MAX_RECOMMEND_DEGREE)
                sorted_recommended_tuples = sorted(experts_for_sort.items(), key=operator.itemgetter(1), reverse=True)

                items.append({'id':project[count]['id'],'keywords':keywords,'authors':authors,'experts':sorted_recommended_tuples,'expertdetail':recommendexperts,'solution':[],'MAX_RECOMMEND_DEGREE':MAX_RECOMMEND_DEGREE})
                count += 1
            #得到单个项目推荐度最高专家列表，计算群组匹配，使用贪心算法

            pointer  = [0]*int(itemNumber)
            history_experts = {}
            history_experts_detail = {}

            solutions = []
            #循环结束条件为 项目推荐数为MAX_EXPERT_NO，或者专家列表已经到头
            expert_no = 0 # 当前循环次数：每个项目的专家数
            while(True):
                no_expert = False
                #初始化指针
                item_no = 0 #此处指项目号
                if expert_no >= MAX_EXPERT_NO:
                    break
                for item in items:
                    while(True):
                        if pointer[item_no] >= item['experts'].__len__():
                            no_expert = True and no_expert
                            break
                        if not history_experts.__contains__(item['experts'][pointer[item_no]][0]):
                            break
                        if ((history_experts[item['experts'][pointer[item_no]][0]] < MAX_ITEM_NO)) and (item_no not in history_experts_detail[item['experts'][pointer[item_no]][0]]):
                            break
                        pointer[item_no] += 1
                    item_no += 1
                #如果专家都用完，那么跳出
                if no_expert:
                    break
                #完成每个项目推荐最多一个专家的过程
                #对冲突的项目排序，取推荐度高的放入解决方案,被抛弃的指针向右移动，在剩余的项目中进行排序，一直到每个项目都被放入解决方案
                step_solutions = {}          #这一轮的解决方案
                while(True):
                    #进行一轮的观察，放入解决方案
                    success  = True
                    item_no = 0                  #此处指项目号
                    now_face = {}                #现在的 专家-项目 列表
                    sorted_now_face = {}         #对当前每个指针指向的专家进行排序

                    for item in items:
                        while(True):
                            if pointer[item_no] >= item['experts'].__len__():
                                #no_expert = True and no_expert
                                break
                            if not history_experts.__contains__(item['experts'][pointer[item_no]][0]):
                                break
                            if ((history_experts[item['experts'][pointer[item_no]][0]] < MAX_ITEM_NO)) and (item_no not in history_experts_detail[item['experts'][pointer[item_no]][0]]):
                                break
                            pointer[item_no] += 1
                        item_no += 1

                    item_no = 0
                    #首先将最高推荐度的专家放入相关项目列表，对于没有得到推荐专家的项目，调整指针再进行比较，直至所有项目都得到了推荐专家或者专家已经用完
                    for item in items:
                        if step_solutions.__contains__(item_no) or pointer[item_no] >= item['experts'].__len__():
                            item_no += 1
                            continue
                        success = False #还有未完成的方案
                        expert = item['experts'][pointer[item_no]][0]
                        expert_recommend_degree = item['experts'][pointer[item_no]][1]

                        # now_face 的格式： {'expert1':{'item_no':'ex_recomm_degree','item_no':'ex_recomm_degree'}}
                        if now_face.__contains__(expert):
                            now_face[expert][item_no] = expert_recommend_degree
                        else:
                            now_face[expert] = {}
                            now_face[expert][item_no] = expert_recommend_degree
                        item_no += 1

                    #排序
                    for face in now_face:
                        sorted_now_face[face] = sorted(now_face[face].items(), key=operator.itemgetter(1), reverse=True)
                    #放入 solution 中
                    for expert in sorted_now_face:
                        step_solutions[sorted_now_face[expert][0][0]] = expert
                        if not history_experts.__contains__(expert):
                            history_experts[expert] = 1
                            history_experts_detail[expert] = [sorted_now_face[expert][0][0]]
                        else:
                            history_experts[expert] += 1
                            history_experts_detail[expert].append(sorted_now_face[expert][0][0])
                    if success:
                        break
                expert_no += 1
                #print step_solutions
                if step_solutions != {}:
                    solutions.append(step_solutions)
            db = sqlite3.connect("./Web/THUCloud/thucloud.sqlite3")
            db_cousor = db.cursor()
            for step_solution in solutions:
                for item_number in step_solution:
                    #print items[item_number]['solution']
                    #print items[item_number]['expertdetail'][step_solution[item_number]]
                    #print step_solution[item_number]
                    db_cousor.execute("select * from original where id = " + step_solution[item_number])
                    result = db_cousor.fetchone()
                    expert = {}
                    if result is not None:
                        expert["name"] = result[1]
                        expert["organization"] = result[2]
                        expert["keywords"] = result[3].split()
                        expert["repulsionIndex"] = str(0)
                        expert["keywordsMatchIndex"] = str(items[item_number]['expertdetail'][step_solution[item_number]]['key_match'])
                        expert["recommendIndex"] = str(items[item_number]['expertdetail'][step_solution[item_number]]['recommend_degree'])
                    items[item_number]['solution'].append({step_solution[item_number]:{'recommendation':items[item_number]['expertdetail'][step_solution[item_number]],'expertinfo':expert,'normalized':float(items[item_number]['expertdetail'][step_solution[item_number]]['recommend_degree'])/float(items[item_number]['MAX_RECOMMEND_DEGREE'])}})
            db.commit()
            db.close()
            result = []
            for item in items:
                tmp = []
                for i in item["solution"]:
                    for k in i:
                        tmp.append(i[k]['expertinfo'])
                result.append({"id":item["id"],"keywords":item["keywords"],"authors":item["authors"],"experts":tmp})
                
            results["result"] = result      
            return JsonResponse(results)
        else:
            return HttpResponse("Request method error!")
    else:
        return HttpResponse("Please Login first!")