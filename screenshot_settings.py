from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PySide6.QtWidgets import (QWidget, QDialog, QLabel, QLineEdit, QPushButton, 
                              QHBoxLayout, QVBoxLayout, QGroupBox,
                              QDialogButtonBox, QMessageBox, QFrame, QScrollArea)
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont

import win32gui
from PIL import ImageGrab

import config
from window_capture import WindowCapture
import config

class ScreenshotSettingsDialog(QDialog):
    def __init__(self, parent=None, hwnd=None):
        super().__init__(parent)
        self.hwnd = hwnd
        self.capture = None
        
        # 初始化界面
        self.initUI()
        
        # 启动定时器更新截图
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateScreenshot)
        self.timer.start(500)
        
    def initUI(self):
        self.setWindowTitle("截图设置")
        self.setMinimumSize(300, 400)
        self.setFixedWidth(300)  # 设置固定宽度
        
        # 创建滚动区域来容纳截图预览
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(80)  # 固定高度
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 截图预览区域
        self.screenshot_frame = QFrame()
        self.screenshot_frame.setFrameShape(QFrame.StyledPanel)
        self.screenshot_frame.setFrameShadow(QFrame.Sunken)
        
        # 创建一个容器存放截图标签
        self.screenshot_container = QWidget(self.screenshot_frame)
        container_layout = QVBoxLayout(self.screenshot_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.screenshot_label = QLabel(self.screenshot_container)
        self.screenshot_label.setAlignment(Qt.AlignCenter)
        self.screenshot_label.setStyleSheet("background-color: #2a2a2a;")
        self.screenshot_label.setText("截图预览区域")
        
        container_layout.addWidget(self.screenshot_label)
        
        # 将容器设置为滚动区域的内容
        self.scroll_area.setWidget(self.screenshot_container)
        
        # 捕获截图按钮
        self.capture_button = QPushButton("捕获新区域", self)
        self.capture_button.clicked.connect(self.captureNewArea)
        
        # 坐标设置区域 - 保持不变
        screenshot_group = QGroupBox("截图区域坐标", self)
        screenshot_layout = QVBoxLayout()
        
        # X和Y设置
        x_y_layout = QHBoxLayout()
        
        self.screenshot_x_label = QLabel("X:", self)
        self.screenshot_x_edit = QLineEdit(str(config.HEKILI_X), self)
        self.screenshot_x_edit.textChanged.connect(self.validateInputs)
        
        self.screenshot_y_label = QLabel("Y:", self)
        self.screenshot_y_edit = QLineEdit(str(config.HEKILI_Y), self)
        self.screenshot_y_edit.textChanged.connect(self.validateInputs)
        
        x_y_layout.addWidget(self.screenshot_x_label)
        x_y_layout.addWidget(self.screenshot_x_edit)
        x_y_layout.addWidget(self.screenshot_y_label)
        x_y_layout.addWidget(self.screenshot_y_edit)
        
        # 宽度和高度设置
        w_h_layout = QHBoxLayout()
        
        self.screenshot_w_label = QLabel("宽:", self)
        self.screenshot_w_edit = QLineEdit(str(config.HEKILI_W), self)
        self.screenshot_w_edit.textChanged.connect(self.validateInputs)
        
        self.screenshot_h_label = QLabel("高:", self)
        self.screenshot_h_edit = QLineEdit(str(config.HEKILI_H), self)
        self.screenshot_h_edit.textChanged.connect(self.validateInputs)
        
        w_h_layout.addWidget(self.screenshot_w_label)
        w_h_layout.addWidget(self.screenshot_w_edit)
        w_h_layout.addWidget(self.screenshot_h_label)
        w_h_layout.addWidget(self.screenshot_h_edit)
        
        screenshot_layout.addLayout(x_y_layout)
        screenshot_layout.addLayout(w_h_layout)
        
        screenshot_group.setLayout(screenshot_layout)
        
        # 按键区域设置 - 保持不变
        ability_group = QGroupBox("按键区域坐标", self)
        ability_layout = QVBoxLayout()
        
        # X和Y设置
        ability_x_y_layout = QHBoxLayout()
        
        self.ability_x_label = QLabel("X:", self)
        self.ability_x_edit = QLineEdit(str(config.ABILITY_KEY_X), self)
        self.ability_x_edit.textChanged.connect(self.validateInputs)
        
        self.ability_y_label = QLabel("Y:", self)
        self.ability_y_edit = QLineEdit(str(config.ABILITY_KEY_Y), self)
        self.ability_y_edit.textChanged.connect(self.validateInputs)
        
        ability_x_y_layout.addWidget(self.ability_x_label)
        ability_x_y_layout.addWidget(self.ability_x_edit)
        ability_x_y_layout.addWidget(self.ability_y_label)
        ability_x_y_layout.addWidget(self.ability_y_edit)
        
        # 宽度和高度设置
        ability_w_h_layout = QHBoxLayout()
        
        self.ability_w_label = QLabel("宽:", self)
        self.ability_w_edit = QLineEdit(str(config.ABILITY_KEY_W), self)
        self.ability_w_edit.textChanged.connect(self.validateInputs)
        
        self.ability_h_label = QLabel("高:", self)
        self.ability_h_edit = QLineEdit(str(config.ABILITY_KEY_H), self)
        self.ability_h_edit.textChanged.connect(self.validateInputs)
        
        ability_w_h_layout.addWidget(self.ability_w_label)
        ability_w_h_layout.addWidget(self.ability_w_edit)
        ability_w_h_layout.addWidget(self.ability_h_label)
        ability_w_h_layout.addWidget(self.ability_h_edit)
        
        ability_layout.addLayout(ability_x_y_layout)
        ability_layout.addLayout(ability_w_h_layout)
        
        ability_group.setLayout(ability_layout)
        
        # 指导文本
        guide_text = QLabel('提示：点击"捕获新区域"按钮选择截图区域，或者手动编辑坐标值。', self)
        guide_text.setWordWrap(True)
        guide_text.setStyleSheet("color: #666; font-size: 11px;")
        
        # 底部按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)  # 使用滚动区域替代原来的frame
        main_layout.addWidget(self.capture_button)
        main_layout.addWidget(screenshot_group)
        main_layout.addWidget(ability_group)
        main_layout.addWidget(guide_text)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)

    def captureNewArea(self):
        # 关闭更新定时器
        self.timer.stop()
        
        # 设置WoW窗口为前景
        if self.hwnd:
            win32gui.SetForegroundWindow(self.hwnd)
        
        # 暂时隐藏设置对话框
        self.hide()
        
        # 创建并显示截图工具
        self.capture = WindowCapture()
        self.capture.closeEvent = self.handleCaptureClosed
        self.capture.show()
    
    # 修改 handleCaptureClosed 方法

    def handleCaptureClosed(self, event):
        x1, y1, x2, y2 = self.capture.x1, self.capture.y1, self.capture.x2, self.capture.y2
        
        if x2 - x1 > 0 and y2 - y1 > 0:
            # 更新截图区域坐标输入框
            self.screenshot_x_edit.setText(str(x1))
            self.screenshot_y_edit.setText(str(y1))
            self.screenshot_w_edit.setText(str(x2 - x1))
            self.screenshot_h_edit.setText(str(y2 - y1))
        
        # 重新显示设置对话框
        self.show()
        
        # 重新启动更新定时器并更新截图预览
        self.timer.start()
        self.updateScreenshot()  # 立即更新截图预览
        
        event.accept()
    
    def validateInputs(self):
        # 检查输入是否为有效数字
        try:
            x = int(self.screenshot_x_edit.text()) if self.screenshot_x_edit.text() else 0
            y = int(self.screenshot_y_edit.text()) if self.screenshot_y_edit.text() else 0
            w = int(self.screenshot_w_edit.text()) if self.screenshot_w_edit.text() else 0
            h = int(self.screenshot_h_edit.text()) if self.screenshot_h_edit.text() else 0
            
            ax = int(self.ability_x_edit.text()) if self.ability_x_edit.text() else 0
            ay = int(self.ability_y_edit.text()) if self.ability_y_edit.text() else 0
            aw = int(self.ability_w_edit.text()) if self.ability_w_edit.text() else 0
            ah = int(self.ability_h_edit.text()) if self.ability_h_edit.text() else 0
            
            # 根据新输入的值更新截图预览
            if w > 0 and h > 0:
                self.updateScreenshot()
        except ValueError:
            # 无效输入，不更新截图
            pass
    
    def updateScreenshot(self):
        try:
            # 获取坐标值部分保持不变
            x = int(self.screenshot_x_edit.text()) if self.screenshot_x_edit.text() else 0
            y = int(self.screenshot_y_edit.text()) if self.screenshot_y_edit.text() else 0
            w = int(self.screenshot_w_edit.text()) if self.screenshot_w_edit.text() else 0
            h = int(self.screenshot_h_edit.text()) if self.screenshot_h_edit.text() else 0
            
            ax = int(self.ability_x_edit.text()) if self.ability_x_edit.text() else 0
            ay = int(self.ability_y_edit.text()) if self.ability_y_edit.text() else 0
            aw = int(self.ability_w_edit.text()) if self.ability_w_edit.text() else 0
            ah = int(self.ability_h_edit.text()) if self.ability_h_edit.text() else 0
            
            if w <= 0 or h <= 0:
                return
            
            # 截取屏幕区域
            screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            
            # 转换为QImage
            qt_image = QImage(screenshot.tobytes(), screenshot.width, screenshot.height, 
                            screenshot.width * 3, QImage.Format_RGB888)
            
            # 转换为QPixmap并绘制按键区域
            pixmap = QPixmap.fromImage(qt_image)
            
            if pixmap.width() > 0 and pixmap.height() > 0:
                # 直接使用原始大小，不进行缩放
                display_pixmap = QPixmap(pixmap)  # 创建副本，以便绘制
                
                # 如果有设置按键区域，绘制红色边框
                if aw > 0 and ah > 0:
                    painter = QPainter(display_pixmap)
                    pen = QPen(Qt.red)
                    pen.setWidth(2)
                    painter.setPen(pen)
                    
                    # 绘制矩形 - 使用原始坐标
                    painter.drawRect(ax, ay, aw, ah)
                    painter.end()
                
                # 设置预览图像
                self.screenshot_label.setPixmap(display_pixmap)
                
                # 调整容器大小以适应图像
                self.screenshot_label.setFixedSize(display_pixmap.size())
                self.screenshot_container.setMinimumSize(display_pixmap.size())
                
                # 不再调整对话框大小
            
        except Exception as e:
            print(f"截图更新错误: {e}")
    
    def accept(self):
        try:
            # 获取输入的坐标值
            screenshot_x = int(self.screenshot_x_edit.text())
            screenshot_y = int(self.screenshot_y_edit.text())
            screenshot_w = int(self.screenshot_w_edit.text())
            screenshot_h = int(self.screenshot_h_edit.text())
            
            ability_x = int(self.ability_x_edit.text())
            ability_y = int(self.ability_y_edit.text())
            ability_w = int(self.ability_w_edit.text())
            ability_h = int(self.ability_h_edit.text())
            
            # 验证输入值
            if screenshot_w <= 0 or screenshot_h <= 0:
                QMessageBox.warning(self, "输入错误", "截图区域的宽度和高度必须大于0")
                return
                
            if ability_w <= 0 or ability_h <= 0:
                QMessageBox.warning(self, "输入错误", "按键区域的宽度和高度必须大于0")
                return
            
            # 检查按键区域是否在截图区域内
            if ability_x < 0 or ability_y < 0 or ability_x + ability_w > screenshot_w or ability_y + ability_h > screenshot_h:
                result = QMessageBox.question(
                    self, 
                    "警告", 
                    "按键区域超出了截图区域的范围，这可能导致无法正确识别。是否继续？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if result == QMessageBox.No:
                    return
            
            # 更新配置
            config.HEKILI_X = screenshot_x
            config.HEKILI_Y = screenshot_y
            config.HEKILI_W = screenshot_w
            config.HEKILI_H = screenshot_h
            
            config.ABILITY_KEY_X = ability_x
            config.ABILITY_KEY_Y = ability_y
            config.ABILITY_KEY_W = ability_w
            config.ABILITY_KEY_H = ability_h
            
            # 保存配置到文件
            config.save_config()
            
            # 关闭对话框
            super().accept()
            
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字")
    
    def resizeEvent(self, event):
        # 窗口大小改变时更新截图
        super().resizeEvent(event)
        self.updateScreenshot()

    def closeEvent(self, event):
        # 停止定时器
        self.timer.stop()
        super().closeEvent(event)