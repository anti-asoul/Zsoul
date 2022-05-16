import json
from datetime import time
import requests
from requests.cookies import cookiejar_from_dict


class Black:
    def __init__(self, window, driver, conf, session):
        self.window = window
        self.driver = driver
        self.session = session
        self.blacklist_ids = json.loads(conf.get("KILL", "blacklist"))
        self.headers = {
            'origin': 'https://weibo.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/99.0.4844.51 Safari/537.36',
        }

    def run(self):
        url = 'https://weibo.com/aj/filter/block?ajwvr=6'
        pbar = self.blacklist_ids
        for uid in pbar:
            if not uid: continue
            self.window.signal.emit(f'正在处理用户{uid}')
            data = {
                'uid': uid,
                'filter_type': '1',
                'status': '1',
                'interact': '1',
                'follow': '1',
            }
            self.headers['referer'] = f'http://weibo.com/u/{uid}'
            with open("cookies.pkl", "r") as f:
                cookie = json.load(f)
            cookie_done = {}
            for c in cookie:
                cookie_done[c['name']] = c['value']
            cookie = cookiejar_from_dict(cookie_done)
            response = requests.get(url, data=data, headers=self.headers, cookies=cookie)
            if response.json()['code'] != '100000':
                self.window.signal.emit(f'拉黑用户{uid}失败'+","+"{0}".format(response.json()['code']))
