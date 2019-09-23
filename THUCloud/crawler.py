import requests
import sqlite3
import threading

from bs4 import BeautifulSoup

class Crawler(threading.Thread):
    
    database_lock = threading.Lock()

    def __init__(self, page):
        threading.Thread.__init__(self)
        self.page = page
        
    def run(self):
        self.get_thucloud_session()
        self.original_experts_page()

    def get_thucloud_session(self):
        url = 'http://experts.thucloud.com:8000/'
        self.session = requests.Session()
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find('input', attrs={ 'name': 'csrfmiddlewaretoken' })['value']
        self.session.post(url, {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'test',
            'password': 'test'
        })

    def init_db(self):
        self.database_connect = sqlite3.connect("thucloud.sqlite3")
        print("成功连接数据库！")
        cursor = self.database_connect.cursor()
        try:
            cursor.execute('''
                CREATE TABLE original(
                    id           INT        PRIMARY KEY     NOT NULL,
                    name         TEXT,
                    organization TEXT,
                    keywords     TEXT,
                    papers       TEXT,
                    relations    TEXT
                );
            ''')
            cursor.execute('CREATE INDEX index_original ON original (name);')
            self.database_connect.commit()
            print("成功建表！")
        except:
            print("已存在目标表！")

    def del_db(self):
        self.database_connect.close()

    def original_experts_page(self):
        url = 'http://experts.thucloud.com:8000/experts/list/' + str(self.page)
        print('开始：', url)
        # 获取整页信息
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        experts = []
        expert = {
            'id': None,
            'name': '',
            'organization': '',
            'keywords': '',
            'papers': '',
            'relations': '',
            'detail_url': ''
        }
        count = 0
        for tag in soup.find_all('td'):
            mod = count % 3
            if mod == 0:
                expert['id'] = int(tag.string)
            elif mod == 1:
                expert['detail_url'] = 'http://experts.thucloud.com:8000' + tag.find('a')['href']
                expert['name'] = tag.string
            else:
                expert['organization'] = tag.string
                experts.append(expert)
                expert = {
                    'id': None,
                    'name': '',
                    'organization': '',
                    'keywords': '',
                    'papers': '',
                    'relations': '',
                    'detail_url': ''
                }
            count = count + 1
        # 获取详情
        for i in range(len(experts)):
            response = self.session.get(experts[i]['detail_url'])
            soup = BeautifulSoup(response.text, "html.parser")
            count = 0
            for tag in soup.find_all('td'):
                if tag.has_attr('colspan'):
                    mod = count % 3
                    if mod == 0:
                        experts[i]['keywords'] = tag.string
                    elif mod == 1:
                        experts[i]['papers'] = tag.string
                    else:                    
                        experts[i]['relations'] = tag.string
                    count = count + 1
        # 数据写入数据库
        Crawler.database_lock.acquire()
        self.init_db()
        for expert in experts:
            cursor = self.database_connect.cursor()
            try:
                # id           INT        PRIMARY KEY     NOT NULL,
                # name         TEXT,
                # organization TEXT,
                # keywords     TEXT,
                # papers       TEXT,
                # relations    TEXT
                cursor.execute(
                    'INSERT INTO original VALUES(' 
                    + str(expert['id']) + ',\'' 
                    + expert['name'] + '\',\'' 
                    + expert['organization'] + '\',\'' 
                    + expert['keywords'] + '\',\'' 
                    + expert['papers'] + '\',\'' 
                    + expert['relations'] + '\');'
                )
                self.database_connect.commit()
            except Exception as e:
                print(e)
        self.del_db()
        Crawler.database_lock.release()
        print('结束', url)
    
if __name__ == '__main__':
    for i in range(0, 46):
        threads = []    
        for i in range(i * 16 + 1, i * 16 + 16):
            crawler = Crawler(i)
            threads.append(crawler)
            crawler.start()
        for thread in threads:
            thread.join()
    print("主线程退出！")
