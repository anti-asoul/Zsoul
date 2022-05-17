import random
import time

from selenium.webdriver.common.by import By


class Kill:
    def __init__(self, window, driver, conf):
        self.window = window
        self.browser = driver
        self.url = str(conf.get("KILL", "url"))
        self.conf = conf
        print(self.url)
        self.treatment = []
        for n in open("trashes.txt", 'r', encoding='utf-8').readlines():
            self.treatment.append(n)
        self.window.signal.emit("话术加载完成")
        self.comment_flag = False
        self.tran_flag = False

    def getTreatment(self):
        return self.treatment[random.randint(0, len(self.treatment) - 1)]

    def work(self):
        self.browser.get(self.url)
        self.browser.implicitly_wait(5)
        time.sleep(3)

        comments = self.browser.find_elements(By.CLASS_NAME, "WB_cardwrap")[1:]
        while len(comments) == 0:
            self.browser.implicitly_wait(3)
            comments = self.browser.find_elements(By.CLASS_NAME, "WB_cardwrap")[1:]
        if len(comments) > 10:
            comments = comments[:10]
        minApprove = 100
        minP = 0
        # self.window.signal.emit("comments length:" + str(len(comments)))

        self.window.signal.emit("开始轰炸 " + str(minP))
        comment = comments[minP]
        self.browser.execute_script("arguments[0].scrollIntoView();", comment)

        try:
            # 转发
            if self.tran_flag:
                comment.find_elements("class name", "pos")[0].click()
                comment.find_element(By.CSS_SELECTOR, "a.W_btn_a").click()
                self.window.signal.emit("转发 " + comment.text.split('\n')[2])
            time.sleep(3)
            # 评论
            if self.comment_flag:
                comment.find_elements("class name", "pos")[2].click()
                time.sleep(3)
                # 写入评论
                tmp = self.getTreatment()
                left = right = 0
                while right < len(tmp):
                    # 模拟手打
                    right = min(len(tmp), right + random.randint(1, 3))
                    comment.find_element(By.CSS_SELECTOR, "textarea.W_input").send_keys(tmp[left:right])
                    left = right
                    time.sleep(random.randint(1, 3) / 5)
                time.sleep(3)
                # 提交评论
                comment.find_element(By.CSS_SELECTOR, "a.W_btn_a").click()
                self.window.signal.emit("评论 " + comment.text.split('\n')[2])
        except Exception as e:
            e = e
            self.window.signal.emit("轰炸失败")
            self.window.signal.emit("仅关注可评论")
            self.work()
