
import os
import sys
import queue as Queue
from threading import Thread
import re
import json
import time

THREADS = 3

class DownloadWorker(Thread):
    
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def run(self):
        while True:
            shop = self.queue.get()
            self.download(shop)
            self.queue.task_done()
    def download(self,shop):
        print(self.getCurrentTime(),shop)
        pass
                
class CrawlerScheduler(object):

    def __init__(self, sites):
        self.sites = sites
        self.queue = Queue.Queue()
        self.scheduling()
        
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def scheduling(self):
        
        # 创建工作线程
        for areaName, pageid in self.sites:
            worker = DownloadWorker(areaName,pageid)
            #设置daemon属性，保证主线程在任何情况下可以退出
            worker.daemon = True
            worker.start()
            for site in self.sites:
                self.GetShopInfo(site[:1])
                
    def GetShopInfo(self,shop):
        self.GetShopInfos(shop)
        self.queue.join()
        
    def GetShopInfos(self,shop):
#         url = "aaaaaaaaaaaaaaa"
#         time.sleep(5)

        self.queue.put(shop)
        
        

if __name__ == "__main__":
    shopInfos = []
    filename = "area.txt"
    if os.path.exists(filename):
        f = open(filename, mode='r', encoding="utf-8", errors='ignore')
        for row in f:
            lista = row.rstrip().lstrip().split(",")
            areaName = lista[0]
            for pageid in lista[1:]:
                shopInfos.append((areaName,pageid))
        f.close()
    if len(shopInfos) > 0:
        CrawlerScheduler(shopInfos)

            


