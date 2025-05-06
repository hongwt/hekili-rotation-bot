import os
import time
import random
import multiprocessing
import numpy as np
import pyautogui

from PIL import ImageGrab

from PySide6.QtCore import Qt, QTimer, QPoint, QObject, Signal
from PySide6.QtWidgets import (QWidget, QApplication, QLabel, 
                              QVBoxLayout, QHBoxLayout, QMenu, QDialog, QMessageBox)
from PySide6.QtGui import QPainter, QColor

from pynput import keyboard  # 添加pynput库以监听全局按键

import config
from vision import Vision
from screenshot_settings import ScreenshotSettingsDialog

class WowBot(QObject):
    # 使用 QObject 作为基类以支持信号和槽
    # 添加按键检测信号
    key_detected = Signal(str)

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
        if key_text == 'NA':
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

        key_text = self.vision.get_ability_key(screenshot_np)
        # 发送信号通知GUI更新按键显示
        self.key_detected.emit(key_text)

        key = self.convert_to_key(key_text)
        
        if (key and key != ''):
            # Replace S with 5
            if key.upper() == 'S':
                key = '5'
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
    # 添加信号用于在非GUI线程中触发GUI操作
    toggle_signal = Signal()
    
    # properties
    bot = None
    offset = None  # 用于窗口拖动
    keyboard_listener = None  # 键盘监听器
    alt_pressed = False  # 记录Alt键状态

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupKeyboardListener()
        
        # 连接信号到槽
        self.toggle_signal.connect(self.startRotation)

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle("Hekili Bot")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 40)  # 减小高度，不再显示截图预览
        
        # 创建Bot实例
        self.bot = WowBot()
        # 连接bot的信号到更新按键显示的槽
        self.bot.key_detected.connect(self.update_key_display)

        # 创建状态标签
        self.status_label = QLabel("就绪 (Alt+X切换)", self)  # 更新标签文本提示快捷键
        self.status_label.setStyleSheet("color: #000000; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 创建按键显示标签
        self.key_label = QLabel("", self)
        self.key_label.setStyleSheet("color: #FF0000; font-size: 16px; font-weight: bold;")
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setMinimumWidth(40)
        
        # 布局
        main_layout = QVBoxLayout()
        
        # 创建水平布局放置状态标签和按键标签
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.status_label)
        h_layout.addWidget(self.key_label)
        
        main_layout.addLayout(h_layout)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.setLayout(main_layout)

    def setupKeyboardListener(self):
        """设置键盘监听器"""
        def on_press(key):
            try:
                if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                    self.alt_pressed = True
                # 使用多种方式检测'x'键，包括直接字符串比较
                elif ((hasattr(key, 'char') and key.char and key.char.lower() == 'x') or 
                      str(key).strip("'") == "x"):
                    if self.alt_pressed:
                        # 使用信号在主线程中执行操作
                        self.toggle_signal.emit()
            except Exception as e:
                # 捕获并记录所有异常以便于调试
                print(f"按键监听器错误: {e}")
        
        def on_release(key):
            try:
                if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
                    self.alt_pressed = False
            except Exception as e:
                print(f"按键释放错误: {e}")
                
            # 不需要返回False，让监听器继续运行
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        self.keyboard_listener.start()

    def closeEvent(self, event):
        """关闭窗口时停止键盘监听"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        event.accept()

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
        settings_dialog = ScreenshotSettingsDialog(self)
        settings_dialog.exec()

    def startRotation(self):
        if self.bot.stopped:
            self.status_label.setText("正在运行... (Alt+X切换)")
            self.bot.start()
        else:
            self.status_label.setText("已停止 (Alt+X切换)")
            self.bot.stop()

    def showAbout(self):
        QMessageBox.about(self, "关于", "Hekili Rotation Bot\n作者: Hongwt\n\n辅助魔兽世界Hekili插件使用")

    def paintEvent(self, event):
        painter = QPainter(self)
        # 开启反锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置半透明白色背景
        painter.setBrush(QColor(255, 255, 255, 100))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def update_key_display(self, key):
        """更新按键显示标签"""
        if key and key != '':
            self.key_label.setText(key.upper())
        else:
            self.key_label.setText("")
            
if __name__ == "__main__":
    multiprocessing.freeze_support()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    app = QApplication([])
    win = WinGUI()
    win.show()
    app.exec()