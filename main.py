import os
import multiprocessing

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen

import win32gui
from pynput import mouse
from PIL import ImageGrab

import config
from windowcapture import WindowCapture
from bot import WowBot

def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hex(hwnd), win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)

class WinGUI(QWidget):

    # threading properties
    stopped = True
    lock = None

    # properties
    hwnd = None
    bot = None

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Hekili Bot")
        self.setGeometry(300, 300, 335, 400)
        self.setFixedSize(335, 400)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        self.hwnd = win32gui.FindWindow(None, config.WOW_WINDOW_NAME)
        self.capture = WindowCapture()
        self.capture.closeEvent = self.handleWidgetClose

        self.bot = WowBot()

        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()

        self.canvas_hekili_zone = self.__create_canvas_hekili_zone(self)

        self.frame_hekili_zone = self.__create_frame_hekili_zone(self)
        self.label_hekili = self.__create_label_hekili(self.frame_hekili_zone)
        
        self.label_hekili_x = self.__create_label_hekili_x(self.frame_hekili_zone)
        self.input_hekili_x = self.__create_input_hekili_x(self.frame_hekili_zone)
        self.label_hekili_y = self.__create_label_hekili_y(self.frame_hekili_zone)
        self.input_hekili_y = self.__create_input_hekili_y(self.frame_hekili_zone)
        self.label_hekili_w = self.__create_label_hekili_w(self.frame_hekili_zone)
        self.input_hekili_w = self.__create_input_hekili_w(self.frame_hekili_zone)
        self.label_hekili_h = self.__create_label_hekili_h(self.frame_hekili_zone)
        self.input_hekili_h = self.__create_input_hekili_h(self.frame_hekili_zone)

        self.frame_ability_key_zone = self.__create_frame_ability_key_zone(self)
        self.label_ability_key = self.__create_label_ability_key(self.frame_ability_key_zone)
        self.label_ability_key_x = self.__create_label_ability_key_x(self.frame_ability_key_zone)
        self.input_ability_key_x = self.__create_input_ability_key_x(self.frame_ability_key_zone)
        self.label_ability_key_y = self.__create_label_ability_key_y(self.frame_ability_key_zone)
        self.input_ability_key_y = self.__create_input_ability_key_y(self.frame_ability_key_zone)
        self.label_ability_key_w = self.__create_label_ability_key_w(self.frame_ability_key_zone)
        self.input_ability_key_w = self.__create_input_ability_key_w(self.frame_ability_key_zone)
        self.label_ability_key_h = self.__create_label_ability_key_h(self.frame_ability_key_zone)
        self.input_ability_key_h = self.__create_input_ability_key_h(self.frame_ability_key_zone)

        self.frame_ability_cooldown_zone = self.__create_frame_ability_cooldown_zone(self)
        self.label_ability_cooldown = self.__create_label_ability_cooldown(self.frame_ability_cooldown_zone)
        self.label_ability_cooldown_x = self.__create_label_ability_cooldown_x(self.frame_ability_cooldown_zone)
        self.input_ability_cooldown_x = self.__create_input_ability_cooldown_x(self.frame_ability_cooldown_zone)
        self.label_ability_cooldown_y = self.__create_label_ability_cooldown_y(self.frame_ability_cooldown_zone)
        self.input_ability_cooldown_y = self.__create_input_ability_cooldown_y(self.frame_ability_cooldown_zone)
        self.label_ability_cooldown_w = self.__create_label_ability_cooldown_w(self.frame_ability_cooldown_zone)
        self.input_ability_cooldown_w = self.__create_input_ability_cooldown_w(self.frame_ability_cooldown_zone)
        self.label_ability_cooldown_h = self.__create_label_ability_cooldown_h(self.frame_ability_cooldown_zone)
        self.input_ability_cooldown_h = self.__create_input_ability_cooldown_h(self.frame_ability_cooldown_zone)

        # 设置默认值
        self.input_hekili_x.setText(str(config.HEKILI_X))
        self.input_hekili_y.setText(str(config.HEKILI_Y))
        self.input_hekili_w.setText(str(config.HEKILI_W))
        self.input_hekili_h.setText(str(config.HEKILI_H))

        self.input_ability_key_x.setText(str(config.ABILITY_KEY_X))
        self.input_ability_key_y.setText(str(config.ABILITY_KEY_Y))
        self.input_ability_key_w.setText(str(config.ABILITY_KEY_W))
        self.input_ability_key_h.setText(str(config.ABILITY_KEY_H))

        self.input_ability_cooldown_x.setText(str(config.ABILITY_COOLDOWN_X))
        self.input_ability_cooldown_y.setText(str(config.ABILITY_COOLDOWN_Y))
        self.input_ability_cooldown_w.setText(str(config.ABILITY_COOLDOWN_W))
        self.input_ability_cooldown_h.setText(str(config.ABILITY_COOLDOWN_H))

        # 添加按钮
        self.buttonSetZone = QPushButton("设置截图区域")
        self.buttonSetZone.setFixedHeight(35)
        self.buttonSetZone.clicked.connect(self.setHekiliZone)
        self.buttonStart = QPushButton("开始")
        self.buttonStart.setFixedHeight(35)
        self.buttonStart.clicked.connect(self.startRotation)

        # 添加布局到主布局
        layout = QVBoxLayout()
        layout.addWidget(self.buttonSetZone)
        layout.addWidget(self.canvas_hekili_zone)
        layout.addWidget(self.frame_hekili_zone)
        layout.addWidget(self.frame_ability_key_zone)
        layout.addWidget(self.frame_ability_cooldown_zone)
        layout.addWidget(self.buttonStart)

        self.setLayout(layout)

    def __create_canvas_hekili_zone(self, parent):
        canvas = QLabel(parent)
        canvas.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        canvas.setStyleSheet("background-color: #aaa;")
        canvas.setGeometry(10, 100, 315, 120)
        canvas.setFixedHeight(120)
        return canvas

    def __create_frame_hekili_zone(self, parent):
        frame = QFrame(parent)
        frame.setGeometry(10, 225, 315, 35)
        frame.setFixedHeight(35)
        return frame

    def __create_label_hekili(self, parent):
        label = QLabel("Hekili区域：", parent)
        label.setGeometry(0, 2, 80, 30)
        return label

    def __create_label_hekili_x(self, parent):
        label = QLabel("X", parent)
        label.setGeometry(70, 2, 20, 30)
        return label

    def __create_input_hekili_x(self, parent):
        ipt = QLineEdit(parent)
        ipt.setReadOnly(True)
        ipt.setStyleSheet("background-color: #eee;")
        ipt.setGeometry(88, 2, 40, 30)
        return ipt

    def __create_label_hekili_y(self, parent):
        label = QLabel("Y", parent)
        label.setGeometry(130, 2, 20, 30)
        return label

    def __create_input_hekili_y(self, parent):
        ipt = QLineEdit(parent)
        ipt.setReadOnly(True)
        ipt.setStyleSheet("background-color: #eee;")
        ipt.setGeometry(148, 2, 40, 30)
        return ipt

    def __create_label_hekili_w(self, parent):
        label = QLabel("W", parent)
        label.setGeometry(190, 2, 20, 30)
        return label

    def __create_input_hekili_w(self, parent):
        ipt = QLineEdit(parent)
        ipt.setReadOnly(True)
        ipt.setStyleSheet("background-color: #eee;")
        ipt.setGeometry(208, 2, 40, 30)
        return ipt

    def __create_label_hekili_h(self, parent):
        label = QLabel("H", parent)
        label.setGeometry(250, 2, 20, 30)
        return label

    def __create_input_hekili_h(self, parent):
        ipt = QLineEdit(parent)
        ipt.setReadOnly(True)
        ipt.setStyleSheet("background-color: #eee;")
        ipt.setGeometry(268, 2, 40, 30)
        return ipt

    def __create_frame_ability_key_zone(self, parent):
        frame = QFrame(parent)
        frame.setGeometry(10, 275, 315, 35)
        frame.setFixedHeight(35)
        return frame

    def __create_label_ability_key(self, parent):
        label = QLabel("按键区域：", parent)
        label.setGeometry(0, 2, 80, 30)
        return label

    def __create_label_ability_key_x(self, parent):
        label = QLabel("X", parent)
        label.setGeometry(70, 2, 30, 30)
        return label

    def __create_input_ability_key_x(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(88, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_key_y(self, parent):
        label = QLabel("Y", parent)
        label.setGeometry(130, 2, 30, 30)
        return label

    def __create_input_ability_key_y(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(148, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_key_w(self, parent):
        label = QLabel("W", parent)
        label.setGeometry(190, 2, 30, 30)
        return label

    def __create_input_ability_key_w(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(208, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_key_h(self, parent):
        label = QLabel("H", parent)
        label.setGeometry(250, 2, 30, 30)
        return label

    def __create_input_ability_key_h(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(268, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_frame_ability_cooldown_zone(self, parent):
        frame = QFrame(parent)
        frame.setGeometry(10, 325, 315, 35)
        frame.setFixedHeight(35)
        return frame

    def __create_label_ability_cooldown(self, parent):
        label = QLabel("冷却区域：", parent)
        label.setGeometry(0, 2, 80, 30)
        return label

    def __create_label_ability_cooldown_x(self, parent):
        label = QLabel("X", parent)
        label.setGeometry(70, 2, 30, 30)
        return label

    def __create_input_ability_cooldown_x(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(88, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_cooldown_y(self, parent):
        label = QLabel("Y", parent)
        label.setGeometry(130, 2, 30, 30)
        return label

    def __create_input_ability_cooldown_y(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(148, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_cooldown_w(self, parent):
        label = QLabel("W", parent)
        label.setGeometry(190, 2, 30, 30)
        return label

    def __create_input_ability_cooldown_w(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(208, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt

    def __create_label_ability_cooldown_h(self, parent):
        label = QLabel("H", parent)
        label.setGeometry(250, 2, 30, 30)
        return label

    def __create_input_ability_cooldown_h(self, parent):
        ipt = QLineEdit(parent)
        ipt.setGeometry(268, 2, 40, 30)
        ipt.textChanged.connect(self.handleInputChanged)
        return ipt
    def setHekiliZone(self):
        # 将窗口设置为前置
        if self.hwnd:
            win32gui.SetForegroundWindow(self.hwnd)
        # 调用 ScreenshotWidget 并获取截图区域
        self.capture.show()

    def handleInputChanged(self, event):
        ability_key_x = self.input_ability_key_x.text()
        ability_key_y = self.input_ability_key_y.text()
        ability_key_w = self.input_ability_key_w.text()
        ability_key_h = self.input_ability_key_h.text()

        ability_cooldown_x = self.input_ability_cooldown_x.text()
        ability_cooldown_y = self.input_ability_cooldown_y.text()
        ability_cooldown_w = self.input_ability_cooldown_w.text()
        ability_cooldown_h = self.input_ability_cooldown_h.text()

        if ability_key_x and ability_key_x.isdigit():
            config.ABILITY_KEY_X = int(ability_key_x)
        if ability_key_y and ability_key_y.isdigit():
            config.ABILITY_KEY_Y = int(ability_key_y)
        if ability_key_w and ability_key_w.isdigit():
            config.ABILITY_KEY_W = int(ability_key_w)
        if ability_key_h and ability_key_h.isdigit():
            config.ABILITY_KEY_H = int(ability_key_h)

        if ability_cooldown_x and ability_cooldown_x.isdigit():
            config.ABILITY_COOLDOWN_X = int(ability_cooldown_x)
        if ability_cooldown_y and ability_cooldown_y.isdigit():
            config.ABILITY_COOLDOWN_Y = int(ability_cooldown_y)
        if ability_cooldown_w and ability_cooldown_w.isdigit():
            config.ABILITY_COOLDOWN_W = int(ability_cooldown_w)
        if ability_cooldown_h and ability_cooldown_h.isdigit():
            config.ABILITY_COOLDOWN_H = int(ability_cooldown_h)

        self.paintImage(event)

    def handleWidgetClose(self, event):
        x1, y1, x2, y2 = int(self.capture.x1), int(self.capture.y1), int(self.capture.x2), int(self.capture.y2)
        print(x1, y1, x2, y2)

        x = x1
        y = y1
        width = x2 - x1
        height = y2 - y1
        print(x, y, width, height)

        self.input_hekili_x.setText(str(x))
        self.input_hekili_y.setText(str(y))
        self.input_hekili_w.setText(str(width))
        self.input_hekili_h.setText(str(height))

        config.HEKILI_X = x
        config.HEKILI_Y = y
        config.HEKILI_W = width
        config.HEKILI_H = height

        self.paintImage(event)

    def paintEvent(self, event):
        # Add code here to switch windows
        self.paintImage(event)

    def on_mouse_event(self, x, y, button, pressed):
        # print(f"Mouse event: {button} {'pressed' if pressed else 'released'} at ({x}, {y})")
        if button == mouse.Button.x2 and pressed:
            self.startRotation()

    def paintImage(self, event):
        screenshot = ImageGrab.grab(bbox=(config.HEKILI_X, 
                                            config.HEKILI_Y, 
                                            config.HEKILI_X + config.HEKILI_W, 
                                            config.HEKILI_Y + config.HEKILI_H))
        # 将截图转换为 QImage 对象
        qt_image = QImage(screenshot.tobytes(), screenshot.width, screenshot.height, screenshot.width * 3, QImage.Format_RGB888)
        # Convert qt_image to QPixmap
        pixmap = QPixmap.fromImage(qt_image)
        # 绘制矩形框
        painter = QPainter(pixmap)
        pen = QPen(Qt.red)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(config.ABILITY_KEY_X, config.ABILITY_KEY_Y, 
                 config.ABILITY_KEY_W, config.ABILITY_KEY_H)
        painter.drawRect(config.ABILITY_COOLDOWN_X, config.ABILITY_COOLDOWN_Y, 
            config.ABILITY_COOLDOWN_W, config.ABILITY_COOLDOWN_H)
        painter.end()  # Add this line to end the painting process

        # Set the pixmap as the background of the canvas
        self.canvas_hekili_zone.setPixmap(pixmap)

    def startRotation(self):
        if (self.bot.stopped):
            print("开始...")
            # 将窗口设置为前置
            if self.hwnd:
                win32gui.SetForegroundWindow(self.hwnd)
            self.bot.start()
            self.buttonStart.setText("结束")
        else:
            print("结束...")
            self.bot.stop()
            self.buttonStart.setText("开始")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    list_window_names()

    app = QApplication([])
    win = WinGUI()
    win.show()
    app.exec_()