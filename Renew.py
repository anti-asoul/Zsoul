import time

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service


class Renew:
    def __init__(self, driver, conf):
        self.driver = driver
        self.num = int(conf.get("RENEW", "tabs"))

    def refresh_tag(self):
        js1 = """
            function reload(timeout, current)     
            {      
                setTimeout('reload(timeout, current)', 1000 * timeout);    
                var fr4me = '<frameset cols=\\\'*\\\'>\\\n<frame src=\\\'' + current + '\\\' />';    
                fr4me += '</frameset>';
                with(document) {write(fr4me);void(close());};    
            }
        """
        js2 = """
                 timeout = 30;    
                 current = location.href;   
                if(timeout > 0)    
                {    
                    setTimeout('reload(timeout, current)', 1000 * timeout);    
                }
                else    
                {    
                    location.replace(current);  
                }
        """
        self.driver.execute_script("window.reload={}".format(js1))
        self.driver.execute_script(js2)

    def create_tag(self, url):
        self.driver.get(url)
        for i in range(self.num):
            time.sleep(5)
            self.driver.execute_script("window.open('{}')".format(url))
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.refresh_tag()
            self.driver.switch_to.window(self.driver.window_handles[0])
    # https://s.weibo.com/weibo?q=%23A-SOUL%E6%88%90%E5%91%98%E9%81%AD%E9%81%87%E5%85%AC%E5%8F%B8PUA%23

