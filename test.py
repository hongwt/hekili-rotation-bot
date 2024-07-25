# 导入 PyQt5 模块
from PyQt5.QtWidgets import QApplication, QWidget
from windowcapture import ScreenshotWidget

def main():
    # 创建 QApplication 实例
    app = QApplication([])

    # 创建 QWidget 实例
    window = QWidget()
    
    # 设置窗口标题和大小
    window.setWindowTitle("示例窗口")
    window.resize(400, 300)
    
    # 显示窗口
    window.show()


    
    # 执行应用程序的事件循环
    app.exec_()

if __name__ == "__main__":
    main()