import requests
import json
import random
import sqlite3

ScientistinPrefix = "http://39.107.153.254/api/"
ScientistinCookie = ["qyJSh4FW3GFScH3ZgFdDg4CFs6vu4mcw0DBX53KH8yOH4Z8U4lGdzGm4zGF-eh2v3Yt0710f8ZKC4FU3thCP3DCmtn7S8Ft77Ft3d4iEq6K-3EF-8186IZ4VtIUF8D4Tr40K71CDqZBZd3FO",
    "5HU1g5XJq43D5oGucyKe5lXkq10S4DiRgHuSIy9U4h85cm9c46twh5dCdXF-eh2v3Yt0710f8ZKC4FU3thCP3DCmtn7S8Ft77Ft3d4iEq6K-3EF-814vIEs_dIOa5HOW569vh1sWsFmXh43O",
    "8nCWsY8o36N-gXGocYKZsYc_I1G6sjTuzH3yg5yZ73OGqXCv4G8a4G0mtGF-eh2v3Yt0710f8ZKC4FU3thCP3DCmtn7S8Ft77Ft3d4iEq6K-3EF-8183ql_D8DiRr1iSaydVz40W3msvtylO"]
AcemapPrefix = "1"

def findExpertsScientistin(name, way):
    responses = []
    while True:
        index = random.randint(0,len(ScientistinCookie)-1)
        para = {'q':name,'range':way,'token':ScientistinCookie[index],'size':100,"withScore":1}
        res = json.loads(requests.get(ScientistinPrefix + "s",params=para).content.decode())
        if res['code'] != 130:
            max = 0
            if way == 'name':
                sortType = 1
                max = res['data']['talents'][0]
            else:
                sortType = 0
                max = res['data']['scores'][0]
            if max == 0:
                max = 1
            num = 0
            for i in res['data']['talents']:
                if way == 'name':
                    academic = 100 * (i['hIndex'] / max)
                else:
                    academic = 100 * (res['data'][num] / max)
                num += 1
                response={'fetchId':None,'name':None,"organization":None,"domains":[],'sources':['Scientistin'], 'academic':format(academic,".2f")}
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
            break
        else:
            ScientistinCookie.remove(ScientistinCookie[index])
            if len(ScientistinCookie) == 0:
                break
    return responses 


def expertsDetailScientistin(uri):
    response = {'fetchId': None, 'name': None, 'organization': None, 'hIndex': None, 'domains': [], 'sources': [], 'papers': [], 'collaborators': [], 'patents': [], 'projects': [],'academic':0, 'normalization':0, 'recommendation':""}
    while True:
        index = random.randint(0,len(ScientistinCookie)-1)
        para = {'uri':uri,'token':ScientistinCookie[index]}
        res = json.loads(requests.get(ScientistinPrefix + "t",params=para).content.decode())
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
            break
        else:
            ScientistinCookie.remove(ScientistinCookie[index])
            if len(ScientistinCookie) == 0:
                break
    while True:
        index = random.randint(0,len(ScientistinCookie)-1)
        para = {'uri':uri,'token':ScientistinCookie[index],'level':1}
        res = json.loads(requests.get(ScientistinPrefix + "co-authors",params=para).content.decode())
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

            break
        else:
            ScientistinCookie.remove(ScientistinCookie[index])
            if len(ScientistinCookie) == 0:
                break
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
            academic = 0.7*random.randint(0,50)
            normalization = 0.3*(100/8*3)
            response={'fetchId':None, 'name':None, "organization":None, "domains":[], 'sources':['THUCloud'], 'academic':format(academic,'.2f'), 'normalization':format(normalization ,'.2f'), 'recommendation':""}
            response['fetchId'] = result[0]
            response['name'] = result[1]
            response['organization'] = result[2]
            response['domains'] = result[3].split()
            response['recommendation'] = format(academic + normalization , '.2f')
            response['originalrecommendation'] = normalization + academic
            responses.append(response)
    db.commit()
    db.close()
    return responses

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
    return []

def expertsDetailAcemap(name):
    return []


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