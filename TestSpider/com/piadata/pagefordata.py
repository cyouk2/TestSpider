# -*- coding:utf-8 -*-
import time
import mysqlfordata
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import copy

class Page(object):
    
    def __init__(self):
        self.dao = mysqlfordata.Mysql()
    
    # time add
    def adddays(self, day):
        now = datetime.now()
        return (now + timedelta(days=day)).strftime('%Y%m%d')
    
    # 数値に変換する
    def stringToint(self, value):    
        try:
            return int(value)
        except Exception:
            return 0
    
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def getDataOfOneDay(self, shopid, taino, target_date, page):
        intplaydate = self.stringToint(target_date.replace('-',''))
        # 本日の大当たり履歴詳細
        listb = []
        # 最終スタート数
        lastStartNumToday = 0
        overviewTable = BeautifulSoup(str(page)).select('table[class="overviewTable"]')
        tdOfoverviewTable = BeautifulSoup(str(overviewTable)).find_all("td")
        if len(tdOfoverviewTable) > 3:
            lastStartNumToday = self.stringToint(BeautifulSoup(str(tdOfoverviewTable[2])).text)
        #print(lastStartNumToday)    
        # 本日の大当たり履歴詳細
        numericValueTable = BeautifulSoup(str(page)).select('table[class="numericValueTable"]')
        listTr = BeautifulSoup(str(numericValueTable)).find_all("tr")
        # 存在チェック
        if len(listTr) > 1:
            # 順位
            index = len(listTr) - 1
            # タイトルを除く >> listTr[1:]
            for trstr in listTr[1:]:
                
                listTr = BeautifulSoup(str(trstr)).find_all("td")
                # スータト
                ballin = self.stringToint(BeautifulSoup(str(listTr[1])).text)
                ballout = self.stringToint(BeautifulSoup(str(listTr[2])).text)
                strbonuskind = BeautifulSoup(str(listTr[3])).text
                intbonuskind = 2
                if strbonuskind == '通常':
                    intbonuskind = 1
#                 timeline =  BeautifulSoup(str(listTr[4])).text
#                 inttimeline = self.stringToint(timeline.replace(':', ''))
                # 当たり毎に情報を取得する
                my_dict = self.getDicData(shopid, taino, intplaydate, index, ballin, ballout, intbonuskind)
                listb.append(my_dict)
                index -= 1
        # ソート
        piaDataInfoDetailOfDay =sorted(listb,key=lambda x:int(x["lineno"]))
        # 最終スータト計算
        if len(piaDataInfoDetailOfDay) > 0:
            bonuskindtmp = piaDataInfoDetailOfDay[-1:][0]["bonuskind"]
            # 前回のボーナスが通常の場合
            if int(bonuskindtmp) == 1:
                lastStartNumToday += 100
            else:
                #確変の場合
                lastStartNumToday += 130
        
        # 降順
        for piaLineInfo in piaDataInfoDetailOfDay:
#             print(piaLineInfo)
            self.dao.insertData("piainfo", piaLineInfo)      
        # 集計関数へ渡す
        piaDataInfoTotal = self.getPiaDataInfoTotal(shopid, taino, intplaydate, piaDataInfoDetailOfDay, lastStartNumToday)
        for totalLineInfo in piaDataInfoTotal:
#             print(totalLineInfo)
            self.dao.insertData("piainfototal", totalLineInfo)
     
    #ライン毎に当たり情報を集計する
    def getPiaDataInfoTotal(self, shopid, taino, target_date, sortedListOfDataInfo, lastStartNumToday):
        listNormal = []
        # 全ての通常のラインデータを洗い出す
        for datainfo in sortedListOfDataInfo:
            if int(datainfo["bonuskind"]) == 1:
                listNormal.append(datainfo) 
        liste = []
        # ライン数を取得する
        rowCount = len(listNormal)
        # ライン毎にグループで分ける
        for i in list(range(rowCount)):
            #print(i)
            startIndex = int(listNormal[i]["lineno"]) - 1
            if i != rowCount - 1:
                if i + 1 < rowCount:
                    endIndex = int(listNormal[i + 1]["lineno"]) - 1
            
                groupDataInfo = sortedListOfDataInfo[startIndex:endIndex]
            else:
                groupDataInfo = sortedListOfDataInfo[startIndex:]
            liste.append(groupDataInfo)
        # ラウンド数集計関数を呼び出す
        piaDataInfoTotal = self.checkRounds(liste)
        dicForDataLine = {"shop" : str(shopid), "taino" : str(taino), "playdate" : str(target_date)}
        dicForDataLine.update({"ballin": str(lastStartNumToday)})
        dicForDataLine.update({"starttotal": str(lastStartNumToday)})
        dicForDataLine.update({"bonus": str(0)})
        dicForDataLine.update({"lineno": str(rowCount + 1)})
        dicForDataLine.update({"big16r": str(0)})
        dicForDataLine.update({"middle8r": str(0)})
        dicForDataLine.update({"small4r": str(0)})
        piaDataInfoTotal.append(dicForDataLine)
        # 前日の最終のスタート数をリストに設定する
        return piaDataInfoTotal
         
    def checkRounds(self, liste):
        listTotal =[]
        listTotalTmp =[]
        startTotal =0
        copiedNewList = copy.deepcopy(liste)
        for (indexOfGroup, groupsData) in enumerate(copiedNewList):
            
            big16r = 0
            middle8r = 1
            small4r = 0
            bonuscount = 1
            
            firstBonus = groupsData[:1][0]
            if len(groupsData) >= 2 :
                otherBonusList = groupsData[1:]
            else:
                otherBonusList = []
            
            startTotal = int(firstBonus["ballin"])
            ballin = int(firstBonus["ballin"])
            if indexOfGroup != 0:
                beforBonus = liste[indexOfGroup - 1][-1:][0]
                bonuskind = int(beforBonus["bonuskind"])
                if bonuskind == 1:
                    ballin += 100
                    startTotal += 100
                else:
                    ballin += 130
                    startTotal += 130
            for dataLine in otherBonusList:
                # ライン毎にボーナス計数
                bonuscount += 1
                # 回転数計数
                ballinOther = int(dataLine["ballin"])
                startTotal += ballinOther
                # R数チェック
                ballout = int(dataLine["ballout"])
                if ballout > 1800 :
                    big16r += 1
                elif ballout < 800:
                    small4r += 1
                else:
                    middle8r += 1
            firstBonus.update({"lineno":str(indexOfGroup + 1)})
            firstBonus.update({"ballin":str(ballin)})
            firstBonus.update({"bonus": str(bonuscount)})
            firstBonus.update({"big16r": str(big16r)})
            firstBonus.update({"middle8r": str(middle8r)})
            firstBonus.update({"small4r": str(small4r)})
            firstBonus.update({"starttotal": str(startTotal)})
            listTotalTmp.append(firstBonus)
        # 不要の項目を削除する
        for i in listTotalTmp:
            for key in ["bonuskind","ballout"]:
                del i[key]   
            listTotal.append(i)
        return listTotal
    
    def getDicData(self, shopid, taino, target_date, lineno, ballin, ballout, bonuskind):
        mydic = {
            "shop" : str(shopid),
            "taino" : str(taino),
            "playdate" : str(target_date),
            "lineno" : str(lineno),
            "ballin" :str(ballin),
            "bonuskind":str(bonuskind),
            "ballout":str(ballout)}
        return mydic

# 
# pagea = Page()
# with open("11.html", mode='r', encoding="utf-8", errors='ignore') as f:
#     pagea.getDataOfOneDay(999999, 112, '2017-2-10', f.read()) 