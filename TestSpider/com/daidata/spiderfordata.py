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
    
    def getShopInfoByURL(self, areaid):
        try:
#             url = "http://p-ken.jp/store/area/?area=" + areaid  
#             request = urllib.request.Request(url)
#             response = urllib.request.urlopen(request)
#             return response.read().decode("shift-jis", errors='ignore')
            with open("44.html", mode='r', encoding="utf-8", errors='ignore') as f:
                return f.read()
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None
    def getShopIdList(self, page):
        if page:
            pagelist = BeautifulSoup(str(page)).find_all(href=re.compile("page="))
            print(pagelist)
            history = BeautifulSoup(str(page)).find(id='sorter')
            shoplist = BeautifulSoup(str(history)).select("td > a")
            for shopinfo in shoplist:
                shopinfoStr = BeautifulSoup(str(shopinfo)).a['href']
                print(shopinfoStr[1:])
            
p = SpiderFotData()
page  = p.getShopInfoByURL(5)
p.getShopIdList(page)