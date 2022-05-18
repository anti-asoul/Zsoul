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
import signal
from psutil import process_iter

_stop_event = threading.Event()
pid_list = []


def terminate():
    global driver
    driver.close()
    driver.quit()
    window.hide()
    log.hide()

    record_pid("msedge")
    kill_pid()
    os.kill(os.getpid(), signal.SIGINT)
    # sys.exit(0)


def record_pid(program_name):
    global pid_list
    # "msedge"
    for process in process_iter():
        if program_name in process.name():
            pid_list.append(process.pid)


def kill_pid():
    global pid_list
    for j in pid_list:
        os.kill(int(j), signal.SIGINT)


def stop():
    global _stop_event
    _stop_event.set()


def stopped():
    return _stop_event.is_set()


class Blogger:

    @staticmethod
    def hide():
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument('--disable-gpu')
        options.add_argument('--hide-scrollbars')
        options.add_argument('blink-settings=imagesEnabled=false')
        # options.add_argument("--headless")
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

    def localize_scanner(self):
        try:
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
                file_name = r'src/Verify\{}.jpg'.format("Login")
                with open(file_name, 'wb') as f:
                    f.write(pics.content)
                return True
        except Exception as e:
            e = e
            return False

    # def login_operator(self, names, passwords):
    #     self.open_browser("https://passport.weibo.cn/signin/login")
    #     name_tag = wait.until(condition.presence_of_element_located((By.CSS_SELECTOR, "input[id='loginName']")))
    #     name_tag.clear()
    #     name_tag.send_keys(names)
    #     password_tag = wait.until(condition.presence_of_element_located((By.CSS_SELECTOR,
    #                                                                      "input[id='loginPassword']")))
    #     password_tag.clear()
    #     password_tag.send_keys(passwords)
    #     login_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR, "a[id='loginAction']")))
    #     [login_button.click() for i in range(2)]
    #     # print(driver.current_url)
    #     while "signin" in driver.current_url:
    #         try:
    #             time.sleep(6)
    #             if len(driver.find_elements(By.XPATH, '//*[@id="errorMsg"]')) != 0:
    #                 print("用户名或密码错误")
    #                 login()
    #                 break
    #             else:
    #                 if "first_enter" in driver.current_url or "secondverify" in driver.current_url:
    #                     # print(driver.current_url)
    #                     verify_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR,
    #                                                                                   "div.my-btn-box a")))
    #                     [verify_button.click() for i in range(2)]
    #                     verify_tag = wait.until(
    #                         condition.presence_of_element_located((By.CSS_SELECTOR, '//*[@id="verifyCode"]'
    #                                                                                 '/div[1]/div/div/div[2]'
    #                                                                                 '/div/div/div/span[1]/input'))
    #                     )
    #                     # change to UI interaction
    #                     codes = console.input("请输入验证码: ")
    #                     verify_tag.send_keys(codes)
    #                     done_button = wait.until(condition.element_to_be_clickable((By.CSS_SELECTOR,
    #                                                                                 "div.my-btn-box a")))
    #                     [done_button.click() for i in range(2)]
    #                     window.start.emit()
    #                     return True
    #                 else:
    #                     driver.refresh()
    #                     window.start.emit()
    #                     return True
    #         except Exception as e:
    #             if type(e) == TimeoutException:
    #                 print("超时，网络错误")
    #                 sys.exit(0)
    # @staticmethod
    # def login_operator(username, password):
    #     global session, info_return
    #     client = login.Login()
    #     session, info_return = client.weibo(username, password, 'mobile')
    #     return session, info_return


