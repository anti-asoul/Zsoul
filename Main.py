import configparser
import json
import os
import sys
import time

import pygame
import requests
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QMouseEvent, QMovie
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QCheckBox, QLineEdit, QTextEdit
from rich.console import Console
from rich.progress import track
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import EdgeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as condition
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# from Cure import WeiboSpider
from utils.Bomb import Black
from utils.Cure import Cure
from utils.Kill import Kill
from utils.Renew import Renew

base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
config_path = os.path.join(base_path, "conf.ini")
conf = configparser.ConfigParser()
conf.read(config_path, encoding="utf-8")
session, info_return = None, None

import threading

_stop_event = threading.Event()



def stop():
    global _stop_event
    _stop_event.set()


def stopped():
    return _stop_event.is_set()


class Blogger:

    @staticmethod
    def bar(second):
        def count(sec):
            do = track(range(sec), description="正在获取二维码")
            for i in do:
                time.sleep(0.1)
                pass

        thread = threading.Thread(target=count, args=(second,))
        thread.start()

    @staticmethod
    def hide():
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument('--disable-gpu')
        options.add_argument('--hide-scrollbars')
        options.add_argument('blink-settings=imagesEnabled=false')
        options.add_argument("--headless")
        options.add_argument('window-size=1920x1080')
        options.add_argument('--start-maximized')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        options.add_argument("-inprivate")
        return options

    @staticmethod
    def open_browser(url):
        driver.get(url)

    # @staticmethod
    # def localize_scanner():
    #     global info_return, session
    #     log = Login()
    #     weibo = log.weibo(reload_history=True)
    #     info_return, session = weibo.login('me','pass', mode='scanqr')
    #
    # @staticmethod
    # def login_operator(name, password):
    #     global info_return, session
    #     log = Login()
    #     weibo = log.weibo(reload_history=True)
    #     info_return, session = weibo.login(name, password, mode='pc')
    #     return info_return, session
    def localize_scanner(self):
        self.open_browser("https://weibo.com/login.php")
        QR_tab = wait.until(condition.element_to_be_clickable((By.XPATH, '//*[@id="pl_login_form"]'
                                                                         '/div/div[1]/div/a[2]')))
        [QR_tab.click() for i in range(2)]
        QR = wait.until(condition.presence_of_element_located((By.CSS_SELECTOR, "#pl_login_form > div > "
                                                                                "div.login_content > img")))
        QR_url = 'about:blank;'

        while 'blank;' in QR_url:
            QR_url = QR.get_attribute("src")
            time.sleep(1)

        if 'blank;' not in QR_url:
            pics = requests.get(QR_url)
            file_name = r'Img\{}.jpg'.format("Login")
            with open(file_name, 'wb') as f:
                f.write(pics.content)

    def login_operator(self, names, passwords):
        self.open_browser("https://passport.weibo.cn/signin/login")
        name_tag = wait.until(condition.presence_of_element_located((By.CSS_SELECTOR, "input[id='loginName']")))
        name_tag.clear()
        name_tag.send_keys(names)
        password_tag = wait.until(condition.presence_of_element_located((By.CSS_SELECTOR,
                                                                         "input[id='loginPassword']")))
        password_tag.clear()
        password_tag.send_keys(passwords)
        login_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR, "a[id='loginAction']")))
        [login_button.click() for i in range(2)]
        # print(driver.current_url)
        while "signin" in driver.current_url:
            try:
                time.sleep(6)
                if len(driver.find_elements(By.XPATH, '//*[@id="errorMsg"]')) != 0:
                    console.print("用户名或密码错误")
                    login()
                    break
                else:
                    if "first_enter" in driver.current_url or "secondverify" in driver.current_url:
                        # print(driver.current_url)
                        verify_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                      "div.my-btn-box a")))
                        [verify_button.click() for i in range(2)]
                        verify_tag = wait.until(
                            condition.presence_of_element_located((By.CSS_SELECTOR, '//*[@id="verifyCode"]'
                                                                                    '/div[1]/div/div/div[2]'
                                                                                    '/div/div/div/span[1]/input'))
                        )
                        # change to UI interaction
                        codes = console.input("请输入验证码: ")
                        verify_tag.send_keys(codes)
                        done_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                    "div.my-btn-box a")))
                        [done_button.click() for i in range(2)]
                        window.start.emit()
                        return True
                    else:
                        driver.refresh()
                        window.start.emit()
                        return True
            except Exception as e:
                if type(e) == TimeoutException:
                    console.print("超时，网络错误", style="magenta")
                    sys.exit(0)
    # @staticmethod
    # def login_operator(username, password):
    #     global session, info_return
    #     client = login.Login()
    #     session, info_return = client.weibo(username, password, 'mobile')
    #     return session, info_return


