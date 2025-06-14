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
from system_hotkey import SystemHotkey
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
        
        # 添加人工按键检测相关属性
        self.manual_key_pressed = False
        self.manual_key_time = 0
        self.manual_key_cooldown = 1.0  # 人工按键后停止自动按键的时间（秒）
        self.last_auto_key = ''
        self.last_auto_key_time = 0
        
        # 启动键盘监听器
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

    def on_key_press(self, key):
        """监听键盘按下事件"""
        try:
            # 获取按键字符
            if hasattr(key, 'char') and key.char:
                key_char = key.char.lower()
            elif hasattr(key, 'name'):
                # 处理特殊键
                if key.name.isdigit():
                    key_char = key.name
                else:
                    return
            else:
                return
            
            # 检查是否是有效的游戏按键
            if key_char in [k.lower() for k in config.MANUAL_KEYS]:
                current_time = time.time()
                
                # 判断是否为人工按键（非自动按键触发的）
                # 如果距离上次自动按键时间很短且按键相同，则认为是自动按键的回响
                if (self.last_auto_key.lower() == key_char and 
                    current_time - self.last_auto_key_time < 0.1):
                    return
                
                # 标记为人工按键
                self.manual_key_pressed = True
                self.manual_key_time = current_time
                print(f"检测到人工按键: {key_char}")
                
        except Exception as e:
            pass  # 忽略按键监听错误

    def on_key_release(self, key):
        """监听键盘释放事件"""
        pass

    def is_manual_key_active(self):
        """检查是否在人工按键冷却期内"""
        if not self.manual_key_pressed:
            return False
        
        current_time = time.time()
        if current_time - self.manual_key_time > self.manual_key_cooldown:
            self.manual_key_pressed = False
            return False
        
        return True

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
        # 检查是否在人工按键冷却期内
        if self.is_manual_key_active():
            print(f"人工按键冷却期内，跳过自动按键: {key}")
            return
            
        key = key.lower()  # Convert key to lowercase
        print(f'Casting ability {key}.')
        
        # 记录自动按键信息
        self.last_auto_key = key
        self.last_auto_key_time = time.time()
        
        pyautogui.keyUp(key)
        delay = random.uniform(0.01, 0.2)
        time.sleep(delay)
        pyautogui.keyDown(key)
        
        # 如果按键在WITH_CLICK_KEYS中，则额外点击一次鼠标
        if key in [k.lower() for k in config.WITH_CLICK_KEYS]:
            print(f'Additional mouse click for key {key}')
            # 添加一个小延迟确保按键先执行
            time.sleep(0.05)
            pyautogui.click()    

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
            if key.upper() == 'D':
                key = '0'
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

    def __del__(self):
        """析构函数，确保键盘监听器被正确关闭"""
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

class WinGUI(QWidget):
    # properties
    bot = None
    offset = None  # 用于窗口拖动
    hk = SystemHotkey()

    # 添加信号，用于线程间通信
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.initUI()

        hotkey_tuple = tuple(config.HOTKEY.split(','))
        self.hk.register(hotkey_tuple, callback=self.onHotkeyPressed)
        
        # 将信号连接到在主线程执行的槽函数
        self.hotkey_pressed.connect(self.startRotation)

    def initUI(self):
        # 设置窗口属性
        self.setWindowTitle("Hekili Bot")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(250, 50)  # 增加高度以显示状态信息
        
        # 创建Bot实例
        self.bot = WowBot()
        # 连接bot的信号到更新按键显示的槽
        self.bot.key_detected.connect(self.update_key_display)

        # 创建状态标签
        self.status_label = QLabel("就绪 (" + config.HOTKEY + "切换)", self)  # 更新标签文本提示快捷键
        self.status_label.setStyleSheet("color: #000000; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # 创建按键显示标签
        self.key_label = QLabel("", self)
        self.key_label.setStyleSheet("color: #FF0000; font-size: 16px; font-weight: bold;")
        self.key_label.setAlignment(Qt.AlignCenter)
        self.key_label.setMinimumWidth(40)
        
        # 创建人工按键状态标签
        self.manual_status_label = QLabel("", self)
        self.manual_status_label.setStyleSheet("color: #0000FF; font-size: 10px;")
        self.manual_status_label.setAlignment(Qt.AlignCenter)
        
        # 布局
        main_layout = QVBoxLayout()
        
        # 创建水平布局放置状态标签和按键标签
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.status_label)
        h_layout.addWidget(self.key_label)
        
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.manual_status_label)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        self.setLayout(main_layout)
        
        # 添加定时器更新人工按键状态显示
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_manual_status)
        self.status_timer.start(100)  # 每100ms更新一次状态

    def update_manual_status(self):
        """更新人工按键状态显示"""
        if self.bot and self.bot.is_manual_key_active():
            remaining_time = self.bot.manual_key_cooldown - (time.time() - self.bot.manual_key_time)
            self.manual_status_label.setText(f"人工按键冷却: {remaining_time:.1f}s")
        else:
            self.manual_status_label.setText("")

    def closeEvent(self, event):
        # 清理资源
        if self.bot:
            self.bot.stop()
            if hasattr(self.bot, 'keyboard_listener'):
                self.bot.keyboard_listener.stop()
        event.accept()

    # ...existing code...
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

    def onHotkeyPressed(self, event=None):
        """热键回调函数，仅发射信号"""
        self.hotkey_pressed.emit()
        
    def startRotation(self):
        """在主线程中执行的槽函数"""
        if self.bot.stopped:
            self.status_label.setText("正在运行... (" + config.HOTKEY + "切换)")
            self.bot.start()
        else:
            self.status_label.setText("已停止 (" + config.HOTKEY + "切换)")
            self.bot.stop()

    def showAbout(self):
        QMessageBox.about(self, "关于", "Hekili Rotation Bot\n作者: Hongwt\n\n辅助魔兽世界Hekili插件使用\n\n支持人工按键优先级")

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