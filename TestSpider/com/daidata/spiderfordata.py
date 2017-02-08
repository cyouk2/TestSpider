import urllib.request
import re
import os
import time
import pagefordata
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class SpiderFotData(object):
    
    def __init__(self):
        self.page = pagefordata.Page()
    
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def adddays(self, day):
        now = datetime.now()
        return (now + timedelta(days=day)).strftime('%Y-%m-%d')
    
    # Internet アクセス共通関数
    def requestPage(self, url):
        try:
            request = urllib.request.Request(urllib.parse.urlencode(url))
            response = urllib.request.urlopen(request)
            return response.read().decode("utf-8", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None
    
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
#         print(self.getCurrentTime(),"getUnitList:",url)
        page = self.requestPage(url)  
        if page:
            history = BeautifulSoup(str(page)).find_all(href=re.compile("%E5%8C%97%E6%96%97%E7%84%A1%E5%8F%8C.*?FWN"))
            for tailist in history:
                tainoList.append(BeautifulSoup(str(tailist)).a['href'])
            self.getTaiList(shopid, tainoList)
            
    #機種別で台情報リスト取得
    def getTaiList(self, shopid, lists):
        for tailist in lists:
            url = "http://daidata.goraggio.com" + tailist
            pageOfTaiList = self.requestPage(url)
            history = BeautifulSoup(str(pageOfTaiList)).find_all(href=re.compile("unit=.*?"))
            for tainoi in history:
                taino = BeautifulSoup(str(tainoi)).text
                for day in list(range(-7, 0)):
                    # 日付取得
                    target_date = self.adddays(day)
                    # 大当たり履歴詳細
                    url = "http://daidata.goraggio.com/" + shopid + "/detail/?unit=" + str(taino) + "&target_date=" + target_date
                    print(self.getCurrentTime(), "getTaiList:", url)
                    self.page.getDataOfOneDay(shopid, taino, target_date, self.requestPage(url))
    
    # main
    def getShopInfoByURL(self, areaid, pageid):
        url = "http://daidata.goraggio.com/?pref=" + areaid + "&page=" + str(pageid)
        page = self.requestPage(url)
        self.getShopIdList(page)

if __name__ == "__main__":
    objSpiderFotData = SpiderFotData()
    shopInfos = []
    filename = "area.txt"
    if os.path.exists(filename):
        f = open(filename, mode='r', encoding="utf-8", errors='ignore')
        for row in f:
            lista = row.rstrip().lstrip().split(",")
            areaName = lista[0]
            for pageid in lista[1:]:
                objSpiderFotData.getShopInfoByURL(areaName,pageid)
        f.close()


#         for i in [1, 2, 3]:
#             page = objSpiderFotData.getShopInfoByURL("%E6%9D%B1%E4%BA%AC%E9%83%BD", i)
#         
#         page = objSpiderFotData.getShopInfoByURL("%E5%8D%83%E8%91%89%E7%9C%8C", 1)
#         for i in [1, 2]:
#             page = objSpiderFotData.getShopInfoByURL("%E5%9F%BC%E7%8E%89%E7%9C%8C", i)

