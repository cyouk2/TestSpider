# import asyncio
import mysqlfordata
import time
import pagefordata
import urllib.request
from datetime import datetime, timedelta

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
    pagetxt = requestPage(url)
    page.getDataOfOneDay(shopid, taino, target_date, pagetxt)

mysqlobj = mysqlfordata.Mysql()
listb = mysqlobj.getTainoInfoData()
listDataInfo = []
for shop, taino in listb:
    for day in list(range(-7, -6)):
        # 日付取得
        target_date = adddays(day)
        download(shop, taino, target_date)
#         listDataInfo.append((shop, taino, target_date))
# loop = asyncio.get_event_loop()
# tasks = [download(shopid, taino, target_date) for shopid, taino, target_date in listDataInfo]
# loop.run_until_complete(asyncio.wait(tasks))
# loop.close()