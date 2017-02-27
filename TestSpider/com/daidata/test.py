import os
import re
import time
import mysqlfordata
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def getCurrentTime():
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

def adddays(day):
    now = datetime.now()
    return (now + timedelta(days=day)).strftime('%Y-%m-%d')

# Internet アクセス共通関数
def requestPage(url):
    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        responsetxt = response.read().decode("utf-8", errors='ignore')
        return responsetxt
    except urllib.request.URLError as e:
        if hasattr(e, "code"):
            print(getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
            return None
        if hasattr(e, "reason"):
            print(getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
            return None
def downloadShopInfo(shopid, taino):
    dao = mysqlfordata.Mysql()
    dao.insertData("shopinfo", {"shop":str(shopid),"taino":str(taino)})   
         
def getShopInfoByURL(areaid, pageid):
    url = "http://daidata.goraggio.com/?pref=" + areaid + "&page=" + str(pageid)
    page = requestPage(url)
    getShopIdList(page)

#アリア別で店舗情報リスト取得      
def getShopIdList(page):
    shopidlist = []
    if page:
        history = BeautifulSoup(str(page)).find(id='sorter')
        shoplist = BeautifulSoup(str(history)).select("td > a")
        for shopinfo in shoplist:
            shopinfoStr = BeautifulSoup(str(shopinfo)).a['href']
            shopidlist.append(shopinfoStr[1:])
            getUnitList(shopinfoStr[1:])
    #店舗別で機種情報リスト取得
def getUnitList(shopid):
    tainoList = [] 
    url = "http://daidata.goraggio.com/" + str(shopid) + "/list/?type=2&f=1"
    print(getCurrentTime(),"getUnitList:",url)
    page = requestPage(url)  
    if page:
        history = BeautifulSoup(str(page)).find_all(href=re.compile("%E5%8C%97%E6%96%97%E7%84%A1%E5%8F%8C.*?FWN"))
        for tailist in history:
            tainoList.append(BeautifulSoup(str(tailist)).a['href'])
        getTaiList(shopid, tainoList)
#機種別で台情報リスト取得
def getTaiList(shopid, lists):
    for tailist in lists:
        url = "http://daidata.goraggio.com" + tailist
        print(getCurrentTime(),"getTaiList:",url)
        pageOfTaiList = requestPage(url)
        history = BeautifulSoup(str(pageOfTaiList)).find_all(href=re.compile("unit=.*?"))
        for tainoi in history:
            taino = BeautifulSoup(str(tainoi)).text
            downloadShopInfo(shopid, taino)
            
AreaInfos = []
filename = "areainfo.txt"
if os.path.exists(filename):
    dao = mysqlfordata.Mysql()
    dao.DeleteShopInfo() 
    f = open(filename, mode='r', encoding="utf-8", errors='ignore')
    for row in f:
        lista = row.rstrip().lstrip().split(",")
        areaName = urllib.parse.quote_plus(lista[0], encoding="utf-8")
        for pageid in lista[1:]:
            AreaInfos.append((areaName,pageid))
    f.close()
for areaName,pageid in AreaInfos:
    getShopInfoByURL(areaName,pageid)

            


