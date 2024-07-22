import tkinter as tk
from windowcapture import ScreenshotWidget
from PyQt5.QtWidgets import QApplication

"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
# 示例下载 https://www.pytk.net/blog/1702564569.html
class Controller:
    # 导入UI类后，替换以下的 object 类型，将获得 IDE 属性提示功能
    ui: object
    def __init__(self):
        pass
    def init(self, ui):
        """
        得到UI实例，对组件进行初始化配置
        """
        self.ui = ui
        # TODO 组件初始化 赋值操作
    def set_hekili_zone(self,evt):
        app = QApplication([])
        widget = ScreenshotWidget()        
        widget.show()
        app.exec_()

        x1, y1, x2, y2 = int(widget.x1), int(widget.y1), int(widget.x2), int(widget.y2)
        print(x1, y1, x2, y2)
        
        x = x1
        y = y1
        width = x2 - x1
        height = y2 - y1
        print(x, y, width, height)

        self.ui.tk_input_hekili_x.delete(0, tk.END)
        self.ui.tk_input_hekili_x.insert(tk.END, str(x))
        self.ui.tk_input_hekili_y.delete(0, tk.END)
        self.ui.tk_input_hekili_y.insert(tk.END, str(y))
        self.ui.tk_input_hekili_h.delete(0, tk.END)
        self.ui.tk_input_hekili_h.insert(tk.END, str(height))
        self.ui.tk_input_hekili_w.delete(0, tk.END)
        self.ui.tk_input_hekili_w.insert(tk.END, str(width))
    def start_rotation(self,evt):
        print("<Button-1>事件未处理:",evt)
