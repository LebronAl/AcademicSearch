import requests
import json
import random
import sqlite3

ScientistinPrefix = "http://39.107.153.254/api/"
ScientistinCookie = "5HU1g5XJq43D5oGucyKe5lXkq10S4DiRgHuSIy9U4h85cm9c46twh5dCdXF-eh2v3Yt0710f8ZKC4FU3thCP3DCmtn7S8Ft77Ft3d4iEq6K-3EF-814vIEs_dIOa5HOW569vh1sWsFmXh43O"
AcemapPrefix = "https://dev.acemap.info/api/v1/thucloud/"

def findExpertsScientistin(name, way):
    responses = []
    nameList = [name]
    para = {'q':name,'range':way,'token':ScientistinCookie,'size':100,"withScore":1}
    res = json.loads(requests.get(ScientistinPrefix + "s",params=para,timeout=5).content.decode())
    if res['code'] != 130:
        if len(res['data']['talents']) == 0:
            return responses,nameList
        max = 0
        if way == 'name':
            max = res['data']['talents'][0]['hIndex']
        else:
            max = res['data']['scores'][0]
        if max == 0:
            max = 1
        num = 0
        for i in res['data']['talents']:
            if way == 'name':
                academic = 100 * (i['hIndex'] / max)
            else:
                academic = 100 * (res['data']['scores'][num] / max)
            num += 1
            response={'fetchId':None,'name':None,"organization":None,"domains":[],'sources':['Scientistin'], 'recommendation':format(academic,".2f"),"originalrecommendation":academic}
            response['fetchId'] = i['uri']
            try:
                response['name'] = i['name'][0].replace("<em>","").replace("</em>","")
            except:
                pass
            try:
                response['organization'] = i['org'].replace("<em>","").replace("</em>","")
            except:
                pass
            try: 
                temp = i['domains']
                for j in range(len(temp)):
                    temp[j] = temp[j].replace("<em>","").replace("</em>","")
                response['domains'] = temp    
            except:
                pass
            responses.append(response)
    return responses,nameList


def expertsDetailScientistin(uri):
    response = {'fetchId': None, 'name': None, 'organization': None, 'hIndex': None, 'domains': [], 'sources': [], 'papers': [], 'collaborators': [], 'patents': [], 'projects': [],'academic':0, 'normalization':0, 'recommendation':""}
    para = {'uri':uri,'token':ScientistinCookie}
    res = json.loads(requests.get(ScientistinPrefix + "t",params=para,timeout=5).content.decode())
    if res['code'] != 130:
        response['fetchId'] = res['data']['uri']
        # 默认返回第一个姓名
        try:
            response['name'] = res['data']['name'][0]
        except:
            pass
        try:
            response['organization'] = res['data']['org'].replace("<em>","").replace("</em>","")
        except:
            pass
        try:
            response['hIndex'] = res['data']['hIndex']
        except:
            pass
        try: 
            temp = res['data']['domains']
            for i in range(len(temp)):
                    temp[i] = temp[i].replace("<em>","").replace("</em>","")
            response['domains'] = temp   
            response['sources'] = ['Scientistin']
        except:
            pass
        try:
            for i in res['data']['papers']:
                try:
                    paper = {}
                    paper['publishYear'] = None
                    paper['url'] = None
                    paper['name'] = i['title']
                    paper['authors'] = None
                    paper['timesCited'] = None
                    paper['publication'] = None
                    if i['kws'] == "null":
                        paper['keywords'] = []
                    else:
                        paper['keywords'] = i['kws'].replace("；"," ").replace(";"," ").replace(","," ").replace("，"," ").split()
                    paper['abstract'] = i['abs']
                    response['papers'].append(paper)
                except:
                    pass
        except:
            pass
        try:
            for i in res['data']['patents']:
                try:
                    patent = {}
                    patent['name'] = i['title']
                    patent['publicationNumber'] = i['pubNum']
                    patent['applicationDate'] = None
                    patent['abstract'] = i['abs']
                    response['patents'].append(patent)
                except:
                    pass
        except:
            pass
        try:
            for i in res['data']['nps']:
                try:
                    project = {}
                    project['name'] = i['title']
                    if i['kws'] == "null":
                        project['keywords'] = []
                    else:
                        project['keywords'] = i['kws'].replace("；"," ").replace(";"," ").replace(","," ").replace("，"," ").split()
                    project['leader'] = None
                    project['fund'] = None
                    project['organization'] = None
                    response['projects'].append(project)
                except:
                    pass
        except:
            pass
        try:
            for i in res['data']['cps']:
                try:
                    project = {}
                    project['name'] = i['title']
                    project['keywords'] = None
                    project['leader'] = None
                    project['fund'] = None
                    project['organization'] = None
                    response['projects'].append(project)
                except:
                    pass
        except:
            pass
    para = {'uri':uri,'token':ScientistinCookie,'level':1}
    res = json.loads(requests.get(ScientistinPrefix + "co-authors",params=para,timeout=5).content.decode())
    if res['code'] != 130:
        for i in res['data']:
            author = {}
            try:
                author['name'] = i["name"]
                author['organization'] = i["org"]
                author['timesCollaborated'] = i["paperCoTimes"] + i["patentCoTimes"] + i["projectCoTimes"]
                author['hIndex'] = None
                response['collaborators'].append(author)
            except:
                pass
    return response


