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
        para = {'q':name,'range':way,'token':ScientistinCookie[index],'size':100}
        res = json.loads(requests.get(ScientistinPrefix + "s",params=para).content.decode())
        if res['code'] != 130:
            for i in res['data']['talents']:
                response={'fetchId':None,'name':None,"organization":None,"domains":[],'sources':['科学家在线']}
                response['fetchId'] = i['uri']
                try:
                    response['name'] = i['name'][0]
                except:
                    pass
                try:
                    response['organization'] = i['org'].replace("<em>","").replace("</em>","")
                except:
                    pass
                try: 
                    temp = i['domains']
                    for i in range(len(temp)):
                        temp[i] = temp[i].replace("<em>","").replace("</em>","")
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
    response = {'fetchId': None, 'name': None, 'organization': None, 'hIndex': None, 'domains': [], 'sources': [], 'papers': [], 'collaborators': [], 'patents': [], 'projects': []}
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
                response['sources'] = ['科学家在线']
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
                    author['timesCollaborated'] = i["paperCoTimes"]
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
            index = "name"
        elif way == "domain" or way == "tag":
            index = "keywords"
        else:
            index = "organization"
        db_cousor.execute("select * from original where " + index + ' like "%' + str(name).strip() + '%"')
        results = db_cousor.fetchall()
        for result in results:
            response={'fetchId':None,'name':None,"organization":None,"domains":[],'sources':['THUCloud']}
            response['fetchId'] = result[0]
            response['name'] = result[1]
            response['organization'] = result[2]
            response['domains'] = result[3].split()
            responses.append(response)
    db.commit()
    db.close()
    return responses

def expertsDetailTHUCloud(id):
    response = {'fetchId': None, 'name': None, 'organization': None, 'hIndex': None, 'domains': [], 'sources': [], 'papers': [], 'collaborators': [], 'patents': [], 'projects': []}
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


def merge2(a, b):
    alen, blen = len(a), len(b)
    mlen = min(alen, blen)
    for i in range(mlen):
        yield a[i]
        yield b[i]

    if alen > blen:
        for i in range(mlen, alen):
            yield a[i]
    else:
        for i in range(mlen, blen):
            yield b[i]

def merge3(a, b, c):
    alen, blen, clen = len(a), len(b), len(c)
    mlen = min(alen, blen, clen)
    for i in range(mlen):
        yield a[i]
        yield b[i]
        yield c[i]
        
    if mlen == clen:
        res = [i for i in merge2(a[mlen:],b[mlen:])]
    elif mlen == blen:
        res = [i for i in merge2(a[mlen:],c[mlen:])]
    else:
        res = [i for i in merge2(a[mlen:],b[mlen:])]
    for i in range(len(res)):
        yield res[i]
