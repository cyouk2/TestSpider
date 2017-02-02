import urllib.request
import re
import time
from bs4 import BeautifulSoup

class SipderForPia(object):
    
    def __init__(self):
        pass
    
    # getCurrentTime
    def getCurrentTime(self):
        return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
    
    def getShopInfoByURL(self, areaid, day, lot_no, model_nm):
        try:
            url = "http://p-ken.jp/store/?area=" + areaid  
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            return response.read().decode("shift-jis", errors='ignore')
        except urllib.request.URLError as e:
            if hasattr(e, "code"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRCODE:", e.code)
                return None
            if hasattr(e, "reason"):
                print(self.getCurrentTime(), "GetShopInfoByURL...ERRREASON:", e.reason)
                return None