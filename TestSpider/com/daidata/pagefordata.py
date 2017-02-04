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
        history = BeautifulSoup(str(page)).select('table[class="numericValueTable"]')
        for tabledata in history:
            listTr = BeautifulSoup(str(tabledata)).find_all("tr")
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
        return listb
    
    def getDicData(self,  shopid, taino, target_date, lstas):
         
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
