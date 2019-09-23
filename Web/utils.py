import requests
import json
import random

ScientistinPrefix = "http://39.107.153.254/api/"
# 需要线程锁，暂时懒得做
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
                response['name'] = i['name'][0]
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
            response['name'] = res['data']['name'][0]
            try:
                response['organization'] = res['data']['org'].replace("<em>","").replace("</em>","")
            except:
                pass
            try:
                response['hIndex'] = res['data']['hIndex']
            except:
                pass
            temp = res['data']['domains']
            for i in range(len(temp)):
                    temp[i] = temp[i].replace("<em>","").replace("</em>","")
            response['domains'] = temp   
            response['sources'] = ['科学家在线']
            for i in res['data']['papers']:
                paper = {}
                try:
                    paper['publishYear'] = None
                    paper['url'] = None
                    paper['name'] = i['title']
                    paper['authors'] = None
                    paper['timesCited'] = None
                    paper['publication'] = None
                    paper['keywords'] = i['kws'].replace(";;",";")
                    paper['abstract'] = i['abs']
                    response['papers'].append(paper)
                except:
                    pass
            for i in res['data']['patents']:
                patent = {}
                try:
                    patent['name'] = i['title']
                    patent['publicationNumber'] = i['pubNum']
                    patent['applicationDate'] = None
                    patent['abstract'] = i['abs']
                    response['patents'].append(patent)
                except:
                    pass
            try:
                for i in res['data']['nps']:
                    project = {}
                    project['name'] = i['title']
                    project['keywords'] = i['kws']
                    project['leader'] = None
                    project['fund'] = None
                    project['organization'] = None
                    response['projects'].append(project)
            except:
                pass
            try:
                for i in res['data']['cps']:
                    project = {}
                    project['name'] = i['title']
                    project['keywords'] = None
                    project['leader'] = None
                    project['fund'] = None
                    project['organization'] = None
                    response['projects'].append(project)
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




def findExpertsAcemap(name,way):
    return []

def ExpertsDetailAcemap(name):
    return []


def findExpertsTHUCloud(name,way):
    return []

def expertsDetailTHUCloud(name):
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