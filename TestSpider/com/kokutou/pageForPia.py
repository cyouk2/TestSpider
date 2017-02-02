# -*- coding:utf-8 -*-
import urllib.request
import re
import time
import mysqlForSpider
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Page(object):
    
    def __init__(self):
        self.dao = mysqlForSpider.Mysql()
        
    # 時間計算
    def adddays(self, day):
        now = datetime.now()
        return (now + timedelta(days=day)).strftime('%Y%m%d')

    # 获取当前时间
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    # 通过页面的URL来获取页面的代码
    def getPageByURL(self, shop, day, lot_no):
        try:
            url = "http://p-ken.jp/p-jnaikebukuro/bonus/detail?ps_div=1&cost=4&model_nm=%82b%82q%90%5E%96k%93l%96%B3%91o%82e%82v%82m&day=1&lot_no=43&mode="
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            return response.read().decode("shift-jis", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "getPageByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "getPageByURL...ERRREASON:", e.reason)
                return None
            
    def getDataOfOneDay(self, shop, day, lot_no):
        lista = []
        pattern = re.compile('<tr><td align="left">(.*?)</td><td align="right">(.*?)</td><td align="right">(.*?)</td></tr>', re.S)
        # 該当ページのｈｔｍｌ文字列取得する
        page = self.getPageByURL(shop, day, lot_no)
        if page:
            index = 0
            history = BeautifulSoup(str(page)).find_all(id='history')
            listTr = BeautifulSoup(str(history)).find_all("tr")
            rowcounts = len(listTr)
            try:
                for strTr in listTr:
                    match = re.search(pattern, str(strTr))
                    if match:
                        my_dict = self.dao.getDicData(shop,
                                                      self.adddays(-day),
                                                      lot_no,
                                                      rowcounts - index,
                                                      match.group(1),
                                                      match.group(2),
                                                      match.group(3))
                        lista.append(my_dict)
                    index += 1
            finally:
                pass
            return lista
        else:
            pass
    
    # main function    
    def getAnswer(self, shop, lot_no):
        for day in range(0, 8):
            listOfPiaInfo = self.getDataOfOneDay(shop, day, lot_no)
            for my_dict in listOfPiaInfo:
                self.dao.insertData("piainfo", my_dict)
            lista = self.getPiaInfoTotal(listOfPiaInfo)
            for my_dict1 in lista:
                self.dao.insertData("piainfototal", my_dict1)
        return None
    
    def getPiaInfoTotal(self, listOfPiaInfo):
        lista = []
        bonusCount = 1
        lineIndex = 1
        dica = {"shop":"", "playdate":"", "taino":"", "lineno":"", "ballin":"", "bonus":""}

        for el in sorted(listOfPiaInfo, key=lambda x: int(x["lineno"])):
            bonuskind = el["bonuskind"]
            if str(bonuskind) == "確変初当たり" or str(bonuskind) == "通常" or str(bonuskind) == "初当たり":
                shop = dica["shop"]
                if shop:
                    lista.append(dica)
                    self.dao.insertData("piainfototal", dica)
                    bonusCount = 1
                    lineIndex += 1
                    dica = {"shop":"", "playdate":"", "taino":"", "lineno":"", "ballin":"", "bonus":""}
                dica["lineno"] = str(lineIndex)
                dica["bonus"] = str(bonusCount)
                dica["shop"] = el["shop"]
                dica["playdate"] = el["playdate"]
                dica["taino"] = el["taino"]
                dica["ballin"] = el["ballin"]
            else:
                bonusCount += 1
                dica["bonus"] = str(bonusCount)
        lista.append(dica)
        return lista
    
page = Page() 
page.getAnswer("p-jnaikebukuro", 41)