class Login(QWidget):
    change = pyqtSignal(str)
    start = pyqtSignal()
    stop = pyqtSignal()
    text = pyqtSignal(str)
    next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.r = float(conf.get("RESCALE", "factor"))
        self.change.connect(self.setQR)
        self.start.connect(self.show)
        self.stop.connect(self.hide)
        self.resize(int(272 * self.r), int(439 * self.r))

        self.base_frame = QLabel(self)
        self.base_frame.resize(int(272 * self.r), int(439 * self.r))
        pixmap = QPixmap("src/UI/login_frame.png")
        self.base_frame.setPixmap(pixmap)

        self.QR_frame = QLabel(self)
        self.QR_frame.resize(int(188 * self.r), int(188 * self.r))
        self.QR_frame.move(int(42 * self.r), int(96 * self.r))
        self.QR_label = QLabel(self)
        pixmap = QPixmap("src/UI/QR_frame.png")
        self.QR_frame.setPixmap(pixmap)

        self.login_button = QPushButton(self)
        self.login_button.setToolTip("是登录按钮捏")
        self.quit_button = QPushButton(self)
        self.quit_button.setToolTip("是退出按钮捏")
        self.login_button.resize(int(251 * self.r), int(51 * self.r))
        self.login_button.move(int(15 * self.r), int(330 * self.r))
        self.login_button.setStyleSheet("QPushButton{border-image: url(src/UI/enter_idle.png)}"
                                        "QPushButton:hover{border-image: url(src/UI/enter_hover.png)}"
                                        "QPushButton:pressed{border-image: url(src/UI/enter_press.png)}")
        self.login_button.clicked.connect(self.login_check)

        self.quit_button.resize(int(251 * self.r), int(51 * self.r))
        self.quit_button.move(int(15 * self.r), int(377 * self.r))
        self.quit_button.setStyleSheet("QPushButton{border-image: url(src/UI/quit_idle.png)}"
                                       "QPushButton:hover{border-image: url(src/UI/quit_hover.png)}"
                                       "QPushButton:pressed{border-image: url(src/UI/quit_press.png)}")
        self.quit_button.clicked.connect(terminate)

        self.create_text = QLineEdit(self)
        self.create_text.setStyleSheet('color: rgb(137, 123, 123);border-width: 1px;border-style: '
                                       'solid;border-color: rgb(255, 255, 255);background-color: rgb(255, 255, '
                                       '255);')
        self.create_text.setPlaceholderText("扫码后，按绿钮验证")
        self.create_text.raise_()
        self.create_text.setGeometry(int(31 * self.r), int(28 * self.r), int(208 * self.r), int(21 * self.r))
        self.create_text.setEnabled(False)

    def setQR(self, file_path):
        pixmap = QPixmap(file_path)
        self.QR_label.setPixmap(pixmap)
        self.QR_label.move(int(46 * self.r), int(100 * self.r))

    def login_check(self):
        global driver, window
        driver.refresh()
        driver.implicitly_wait(2)
        if "home" in driver.current_url:
            self.next.emit()
        else:
            log.text.emit("您尚未扫码")
            self.setQR(r'src\Verify\{}.jpg'.format("Denied"))
            blogger.localize_scanner()
            path = (r'src\Verify\{}.jpg'.format("Login"))
            log.change.emit(path)

    def auto_login_check(self):
        def do():
            while "home" not in driver.current_url:
                time.sleep(1.5)
            else:
                self.next.emit()
                return True

        thread = threading.Thread(target=do)
        thread.start()

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

        self.back_frame = QLabel(self)
        self.back_frame.move(0, 0)
        self.back_frame.setFixedSize(int(713 * self.r), int(439 * self.r))
        back_frame_pic = QPixmap('src/UI/background_A.png')
        self.back_frame.setScaledContents(True)
        self.back_frame.setPixmap(back_frame_pic)

        self.do_button = QPushButton(self.back_frame)
        self.do_button.setFixedSize(int(76 * self.r), int(76 * self.r))
        self.do_button.move(int(517 * self.r), int(17 * self.r))
        self.do_button.setStyleSheet("QPushButton{border-image: url(src/UI/do_idle.png)}"
                                     "QPushButton:hover{border-image: url(src/UI/do_hover.png)}"
                                     "QPushButton:pressed{border-image: url(src/UI/do_press.png)}")
        self.do_button.clicked.connect(self.execute)
        self.do_button.setToolTip("是开始按钮捏")

        self.stop_button = QPushButton(self.back_frame)
        self.stop_button.setFixedSize(int(82 * self.r), int(82 * self.r))
        self.stop_button.move(int(514 * self.r), int(98 * self.r))
        self.stop_button.setStyleSheet("QPushButton{border-image: url(src/UI/stop_idle.png)}"
                                       "QPushButton:hover{border-image: url(src/UI/stop_hover.png)}"
                                       "QPushButton:pressed{border-image: url(src/UI/stop_press.png)}")
        self.stop_button.clicked.connect(stop)
        self.stop_button.setToolTip("是终止按钮捏")

        self.music_button = QPushButton(self.back_frame)
        self.music_button.setFixedSize(int(75 * self.r), int(163 * self.r))
        self.music_button.move(int(592 * self.r), int(17 * self.r))
        self.music_button.setStyleSheet("QPushButton{border-image: url(src/UI/music_idle.png)}"
                                        "QPushButton:hover{border-image: url(src/UI/music_hover.png)}"
                                        "QPushButton:pressed{border-image: url(src/UI/music_press.png)}")
        self.music_button.clicked.connect(self.music)
        self.music_button.setToolTip("是发病按钮捏")

        self.exit_button = QPushButton(self.back_frame)
        self.exit_button.setFixedSize(int(54 * self.r), int(163 * self.r))
        self.exit_button.move(int(660 * self.r), int(17 * self.r))
        self.exit_button.setStyleSheet("QPushButton{border-image: url(src/UI/exit_idle.png)}"
                                       "QPushButton:hover{border-image: url(src/UI/exit_hover.png)}"
                                       "QPushButton:pressed{border-image: url(src/UI/exit_press.png)}")
        self.exit_button.clicked.connect(terminate)
        self.exit_button.setToolTip("是退出按钮捏")

        self.manu_base = QCheckBox('手动挡', self)
        self.manu_base.move(int(41 * self.r), int(106 * self.r))
        self.manu_base.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.manu_base.toggled.connect(self.change_manu)

        self.auto_base = QCheckBox('自动挡', self)
        self.auto_base.move(int(41 * self.r), int(147 * self.r))
        self.auto_base.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.auto_base.setChecked(True)
        self.auto_base.toggled.connect(self.change_auto)

        self.bomb_mode = QCheckBox('爆破模式', self)
        self.bomb_mode.move(int(41 * self.r), int(208 * self.r))
        self.bomb_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.bomb_mode.toggled.connect(self.change_bomb)

        self.fast_tran = QCheckBox('是否快转', self)
        self.fast_tran.move(int(81 * self.r), int(249 * self.r))
        self.fast_tran.setStyleSheet("QCheckBox{color: rgb(211, 106, 126);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.fast_tran.toggled.connect(self.change_tran)

        self.fast_comm = QCheckBox('是否冲评', self)
        self.fast_comm.move(int(81 * self.r), int(290 * self.r))
        self.fast_comm.setStyleSheet("QCheckBox{color: rgb(211, 106, 126);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.fast_tran.toggled.connect(self.change_comm)

        self.cure_mode = QCheckBox('医疗模式', self)
        self.cure_mode.move(int(41 * self.r), int(331 * self.r))
        self.cure_mode.setStyleSheet("color: rgb(184, 96, 104)")
        self.cure_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                     "QCheckBox::indicator{width: 20px;height: 21px;}"
                                     "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                     "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.cure_mode.toggled.connect(self.change_cure)

        self.renew_mode = QCheckBox('刷新模式', self)
        self.renew_mode.move(int(41 * self.r), int(372 * self.r))
        self.renew_mode.setStyleSheet("color: rgb(184, 96, 104)")
        self.renew_mode.setStyleSheet("QCheckBox{color: rgb(184, 96, 104);}"
                                      "QCheckBox::indicator{width: 20px;height: 21px;}"
                                      "QCheckBox::indicator:enabled:unchecked{image: url(src/UI/none.png)}"
                                      "QCheckBox::indicator:enabled:checked{image: url(src/UI/space.png)}")
        self.renew_mode.toggled.connect(self.change_renew)

        self.create_text = QLineEdit(self)
        self.create_text.setStyleSheet('color: rgb(137, 123, 123);border-width: 1px;border-style: '
                                       'solid;border-color: rgb(255, 255, 255);background-color: rgb(255, 255, '
                                       '255);')
        self.create_text.setPlaceholderText("是输入框捏")
        self.create_text.raise_()
        self.create_text.setGeometry(int(31 * self.r), int(28 * self.r), int(208 * self.r), int(21 * self.r))

        self.animate = QLabel(self)
        self.animate.setFixedSize(int(119 * self.r), int(153 * self.r))
        self.animate.move(int(267 * self.r), int(270 * self.r))
        self.gif = QMovie('src/JR.gif')
        self.gif.setScaledSize(QSize(int(119 * self.r), int(153 * self.r)))
        self.animate.setMovie(self.gif)
        self.gif.start()

        self.texts = QTextEdit(self)
        self.scr()
        self.texts.setFocusPolicy(Qt.NoFocus)
        self.texts.setFontPointSize(13)
        self.texts.setStyleSheet('border-width: 1px;border-style: solid;border-color: rgb(255,224,'
                                 '230);background-color: rgb(255,224,230)')
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
        if self.manu_base.isChecked() and self.auto_base.isChecked():
            self.manu_base.setChecked(False)
        if self.bomb_mode.isChecked():
            self.create_text.setPlaceholderText("无需输入")
        if self.cure_mode.isChecked():
            self.create_text.setPlaceholderText("无需输入")
        if self.renew_mode.isChecked():
            self.create_text.setPlaceholderText("请输入待刷新网址")

    def change_manu(self, cb):
        if self.manu_base.isChecked() and self.auto_base.isChecked():
            self.auto_base.setChecked(False)
        if self.bomb_mode.isChecked():
            self.create_text.setPlaceholderText("请输入帖子网址")
        if self.cure_mode.isChecked():
            self.create_text.setPlaceholderText("请输入超话网址")
        if self.renew_mode.isChecked():
            self.create_text.setPlaceholderText("请输入待刷新网址")

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
        if self.manu_base.isChecked():
            self.create_text.setPlaceholderText("请输入帖子网址")
        elif self.auto_base.isChecked():
            self.create_text.setPlaceholderText("无需输入")

    def change_cure(self, cb):
        if (self.renew_mode.isChecked() or self.bomb_mode.isChecked()) and self.cure_mode.isChecked():
            self.bomb_mode.setChecked(False)
            self.renew_mode.setChecked(False)
        if self.manu_base.isChecked():
            self.create_text.setPlaceholderText("请输入超话网址")
        elif self.auto_base.isChecked():
            self.create_text.setPlaceholderText("无需输入")

    def change_renew(self, cb):
        if (self.cure_mode.isChecked() or self.bomb_mode.isChecked()) and self.renew_mode.isChecked():
            self.bomb_mode.setChecked(False)
            self.cure_mode.setChecked(False)
        self.create_text.setPlaceholderText("请输入待刷新网址")

    def music(self):
        if self.first_play:
            self.first_play = False
            self.playing = True
            pygame.mixer.init()
            pygame.mixer.music.load("src/audio.mp3")
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
            "ID": self.manu_base.isChecked(),
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
        self.kill = Kill(window=window, wait=wait, driver=driver, conf=conf)
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
        global log, session, info_return
        blogger.open_browser("https://passport.weibo.cn/signin/login")
        try:
            if "home" not in driver.current_url:
                blogger.localize_scanner()
                path = (r'src\Verify\{}.jpg'.format("Login"))
                log.change.emit(path)
                log.start.emit()
                log.auto_login_check()
                return True

        except Exception as e:
            if type(e) == TimeoutException:
                path = (r'src\Verify\{}.jpg'.format("Timeout"))
                log.change.emit(path)
                log.text.emit("加载超时，调试网络设备")
                return False
            else:
                path = (r'src\Verify\{}.jpg'.format("Denied"))
                log.change.emit(path)
                log.text.emit("侦测未知错误，尝试重启")
                return False

    thread = threading.Thread(target=do)
    thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Interface()
    log = Login()
    blogger = Blogger()
    service = Service('Chrome/App/chromedriver.exe')
    driver = webdriver.Chrome(service=Service(EdgeChromiumDriverManager().install()), options=Blogger.hide())
    # driver = webdriver.Chrome(service=Service(EdgeChromiumDriverManager().install()))
    wait = WebDriverWait(driver, 20)

    ids = QFontDatabase.addApplicationFont('src/UI/Pixes.ttf')
    font = QFont(QFontDatabase.applicationFontFamilies(ids)[0])
    font.setPointSize(int(13 * window.r * float(conf.get("RESCALE", "font_size"))))
    app.setFont(font)


    def next_page():
        global window, log
        log.login_button.hide()
        log.quit_button.hide()
        log.QR_frame.hide()
        log.QR_label.hide()
        pixmap = QPixmap("src/UI/tran_frame.png")
        log.base_frame.setPixmap(pixmap)
        window.move(log.pos())
        window.start.emit()
        log.hide()

    def append(content):
        content = "<font color=\"#E77E89\">" + content + "</font>"
        window.texts.append(content)


    def login_warning(content):
        log.create_text.setPlaceholderText(content)


    window.signal.connect(append)
    log.text.connect(login_warning)
    log.next.connect(next_page)

    login()

    sys.exit(app.exec_())
