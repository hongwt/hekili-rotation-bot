import os
import time
import random
import multiprocessing
import numpy as np
import pyautogui

from PIL import ImageGrab

from PySide6.QtCore import Qt, QTimer, QPoint, QObject
from PySide6.QtWidgets import (QWidget, QApplication, QLabel, 
                              QVBoxLayout, QMenu, QDialog, QMessageBox)
from PySide6.QtGui import QPainter, QColor

import win32gui

import config
from vision import Vision
from screenshot_settings import ScreenshotSettingsDialog

class WowBot(QObject):
    # 使用 QObject 作为基类以支持信号和槽
    
    def __init__(self):
        super().__init__()
        self.stopped = True
        self.vision = Vision()
        
        # 创建定时器替代线程
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        
        # 设置pyautogui暂停时间
        pyautogui.PAUSE = 0.0

    def convert_to_key(self, key_text):
        if not key_text:
            return ''
        # drop all keys that are not in the valid keys list
        key_text = [key for key in key_text if (key >= '0' and key <= 'z')]
        key_text = ''.join(key_text)
        # add some special cases
        if ("11" == key_text):
            return '1'
        if len(key_text) == 1:
            return key_text[0]
        else:
            return ''
        
    def press_ability_key(self, key, cooldown):
        key = key.lower()  # Convert key to lowercase
        print(f'Casting ability {key}.')
        pyautogui.keyUp(key)
        delay = random.uniform(0.01, 0.5)
        time.sleep(delay)
        pyautogui.keyDown(key)

    # 创建一个函数，将所有非黑色像素转换为白色
    def to_white_or_black(self, value):
        threshold = 1
        if value < threshold:
            return 0  # 返回黑色
        else:
            return 255  # 返回白色
    
    def process_frame(self):
        """单次处理一帧图像，作为 QTimer 的槽函数"""
        loop_time = time.time()
        print('begin loop: ', loop_time)
        
        screenshot = ImageGrab.grab(bbox=(config.HEKILI_X, 
                                        config.HEKILI_Y, 
                                        config.HEKILI_X + config.HEKILI_W, 
                                        config.HEKILI_Y + config.HEKILI_H))
        if screenshot is None:
            return
            
        screenshot_np = np.array(screenshot)
        print('grab image: ', time.time())

        key_text = self.vision.get_ability_key(screenshot_np)
        key = self.convert_to_key(key_text)
        print('get key: ', time.time())
        
        if (key and key != ''):
            if key in config.VALID_KEYS:
                self.press_ability_key(key, 0)
                print('press key: ', time.time())
            else:
                screenshot.save(f'images/invalid_{key}_{time.time()}.png')
                
        print(f'vision FPS {1 / (time.time() - loop_time)}')

    def start(self):
        """启动机器人"""
        if self.stopped:
            self.stopped = False
            # 启动定时器，设置适当的间隔（毫秒）
            self.timer.start(50)  # 每50毫秒执行一次，约等于20FPS

    def stop(self):
        """停止机器人"""
        if not self.stopped:
            self.stopped = True
            self.timer.stop()

class WinGUI(QWidget):
    # properties
    hwnd = None
    bot = None
    offset = None  # 用于窗口拖动

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle("Hekili Bot")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 40)  # 减小高度，不再显示截图预览

        # 获取WoW窗口句柄
        self.hwnd = win32gui.FindWindow(None, config.WOW_WINDOW_NAME)
        
        # 创建Bot实例
        self.bot = WowBot()

        # 创建状态标签
        self.status_label = QLabel("就绪", self)
        self.status_label.setStyleSheet("color: #000000; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.setLayout(layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.position().toPoint()
        elif event.button() == Qt.RightButton:
            self.showContextMenu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    def showContextMenu(self, pos):
        menu = QMenu(self)
        
        settings_action = menu.addAction("设置截图区域")
        
        if self.bot.stopped:
            start_action = menu.addAction("开始")
        else:
            start_action = menu.addAction("结束")
        
        about_action = menu.addAction("关于")
        exit_action = menu.addAction("退出")
        
        action = menu.exec(pos)
        
        if action == settings_action:
            self.openScreenshotSettings()
        elif action == start_action:
            self.startRotation()
        elif action == about_action:
            self.showAbout()
        elif action == exit_action:
            self.close()

    def openScreenshotSettings(self):
        # 创建并显示设置对话框
        settings_dialog = ScreenshotSettingsDialog(self, self.hwnd)
        settings_dialog.exec()

    def startRotation(self):
        if self.bot.stopped:
            self.status_label.setText("正在运行...")
            # 将窗口设置为前置
            if self.hwnd:
                win32gui.SetForegroundWindow(self.hwnd)
            self.bot.start()
        else:
            self.status_label.setText("已停止")
            self.bot.stop()

    def showAbout(self):
        QMessageBox.about(self, "关于", "Hekili Rotation Bot\n作者: Hongwt\n\n辅助魔兽世界Hekili插件使用")

    def paintEvent(self, event):
        # 绘制半透明背景
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置半透明白色背景
        painter.setBrush(QColor(255, 255, 255, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    app = QApplication([])
    win = WinGUI()
    win.show()
    app.exec()