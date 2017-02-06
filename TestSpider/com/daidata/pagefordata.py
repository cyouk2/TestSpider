# -*- coding:utf-8 -*-
import time
import mysqlfordata
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Page(object):
    
    def __init__(self):
        self.dao = mysqlfordata.Mysql()
    
    # time add
    def adddays(self, day):
        now = datetime.now()
        return (now + timedelta(days=day)).strftime('%Y%m%d')

    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def getDataOfOneDay(self, shopid, taino, target_date, page):
        listb = []
        # 累計スタート
        overviewTable = BeautifulSoup(str(page)).select('table[class="overviewTable3"]')
        tdOfoverviewTable = BeautifulSoup(str(overviewTable)).find_all("td")
        # 累計スタート
        print("累計スタート:", BeautifulSoup(str(tdOfoverviewTable[1])).text)
        # 前日最終スタート
        print("前日最終スタート:", BeautifulSoup(str(tdOfoverviewTable[3])).text)
        lastStartNum = BeautifulSoup(str(tdOfoverviewTable[3])).text
        if not lastStartNum:
            lastStartNum = str(0)
        # 本日の大当たり履歴詳細
        numericValueTable = BeautifulSoup(str(page)).select('table[class="numericValueTable"]')
        listTr = BeautifulSoup(str(numericValueTable)).find_all("tr")
        if len(listTr) > 1:
            index = len(listTr) - 1
            for trstr in listTr[1:]:
                lista = []
                listTr = BeautifulSoup(str(trstr)).find_all("td")
                for td in listTr:
                    txt = BeautifulSoup(str(td)).text
                    if txt == "-":
                        lista.append(index)
                    else:
                        lista.append(txt)
                index -= 1
                my_dict = self.getDicData(shopid, taino, target_date, lista)
                self.dao.insertData("piainfo", my_dict)
                listb.append(my_dict)  
        self.getPiaDataInfoTotal(shopid, taino, target_date, listb, lastStartNum)
        
    def getPiaDataInfoTotal(self, shopid, taino, target_date, listb, lastStartNum):
        
        listd = []
        # ボーナス計数
        bonuscount = 0
        # ラインNo
        lineno = 0
        # ループ
        dicForDataLine = {"shop" : str(shopid), "taino" : str(taino), "playdate" : str(target_date)}
        for index, dataLine in enumerate(sorted(listb, key=lambda x: int(x["lineno"]))):
            bonuscount += 1
            if str(dataLine["bonuskind"]) == "通常":
                lineno += 1
                if not index == 0:
                    # 行を追加
                    listd.append(dicForDataLine)
                    bonuscount = 1
                    dicForDataLine = {"shop" : str(shopid), "taino" : str(taino), "playdate" : str(target_date)}
                dicForDataLine.update({"ballin": dataLine["ballin"]})
            dicForDataLine.update({"bonus": str(bonuscount)})
            dicForDataLine.update({"lineno": str(lineno)})
        # 最後に行を追加
        dicForDataLine.update({"bonus": str(bonuscount)})
        dicForDataLine.update({"lineno": str(lineno)})
        listd.append(dicForDataLine)
        
        dicForDataLine = {"shop" : str(shopid), "taino" : str(taino), "playdate" : str(target_date)}
        dicForDataLine.update({"ballin": lastStartNum})
        dicForDataLine.update({"bonus": str(0)})
        dicForDataLine.update({"lineno": str(0)})
        listd.append(dicForDataLine)
        for totalLineInfo in listd:
            self.dao.insertData("piainfototal", totalLineInfo)        
        
    def getDicData(self, shopid, taino, target_date, lstas):
        mydic = {
            "shop" : str(shopid),
            "taino" : str(taino),
            "playdate" : str(target_date),
            "lineno" : str(lstas[0]),
            "timeline" : str(lstas[4]),
            "ballin" :str(lstas[1]),
            "bonuskind":str(lstas[3]),
            "ballout":str(lstas[2])}
        return mydic
