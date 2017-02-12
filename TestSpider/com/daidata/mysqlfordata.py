# -*- coding:utf-8 -*-
import time
import mysql.connector
from mysql.connector import errorcode


class Mysql(object):
    
    def __init__(self):
        try:
            self.db= mysql.connector.connect(user='root', password='541880qw', host='127.0.0.1', database='beidou',charset='utf8')
            self.cur = self.db.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print(self.getCurrentTime(), "Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(self.getCurrentTime(), "Database does not exist")
            else:
                print(self.getCurrentTime(), "ERR:", err)
       
    # 获取当前时间
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))

    def insertData(self, table, my_dict):
        
        cols = ','.join(my_dict.keys())
        values = "','".join(my_dict.values())
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, "'" + values + "'")
        try:
            self.cur.execute(sql)
            self.db.commit()
            print(self.getCurrentTime(), "Database commit....SQL:", sql)
        except mysql.connector.Error as err:
            self.db.rollback()
            print(self.getCurrentTime(), "Database ROLLBACK....",  "ERR:", err, "...SQL:", sql)
        except Exception as err:
            print(self.getCurrentTime(), "ERR:", err)
    def getTainoInfoData(self):
        lists = []
        sql= "SELECT shop, taino FROM shopinfo"
        self.cur.execute(sql)
        for (shop, taino) in self.cur:
            lists.append((shop,taino))
        return lists
                
    def close(self):
        self.db.close()
mysqlobj = Mysql()
mysqlobj.getTainoInfoData()













