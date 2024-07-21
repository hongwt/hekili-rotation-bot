import tkinter as tk
from windowcapture import ScreenshotWidget
from PyQt5.QtWidgets import QApplication

class Controller:
    ui: object

    def __init__(self):
        self.ui = None

    def init(self, ui):
        self.ui = ui

    # Add the init method here
    def init(self, ui):
        pass

    def start(self, evt):
        print("<Button-1>事件未处理:", evt)

    def set_ability_key_zone(self, evt):
        print("<Button-1>事件未处理:", evt)
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

        self.ui.key_input_x.delete(0, tk.END)
        self.ui.key_input_x.insert(tk.END, str(x))
        self.ui.key_input_y.delete(0, tk.END)
        self.ui.key_input_y.insert(tk.END, str(y))
        self.ui.key_input_h.delete(0, tk.END)
        self.ui.key_input_h.insert(tk.END, str(height))
        self.ui.key_input_w.delete(0, tk.END)
        self.ui.key_input_w.insert(tk.END, str(width))

    def set_ability_cooldown_zone(self, evt):
        print("<Button-1>事件未处理:", evt)
        
    def set_ability_cooldown_zone(self, evt):
        print("<Button-1>事件未处理:", evt)
        


    def set_ability_cooldown_zone(self, evt):
        print("<Button-1>事件未处理:", evt)
        
    def set_ability_cooldown_zone(self,evt):
        print("<Button-1>事件未处理:",evt)