def findExpertsTHUCloud(name, way):
    responses = []
    try:
        db = sqlite3.connect("./Web/THUCloud/thucloud.sqlite3")
    except:
        print("THUCloud data lost!")
        return responses
    db_cousor = db.cursor()
    if way in ["name","domain","org","tag"]:
        if way == "name":
            db_cousor.execute("select * from original where name is '" + str(name).strip() + "'")
        elif way == "domain" or way == "tag":
            db_cousor.execute('select * from original where keywords like "%' + str(name).strip() + '%"')
        else:
            db_cousor.execute('select * from original where organization like "%' + str(name).strip() + '%"')
        results = db_cousor.fetchall()
        for result in results:
            response={'fetchId':None, 'name':None, "organization":None, "domains":[], 'sources':['THUCloud'], 'recommendation':"0.00","originalrecommendation":0}
            response['fetchId'] = result[0]
            response['name'] = result[1]
            response['organization'] = result[2]
            response['domains'] = result[3].split()
            responses.append(response)
    db.commit()
    db.close()
    nameList = [name]
    return responses,nameList

def expertsDetailTHUCloud(id):
    response = {'fetchId': None, 'name': None, 'organization': None, 'hIndex': None, 'domains': [], 'sources': ['THUCloud'], 'papers': [], 'collaborators': [], 'patents': [], 'projects': []}
    try:
        db = sqlite3.connect("./Web/THUCloud/thucloud.sqlite3")
    except:
        print("THUCloud data lost!")
        return response
    db_cousor = db.cursor()
    db_cousor.execute("select * from original where id = " + id)
    result = db_cousor.fetchone()
    if result is not None:
        response['fetchId'] = result[0]
        response['name'] = result[1]
        response['organization'] = result[2]
        response['domains'] = result[3].split()
    db.commit()
    db.close()
    return response

def findExpertsAcemap(name, way):
    responses = []
    para = {'condition':name,'page':1,'pagesize':200}
    res = json.loads(requests.post(AcemapPrefix + "find-experts-by-" + way, para, timeout=5).content.decode())
    for i in res['data']['resultForm']:
        response={'fetchId':i["fetchId"],'name':i["name"],"organization":", ".join(i["organization"]),"domains":i["domains"],'sources':['Acemap'], 'recommendation':format(100*i["recommendation"],".2f"),"originalrecommendation":100*i["recommendation"]}
        responses.append(response)
    nameList = res['data']['translationList']
    return responses,nameList

def expertsDetailAcemap(id):
    para = {'fetchId':id}
    res = json.loads(requests.post(AcemapPrefix + "expert", para,timeout=5).content.decode())
    if not res['data']['expert'].__contains__("papers"):
        res['data']['expert']['papers'] = []
    if not res['data']['expert'].__contains__("collaborators"):
        res['data']['expert']['collaborators'] = []
    if not res['data']['expert'].__contains__("patents"):
        res['data']['expert']['patents'] = []
    if not res['data']['expert'].__contains__("projects"):
        res['data']['expert']['projects'] = []
    res["data"]['expert']['sources'] = ["Acemap"]
    res["data"]['expert']['organization'] = ", ".join(res["data"]['expert']['organization'])
    return res['data']['expert']

def getStartAndEnd(limit, page, length):
    if (page - 1) * limit < 0:
        start = 0
    else:
        start = (page - 1) * limit
    if page * limit > length:
        end = length
    else:
        end = page * limit  
    if end < start:
        end = 0
        start = 0
    return start, end