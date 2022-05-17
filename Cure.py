import random
import time

from selenium.webdriver.common.by import By


class Cure:
    def __init__(self, window, driver, conf):
        self.window = window
        self.browser = driver
        self.blackWords = conf.get("CURE", "blacklist")
        self.whiteList = conf.get("CURE", "whitelist")
        self.url = str(conf.get("CURE", "url"))
        self.conf = conf
        print(self.url)
        self.treatment = []
        for n in open("comments.txt", 'r', encoding='utf-8').readlines():
            self.treatment.append(n)
        self.window.signal.emit("话术加载完成")

    def getTreatment(self):
        return self.treatment[random.randint(0, len(self.treatment) - 1)]

    def skip(self, text):
        if len(text) > 120:
            # 认为是正常发帖
            return True
        for word in self.blackWords:
            if text.find(word) != -1:
                return True
        return False

    def shouldHelp(self, text):
        for word in self.whiteList:
            if text.find(word) != -1:
                return True
        return False

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
        for i in range(len(comments)):
            # self.window.signal.emit("===========================\n " + comments[i].text)
            if self.skip(comments[i].text) or not self.shouldHelp(comments[i].text):
                continue
            if comments[i].text.split("\n")[-2].find('评论') == 1:
                # 优先评论暂无评论的发布
                minP = i
                break
            currApprove = int(comments[i].text.split('\n')[-2].split(' ')[1])
            if currApprove < minApprove:
                minApprove = currApprove
                minP = i

        self.window.signal.emit("开始治疗 " + str(minP))
        comment = comments[minP]
        self.browser.execute_script("arguments[0].scrollIntoView();", comment)

        try:
            # 点赞
            comment.find_elements("class name", "pos")[3].click()
            self.window.signal.emit("点赞 " + comment.text.split('\n')[2])
            time.sleep(3)
            # 评论
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
            self.window.signal.emit("治疗失败")
            self.window.signal.emit("仅关注可评论")
            self.work()
