from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QGuiApplication

class WindowCapture(QWidget):

    # Properties
    x1, y1, x2, y2 = 0, 0, 0, 0

    def __init__(self):
        super().__init__()
        self.begin = None
        self.end = None
        self.show_help = True  # 是否显示帮助信息
        
        # 获取屏幕缩放比例
        self.device_pixel_ratio = QGuiApplication.primaryScreen().devicePixelRatio()
        
        # 设置窗口属性
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowOpacity(0.3)  # 稍微调低透明度使用户更容易看到底层内容
        self.setWindowState(Qt.WindowFullScreen)
        
        # 设置光标为十字形
        self.setCursor(Qt.CrossCursor)
 
    def keyPressEvent(self, event):
        # 按ESC键退出截图
        if event.key() == Qt.Key_Escape:
            self.close()
        # 按H键切换帮助提示的显示
        elif event.key() == Qt.Key_H:
            self.show_help = not self.show_help
            self.update()
            
    def mousePressEvent(self, event):
        self.begin = event.position()
        self.end = event.position()
        self.update()
 
    def mouseMoveEvent(self, event):
        self.end = event.position()
        self.update()
 
    def mouseReleaseEvent(self, event):
        # 获取坐标
        self.x1, self.y1 = int(self.begin.x() * self.device_pixel_ratio), int(self.begin.y() * self.device_pixel_ratio)
        self.x2, self.y2 = int(self.end.x() * self.device_pixel_ratio), int(self.end.y() * self.device_pixel_ratio)
        
        # 确保x1,y1是左上角点，x2,y2是右下角点
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
            
        # 如果选择范围太小，忽略此次选择
        if abs(self.x2 - self.x1) < 5 or abs(self.y2 - self.y1) < 5:
            return
            
        self.close()
 
    def paintEvent(self, event):
        if not self.begin:
            # 如果还未开始选择，绘制帮助信息
            if self.show_help:
                self.drawHelpText()
            return
            
        painter = QPainter(self)
        
        # 绘制半透明遮罩
        painter.fillRect(0, 0, self.width(), self.height(), QColor(0, 0, 0, 50))
        
        # 计算选择区域
        x = min(self.begin.x(), self.end.x())
        y = min(self.begin.y(), self.end.y())
        w = abs(self.end.x() - self.begin.x())
        h = abs(self.end.y() - self.begin.y())
        
        # 选择区域设为透明
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(x, y, w, h, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        # 绘制边框
        pen = QPen(QColor(255, 50, 50))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(x, y, w, h)
        
        # 显示选择尺寸
        x_phys = int(x * self.device_pixel_ratio)
        y_phys = int(y * self.device_pixel_ratio)
        w_phys = int(w * self.device_pixel_ratio)
        h_phys = int(h * self.device_pixel_ratio)
        
        size_text = f"{x_phys}:{y_phys} {w_phys} × {h_phys}"
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(QColor(255, 0, 0))
        
        # 计算文本位置，确保显示在屏幕内
        text_x = x + 5
        text_y = y - 10 if y > 20 else y + h + 20
        painter.drawText(text_x, text_y, size_text)
    
    def drawHelpText(self):
        painter = QPainter(self)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12))
        
        help_text = [
            "拖拽鼠标选择截图区域",
            "按ESC键取消截图",
            "按H键隐藏/显示帮助"
        ]
        
        y_pos = 50
        for text in help_text:
            painter.drawText(50, y_pos, text)
            y_pos += 25

def main():
    app = QApplication([])
    widget = WindowCapture()
    widget.show()
    app.exec()  # PySide6中不需要括号
 
 
if __name__ == '__main__':
    main()