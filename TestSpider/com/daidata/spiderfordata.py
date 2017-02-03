import urllib.request
import re
import time
from bs4 import BeautifulSoup

class SpiderFotData(object):
    def __init__(self):
        pass
    
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    # requestPage
    def requestPage(self,url):
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            return response.read().decode("shift-jis", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None
            
    def getShopInfoByURL(self, areaid, pageid):
        url = "http://daidata.goraggio.com/?pref=" + areaid + "&page=" + str(pageid)
        page = self.requestPage(url)
        self.getShopIdList(page)
        
    def getShopIdList(self, page):
        shopidlist =[]
        if page:
            history = BeautifulSoup(str(page)).find(id='sorter')
            shoplist = BeautifulSoup(str(history)).select("td > a")
            for shopinfo in shoplist:
                shopinfoStr = BeautifulSoup(str(shopinfo)).a['href']
                shopidlist.append(shopinfoStr[1:])
                self.getUnitList(shopinfoStr[1:])

    def getUnitList(self, shopid):
        tainoList = [] 
        url = "http://daidata.goraggio.com/"+ str(shopid) +"/list/?type=2&f=1"
        print(self.getCurrentTime(), shopid,"getUnitList:",url)
        page = self.requestPage(url)  
        if page:
            history = BeautifulSoup(str(page)).find_all(href=re.compile("%E5%8C%97%E6%96%97%E7%84%A1%E5%8F%8C.*?FWN"))
            for tailist in history:
                tainoList.append(BeautifulSoup(str(tailist)).a['href'])
            self.getTaiList(shopid, tainoList)
        
    def getTaiList(self,shopid,lists):
        for tailist in lists:
            url = "http://daidata.goraggio.com" + tailist
            pageOfTaiList = self.requestPage(url)
            history = BeautifulSoup(str(pageOfTaiList)).find_all(href=re.compile("unit=.*?"))
            for tainoi in history:
                taino = BeautifulSoup(str(tainoi)).text
                url = "http://daidata.goraggio.com/" + shopid + "/detail/?unit=" + str(taino)
                print(self.getCurrentTime(),"getTaiList:",url)
          
    
#機種別で探す
#             with open("44.html", mode='r', encoding="utf-8", errors='ignore') as f:
#                 return f.read()
#http://daidata.goraggio.com/100196/detail/?unit=90
# %E6%9D%B1%E4%BA%AC%E9%83%BD 東京都
p = SpiderFotData()
page  = p.getShopInfoByURL("%E6%9D%B1%E4%BA%AC%E9%83%BD",1)
# p.getTaiList([])