import random
import time
import sys

from selenium.webdriver.common.by import By
sys.path.append("..")


class Kill:
    def __init__(self, window, wait, driver, conf):
        self.window = window
        self.wait = wait
        self.browser = driver
        self.url = str(conf.get("KILL", "url"))
        self.conf = conf
        print(self.url)
        self.treatment = []
        for n in open("src/trashes.txt", 'r', encoding='utf-8').readlines():
            self.treatment.append(n)
        self.window.signal.emit("黑话加载完成")
        self.comment_flag = False
        self.tran_flag = False

    def getTreatment(self):
        return self.treatment[random.randint(0, len(self.treatment) - 1)]

    @staticmethod
    def change_url(url):
        import sys
        BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        def url_processing(url):
            uid = url.split('/')[3]
            content_id = url.split('/')[-1]
            num1, num2, num3 = cut_numbers(content_id)
            converted_content_id = generate_content_id(num1, num2, num3)
            final_url = generate_pc_url(uid, converted_content_id)
            return final_url

        def cut_numbers(num):
            number_string = [str(digit) for digit in str(num)]
            number1 = format_deleting_extra_zero(''.join(str(x) for x in number_string[:2]))
            number2 = format_deleting_extra_zero(''.join(str(x) for x in number_string[2:9]))
            number3 = format_deleting_extra_zero(''.join(str(x) for x in number_string[9:16]))
            return number1, number2, number3

        def generate_content_id(num1, num2, num3):
            result1 = encode(num1, BASE62)
            result2 = encode(num2, BASE62).zfill(4)
            result3 = encode(num3, BASE62).zfill(4)
            final_result = result1 + result2 + result3
            return final_result

        def format_deleting_extra_zero(num):
            output = int(num)
            return output

        def generate_pc_url(uid, contentid):
            final_url = "https://weibo.com/" + uid + "/" + contentid
            return final_url

        def encode(num, alphabet):
            if num == 0:
                return alphabet[0]
            arr = []
            arr_append = arr.append
            _div_mod = divmod
            base = len(alphabet)
            while num:
                num, rem = _div_mod(num, base)
                arr_append(alphabet[rem])
            arr.reverse()
            return ''.join(arr)

        def decode(string, alphabet=BASE62):
            base = len(alphabet)
            str_len = len(string)
            num = 0
            idx = 0
            for char in string:
                power = (str_len - (idx + 1))
                num += alphabet.index(char) * (base ** power)
                idx += 1
            return num
        processed_url = url_processing(url)
        return processed_url

    def work(self):
        if self.window.create_text.text() != "" and self.window.manu_base.isChecked():
            self.url = self.window.create_text.text()
            self.browser.get(self.change_url(self.url))
            comment = wait.until(condition.element_to_be_clickable(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div['
                                                                             '2]/main/div[1]/div/div['
                                                                             '2]/article/footer/div/div[1]/div'))
            [comment.click() for i in range(2)]
            self.browser.implicitly_wait(2)
            time.sleep(3)

            send_comment = \
            self.browser.find_elements(By.XPATH, '//*[@id="composerEle"]/div[2]/div/div[1]/div/textarea')[0]
            send_comment.send_keys(self.getTreatment())
            self.browser.implicitly_wait(2)
            time.sleep(3)

            commit_comment = self.wait.until(condition.element_to_be_clickable(By.XPATH, '//*[@id="composerEle"]'
                                                                                '/div[2]/div/div[3]/div/button'))
            [commit_comment.click() for i in range(2)]
            self.browser.implicitly_wait(2)
            time.sleep(3)
            self.window.signal.emit("评论完成")

            tran_start = self.wait.until(condition.element_to_be_clickable(By.XPATH, '//*[@id="app"]/div[1]/div[2]/div['
                                                                                     '2]/main/div[1]/div/div[2]/article'
                                                                                     '/footer/div/div[2]/div'))
            [tran_start.click() for i in range(2)]
            self.browser.implicitly_wait(2)
            time.sleep(3)
            tran_button = \
                self.wait.until(condition.element_to_be_clickable(By.XPATH,  '//*[@id="composerEle"]/div[2]/div/'
                                                                             'div[3]/div/button'))
            [tran_button.click() for i in range(2)]
            self.browser.implicitly_wait(2)
            self.window.signal.emit("转发完成")

        else:
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