class Picture(QWidget):
    change = pyqtSignal(str)
    start = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.change.connect(self.changePic)
        self.start.connect(self.show)
        self.stop.connect(self.hide)

    def changePic(self, file_path):
        label = QLabel(self)
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        label.move(0, 0)
        self.setFixedSize(180, 180)
        self.move(300, 200)
        self.setWindowTitle('')

    start_pos = QtCore.QPoint(0, 0)
    end_pos = QtCore.QPoint(0, 0)
    is_tracking = False

    def mouseMoveEvent(self, e: QMouseEvent):
        self.end_pos = e.pos() - self.start_pos
        self.move(self.pos() + self.end_pos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.is_tracking = True
            self.start_pos = QtCore.QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.is_tracking = False
            self.start_pos = 0
            self.end_pos = 0


class Interface(QWidget):
    signal = pyqtSignal(str)
    start = pyqtSignal()

    def __init__(self):
        super(QWidget, self).__init__()
        self.r = float(conf.get("RESCALE", "factor"))
        self.setFixedSize(int(713 * self.r), int(439 * self.r))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        ids = QFontDatabase.addApplicationFont('UI/Pixes.ttf')
        fonts = QFont(QFontDatabase.applicationFontFamilies(ids)[0])
        fonts.setPointSize(int(12 * self.r))

        self.back_frame = QLabel(self)
        self.back_frame.move(0, 0)
        self.back_frame.setFixedSize(int(713 * self.r), int(439 * self.r))
        back_frame_pic = QPixmap('UI/background_A.png')
        self.back_frame.setScaledContents(True)
        self.back_frame.setPixmap(back_frame_pic)

        self.do_button = QPushButton(self.back_frame)
        self.do_button.setFixedSize(int(76 * self.r), int(76 * self.r))
        self.do_button.move(int(517 * self.r), int(17 * self.r))
        self.do_button.setStyleSheet("QPushButton{border-image: url(UI/do_idle.png)}"
                                     "QPushButton:hover{border-image: url(UI/do_hover.png)}"
                                     "QPushButton:pressed{border-image: url(UI/do_press.png)}")
        self.do_button.clicked.connect(self.execute)

        self.stop_button = QPushButton(self.back_frame)
        self.stop_button.setFixedSize(int(82 * self.r), int(82 * self.r))
        self.stop_button.move(int(514 * self.r), int(98 * self.r))
        self.stop_button.setStyleSheet("QPushButton{border-image: url(UI/stop_idle.png)}"
                                       "QPushButton:hover{border-image: url(UI/stop_hover.png)}"
                                       "QPushButton:pressed{border-image: url(UI/stop_press.png)}")
        self.stop_button.clicked.connect(stop)

        self.music_button = QPushButton(self.back_frame)
        self.music_button.setFixedSize(int(75 * self.r), int(163 * self.r))
        self.music_button.move(int(592 * self.r), int(17 * self.r))
        self.music_button.setStyleSheet("QPushButton{border-image: url(UI/music_idle.png)}"
                                        "QPushButton:hover{border-image: url(UI/music_hover.png)}"
                                        "QPushButton:pressed{border-image: url(UI/music_press.png)}")
        self.music_button.clicked.connect(self.music)

        self.exit_button = QPushButton(self.back_frame)
        self.exit_button.setFixedSize(int(54 * self.r), int(163 * self.r))
        self.exit_button.move(int(660 * self.r), int(17 * self.r))
        self.exit_button.setStyleSheet("QPushButton{border-image: url(UI/exit_idle.png)}"
                                       "QPushButton:hover{border-image: url(UI/exit_hover.png)}"
                                       "QPushButton:pressed{border-image: url(UI/exit_press.png)}")
        self.exit_button.clicked.connect(sys.exit)

        self.id_base = QCheckBox('手动挡', self)
        self.id_base.move(int(41 * self.r), int(106 * self.r))
        self.id_base.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                   "QCheckBox::indicator{width: 20px;height: 21px;}"
                                   "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                   "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.id_base.toggled.connect(self.change_id)

        self.auto_base = QCheckBox('自动挡', self)
        self.auto_base.move(int(41 * self.r), int(147 * self.r))
        self.auto_base.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.auto_base.setChecked(True)
        self.auto_base.toggled.connect(self.change_auto)

        self.bomb_mode = QCheckBox('爆破模式', self)
        self.bomb_mode.move(int(41 * self.r), int(208 * self.r))
        self.bomb_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.bomb_mode.toggled.connect(self.change_bomb)

        self.fast_tran = QCheckBox('是否快转', self)
        self.fast_tran.move(int(81 * self.r), int(249 * self.r))
        self.fast_tran.setStyleSheet("QCheckBox{color: rgb(211, 106, 126);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.fast_tran.toggled.connect(self.change_tran)

        self.fast_comm = QCheckBox('是否冲评', self)
        self.fast_comm.move(int(81 * self.r), int(290 * self.r))
        self.fast_comm.setStyleSheet("QCheckBox{color: rgb(211, 106, 126);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.fast_tran.toggled.connect(self.change_comm)

        self.cure_mode = QCheckBox('医疗模式', self)
        self.cure_mode.move(int(41 * self.r), int(331 * self.r))
        self.cure_mode.setStyleSheet("color: rgb(184, 96, 104)")
        self.cure_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.cure_mode.toggled.connect(self.change_cure)

        self.renew_mode = QCheckBox('刷新模式', self)
        self.renew_mode.move(int(41 * self.r), int(372 * self.r))
        self.renew_mode.setStyleSheet("color: rgb(184, 96, 104)")
        self.renew_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                      "QCheckBox::indicator{width: 20px;height: 21px;}"
                                      "QCheckBox::indicator:enabled:unchecked{image: url(UI/none.png)}"
                                      "QCheckBox::indicator:enabled:checked{image: url(UI/space.png)}")
        self.renew_mode.toggled.connect(self.change_renew)

        self.create_text = QLineEdit(self)
        self.create_text.setFont(fonts)
        self.create_text.setStyleSheet('color: rgb(137, 123, 123);border-width: 1px;border-style: '
                                       'solid;border-color: rgb(255, 255, 255);background-color: rgb(255, 255, '
                                       '255);')
        self.create_text.setPlaceholderText("是输入框捏")
        self.create_text.raise_()
        self.create_text.setGeometry(int(31 * self.r), int(28 * self.r), int(208 * self.r), int(21 * self.r))

        self.animate = QLabel(self)
        self.animate.setFixedSize(int(119 * self.r), int(153 * self.r))
        self.animate.move(int(267 * self.r), int(270 * self.r))
        self.gif = QMovie('JR.gif')
        self.gif.setScaledSize(QSize(int(119 * self.r), int(153 * self.r)))
        self.animate.setMovie(self.gif)
        self.gif.start()

        self.texts = QTextEdit(self)
        self.scr()
        # self.texts.setEnabled(False)
        self.texts.setFocusPolicy(Qt.NoFocus)
        self.texts.setFontPointSize(13)
        self.texts.setStyleSheet('border-width: 1px;border-style: solid;border-color: rgb(255,224,'
                                 '230);background-color: rgb(255,224,230)')
        self.texts.setFont(fonts)
        self.texts.setFixedSize(207, 118)
        self.texts.move(281, 31)
        self.texts.raise_()
        self.texts.ensureCursorVisible()
        cursor = self.texts.textCursor()
        pos = len(self.texts.toPlainText())
        cursor.setPosition(pos)
        self.texts.setTextCursor(cursor)
        self.start.connect(self.show)
        self.playing = False
        self.first_play = True

    def change_auto(self, cb):
        if self.id_base.isChecked() and self.auto_base.isChecked():
            self.id_base.setChecked(False)

    def change_id(self, cb):
        if self.id_base.isChecked() and self.auto_base.isChecked():
            self.auto_base.setChecked(False)
        self.create_text.setPlaceholderText("手动挡下需输入ID")

    def change_tran(self, cb):
        if self.bomb_mode.checkState() == Qt.Unchecked and self.fast_tran.isChecked():
            self.fast_tran.setChecked(False)

    def change_comm(self, cb):
        if self.bomb_mode.checkState() == Qt.Unchecked and self.fast_comm.isChecked():
            self.fast_comm.setChecked(False)

    def change_bomb(self, cb):
        if self.bomb_mode.checkState() == Qt.Checked:
            self.fast_tran.setChecked(True)
            self.fast_comm.setChecked(True)
        elif self.bomb_mode.checkState() == Qt.Unchecked:
            self.fast_tran.setChecked(False)
            self.fast_comm.setChecked(False)
        if (self.cure_mode.isChecked() or self.renew_mode.isChecked()) and self.bomb_mode.isChecked():
            self.cure_mode.setChecked(False)
            self.renew_mode.setChecked(False)

    def change_cure(self, cb):
        if (self.renew_mode.isChecked() or self.bomb_mode.isChecked()) and self.cure_mode.isChecked():
            self.bomb_mode.setChecked(False)
            self.renew_mode.setChecked(False)
        self.create_text.setPlaceholderText("无需输入")

    def change_renew(self, cb):
        if (self.cure_mode.isChecked() or self.bomb_mode.isChecked()) and self.renew_mode.isChecked():
            self.bomb_mode.setChecked(False)
            self.cure_mode.setChecked(False)
        self.create_text.setPlaceholderText("需输入待刷新网址")

    def music(self):
        if self.first_play:
            self.first_play = False
            self.playing = True
            pygame.mixer.init()
            pygame.mixer.music.load("audio.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1, start=0.0, fade_ms=40)
        else:
            if self.playing:
                pygame.mixer.music.pause()
                self.playing = False
            else:
                pygame.mixer.music.unpause()
                self.playing = True

    def execute(self):
        commander = Commander()
        status = {
            "ID": self.id_base.isChecked(),
            "AUTO": self.auto_base.isChecked(),
            "BOMB": self.bomb_mode.isChecked(),
            "TRAN": self.fast_tran.isChecked(),
            "COMM": self.fast_comm.isChecked(),
            "CURE": self.cure_mode.isChecked(),
            "RENEW": self.renew_mode.isChecked()
        }
        if status["AUTO"]:
            if status["CURE"]:
                commander.auto_heal()
        if status["RENEW"]:
            commander.do_renew()
        if status["BOMB"]:
            if status["TRAN"]:
                commander.renew.comment_flag = True
            if status["COMM"]:
                commander.renew.tran_flag = True
            commander.auto_kill()
            if not status["TRAN"] and status["COMM"]:
                commander.bomb_auto()

    def scr(self):
        self.texts.setVerticalScrollBarPolicy(1)

    start_pos = QtCore.QPoint(0, 0)
    end_pos = QtCore.QPoint(0, 0)
    is_tracking = False

    def mouseMoveEvent(self, e: QMouseEvent):
        self.end_pos = e.pos() - self.start_pos
        self.move(self.pos() + self.end_pos)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.is_tracking = True
            self.start_pos = QtCore.QPoint(e.x(), e.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.is_tracking = False
            self.start_pos = 0
            self.end_pos = 0


class Commander:
    def __init__(self):
        self.kill = Kill(window=window, driver=driver, conf=conf)
        self.cure = Cure(window=window, driver=driver, conf=conf)
        self.renew = Renew(driver, conf)
        self.black = Black(window, driver, conf, session)

    def auto_heal(self):
        global window, driver, conf

        def heal():
            times = 0
            while True:
                self.cure.work()
                times += 1
                window.signal.emit("第{:d}次工作结束，开始睡眠".format(times))
                time.sleep(int(conf.get("CURE", "sleep_seconds")))
                if stopped():
                    return True

        thread = threading.Thread(target=heal)
        thread.start()

    def auto_kill(self):
        global window, driver, conf

        def heal():
            times = 0
            while True:
                self.kill.work()
                times += 1
                window.signal.emit("第{:d}次工作结束，开始睡眠".format(times))
                time.sleep(50)
                if stopped():
                    return True

        thread = threading.Thread(target=heal)
        thread.start()

    def do_renew(self):
        global window, driver, conf

        def detector():
            global _stop_event
            while True:
                window.signal.emit("页面正在刷新")
                time.sleep(3)
                if stopped():
                    window.signal.emit("页面停止刷新")
                    do.join()
                    return True

        url = window.create_text.text()
        if url == "":
            window.signal.emit("贝极星未输入网址")
            return False
        do = threading.Thread(target=self.renew.create_tag, args=(url,))
        do.start()

        thread = threading.Thread(target=detector)
        thread.start()

    def bomb_auto(self):
        global window, driver, conf, session
        bomb = self.black.run()


class Poster:
    def __init__(self, uid):
        Blogger.open_browser("https://weibo.com/u/" + uid)

    @staticmethod
    def tran():
        global wait
        tran_button = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/main/div/div/div[2]/article/footer/div/div[1]/div')))
        [tran_button.click() for i in range(2)]
        tran_do = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="composerEle"]/div/div/div[3]/div/button')))
        [tran_do.click() for i in range(2)]

    @staticmethod
    def comm(comment):
        global wait
        comm_button = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/main/div/div/div[2]/article/footer/div/div[2]/div')))
        [comm_button.click() for i in range(2)]
        comm_text = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="composerEle"]/div/div/div[1]/div/textarea')))
        comm_text.send_keys(comment)
        send_button = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="composerEle"]/div/div/div[3]/div/button')))
        [send_button.click() for i in range(2)]

    @staticmethod
    def like():
        global wait
        like_button = wait.until(condition.element_to_be_clickable(
            (By.XPATH, '//*[@id="app"]/div[1]/div[2]/div[2]/main/div/div/div[2]/article/footer/div/div[3]/div')))
        [like_button.click() for i in range(2)]


def login():
    def do():
        global pic, session, info_return
        #console.print("[blink]请选择登录方式，输入数字后回车（推荐方式2）：[/blink]")
        #way = console.input("[dim]手动输入账号密码登录[/dim](1)  [dim]微博app扫码一键登录[/dim](2): ")
        way = 2
        console.print("\n")
        blogger.open_browser("https://passport.weibo.cn/signin/login")
        try:
            if "home" not in driver.current_url:
                if int(way) == 1:
                    name = console.input("[blink]请输入账号: ")
                    password = console.input("[blink]请输入密码: ")
                    console.print("可能要求输入验证码，注意检查", style="italic magenta")
                    blogger.login_operator(name, password)
                elif int(way) == 2:
                    blogger.bar(25)
                    blogger.localize_scanner()
                    path = (r'Img\{}.jpg'.format("Login"))
                    pic.change.emit(path)
                    pic.start.emit()
                    console.print("请使用微博app扫描弹出的二维码", style="italic magenta")
                    cont = console.input("[blink]允许登录后请返回此界面，并按下回车[/blink] [[green]Enter[/green]]")
                    driver.refresh()
                    pic.stop.emit()
                # saveSessionCookies(session=session, cookiespath='cookie.pkl')
                # driver.get('https://weibo.com/')
                # driver.delete_all_cookies()
                # with open('cookies.pkl', 'r') as f:
                #     cookies_list = json.load(f)
                #     for cookie in cookies_list:
                #         driver.add_cookie(cookie)
                # driver.refresh()
                window.start.emit()
                time.sleep(20)
                with open('cookies.pkl', 'w') as f:
                    # 将cookies保存为json格式
                    f.write(json.dumps(driver.get_cookies()))

        except Exception as e:
            if type(e) == TimeoutException:
                console.print("超时，网络错误", style="magenta")
                sys.exit(0)
            else:
                print("侦测到未知错误，请尝试关闭再打开本程序")
                #print(e)
                sys.exit(0)

    thread = threading.Thread(target=do)
    thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Interface()
    pic = Picture()


    def append(content):
        content = "<font color=\"#E77E89\">" + content + "</font>"
        window.texts.append(content)


    window.signal.connect(append)

    ids = QFontDatabase.addApplicationFont('UI/Pixes.ttf')
    font = QFont(QFontDatabase.applicationFontFamilies(ids)[0])
    font.setPointSize(int(13 * window.r * float(conf.get("RESCALE", "font_size"))))
    app.setFont(font)

    console = Console(color_system="256", style=None)
    console.rule("[magenta]程序启动")

    console.print("[blink]启动中... 若出现错误请尝试关闭再开启本程序...\n[/blink]")

    service = Service('Chrome/App/chromedriver.exe')
    driver = webdriver.Chrome(service=Service(EdgeChromiumDriverManager().install()), options=Blogger.hide())
    # driver = webdriver.Chrome(service=service, options=Blogger.hide())
    # driver = webdriver.Chrome(service=service)
    blogger = Blogger()
    driver.implicitly_wait(5)
    # driver.set_window_size(400, 600)
    wait = WebDriverWait(driver, 20)
    login()
    # 输入账号密码
    #     console.print("[blink]您的操作内容[/blink]")
    #     way = console.input("[dim]爆破[/dim](1)[dim]奶人[/dim](2)[dim]快转[/dim](3)[dim]点赞[/dim](4)[dim]刷新[/dim](5): ")
    #     console.print("[blink]您的操作对象[/blink]")
    #     target = console.input("[dim]一个账户[/dim](1)[dim]一张帖子[/dim](2): ")
    #     if target == 1:
    #         uid = console.input("[dim]输入ID[/dim]: ")
    #         basic_url = "https://weibo.com/u/" + uid
    #         detail_page = "https://m.weibo.cn/detail/" + uid
    #     elif target == 2:
    #         url = console.input("[dim]输入网址[/dim]: ")
    sys.exit(app.exec_())
