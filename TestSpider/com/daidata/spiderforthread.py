
import os
import queue as Queue
from threading import Thread
import re
import mysqlfordata
import time
import pagefordata
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

THREADS = 3

class DownloadWorker(Thread):
    
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.page = pagefordata.Page()
    
        # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
       
    # Internet アクセス共通関数
    def requestPage(self, url):
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            return response.read().decode("utf-8", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None
     

    def run(self):
        while True:
            shopid, taino, target_date = self.queue.get()
            self.download(shopid, taino, target_date)
            self.queue.task_done()
    
    def download(self, shopid, taino, target_date):
        
        url = "http://daidata.goraggio.com/" + shopid + "/detail/?unit=" + str(taino) + "&target_date=" + target_date
        print(self.getCurrentTime(), "getTaiList:", url)
        self.page.getDataOfOneDay(shopid, taino, target_date, self.requestPage(url))
               
class CrawlerScheduler(object):

    def __init__(self, sites):
        self.sites = sites
        self.queue = Queue.Queue()
        self.scheduling()
#         self.dao = mysqlfordata.Mysql()
        
    def adddays(self, day):
        now = datetime.now()
        return (now + timedelta(days=day)).strftime('%Y-%m-%d')
        
    # Internet アクセス共通関数
    def requestPage(self, url):
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            return response.read().decode("utf-8", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None
            
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def scheduling(self):
        
        # 创建工作线程
        for x in range(20):
            worker = DownloadWorker(self.queue)
            #设置daemon属性，保证主线程在任何情况下可以退出
            worker.daemon = True
            worker.start()
            for areaName, pageid in self.sites:
                self.getShopInfoByURL(areaName, pageid)
    
    def getShopInfoByURL(self, areaid, pageid):
        url = "http://daidata.goraggio.com/?pref=" + areaid + "&page=" + str(pageid)
        page = self.requestPage(url)
        self.getShopIdList(page)
    
    #アリア別で店舗情報リスト取得      
    def getShopIdList(self, page):
        shopidlist = []
        if page:
            history = BeautifulSoup(str(page)).find(id='sorter')
            shoplist = BeautifulSoup(str(history)).select("td > a")
            for shopinfo in shoplist:
                shopinfoStr = BeautifulSoup(str(shopinfo)).a['href']
                shopidlist.append(shopinfoStr[1:])
                self.getUnitList(shopinfoStr[1:])
        #店舗別で機種情報リスト取得
    def getUnitList(self, shopid):
        tainoList = [] 
        url = "http://daidata.goraggio.com/" + str(shopid) + "/list/?type=2&f=1"
        print(self.getCurrentTime(),"getUnitList:",url)
        page = self.requestPage(url)  
        if page:
            history = BeautifulSoup(str(page)).find_all(href=re.compile("%E5%8C%97%E6%96%97%E7%84%A1%E5%8F%8C.*?FWN"))
            for tailist in history:
                tainoList.append(BeautifulSoup(str(tailist)).a['href'])
            self.getTaiList(shopid, tainoList)
            self.queue.join()
    #機種別で台情報リスト取得
    def getTaiList(self, shopid, lists):
        for tailist in lists:
            url = "http://daidata.goraggio.com" + tailist
            print(self.getCurrentTime(),"getTaiList:",url)
            pageOfTaiList = self.requestPage(url)
            history = BeautifulSoup(str(pageOfTaiList)).find_all(href=re.compile("unit=.*?"))
            for tainoi in history:
                taino = BeautifulSoup(str(tainoi)).text
#                 self.dao.insertData("shopinfo", {"shop":str(shopid),"taino":str(taino)})   
                for day in list(range(-7, 0)):
                    # 日付取得
                    target_date = self.adddays(day)
                    self.queue.put((shopid, taino, target_date))
if __name__ == "__main__":
    AreaInfos = []
    filename = "areainfo.txt"
    if os.path.exists(filename):
        f = open(filename, mode='r', encoding="utf-8", errors='ignore')
        for row in f:
            lista = row.rstrip().lstrip().split(",")
            areaName = urllib.parse.quote_plus(lista[0], encoding="utf-8")
            for pageid in lista[1:]:
                AreaInfos.append((areaName,pageid))
        f.close()
    if len(AreaInfos) > 0:
        CrawlerScheduler(AreaInfos)

            


