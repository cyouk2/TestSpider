import asyncio
import os
import queue as Queue
from threading import Thread
import re
import time
import pagefordata
import urllib.request
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

THREADS = 3

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
def download(shopid, taino, target_date):
    page = pagefordata.Page()
    url = "http://daidata.goraggio.com/" + shopid + "/detail/?unit=" + str(taino) + "&target_date=" + target_date
    print(getCurrentTime(), "getTaiList:", url)
    page.getDataOfOneDay(shopid, taino, target_date, requestPage(url))
    
@asyncio.coroutine              
def getShopInfoByURL(areaid, pageid):
    url = "http://daidata.goraggio.com/?pref=" + areaid + "&page=" + str(pageid)
    page =  yield from requestPage(url)
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
            for day in list(range(-7, 0)):
                # 日付取得
                target_date = adddays(day)
                download(shopid, taino, target_date)

AreaInfos = []
filename = "area.txt"
if os.path.exists(filename):
    f = open(filename, mode='r', encoding="utf-8", errors='ignore')
    for row in f:
        lista = row.rstrip().lstrip().split(",")
        areaName = lista[0]
        for pageid in lista[1:]:
            AreaInfos.append((areaName,pageid))
    f.close()
loop = asyncio.get_event_loop()
tasks = [ getShopInfoByURL(areaName,pageid) for areaName,pageid in AreaInfos]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()

            


