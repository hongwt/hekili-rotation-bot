"""
本代码由[Tkinter布局助手]生成
官网:https://www.pytk.net
QQ交流群:905019785
在线反馈:https://support.qq.com/product/618914
"""
import random
from tkinter import *
from tkinter.ttk import *
class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_button_lyvdnkur = self.__tk_button_lyvdnkur(self)
        self.key_zone_frame = self.__key_zone_frame(self)
        self.key_label_x = self.__key_label_x( self.key_zone_frame) 
        self.key_input_x = self.__key_input_x( self.key_zone_frame) 
        self.key_label_y = self.__key_label_y( self.key_zone_frame) 
        self.key_input_y = self.__key_input_y( self.key_zone_frame) 
        self.key_label_h = self.__key_label_h( self.key_zone_frame) 
        self.key_input_h = self.__key_input_h( self.key_zone_frame) 
        self.key_label_w = self.__key_label_w( self.key_zone_frame) 
        self.key_input_w = self.__key_input_w( self.key_zone_frame) 
        self.key_zone_button = self.__key_zone_button( self.key_zone_frame) 
        self.coodown_zone_frame = self.__coodown_zone_frame(self)
        self.cooldown_label_x = self.__cooldown_label_x( self.coodown_zone_frame) 
        self.cooldown_input_x = self.__cooldown_input_x( self.coodown_zone_frame) 
        self.cooldown_label_y = self.__cooldown_label_y( self.coodown_zone_frame) 
        self.cooldown_input_y = self.__cooldown_input_y( self.coodown_zone_frame) 
        self.cooldown_label_h = self.__cooldown_label_h( self.coodown_zone_frame) 
        self.cooldown_input_h = self.__cooldown_input_h( self.coodown_zone_frame) 
        self.cooldown_label_w = self.__cooldown_label_w( self.coodown_zone_frame) 
        self.cooldown_input_w = self.__cooldown_input_w( self.coodown_zone_frame) 
        self.cooldown_zone_button = self.__cooldown_zone_button( self.coodown_zone_frame) 
    def __win(self):
        self.title("Tkinter布局助手")
        # 设置窗口大小、居中
        width = 342
        height = 381
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        
        self.resizable(width=False, height=False)
        
    def scrollbar_autohide(self,vbar, hbar, widget):
        """自动隐藏滚动条"""
        def show():
            if vbar: vbar.lift(widget)
            if hbar: hbar.lift(widget)
        def hide():
            if vbar: vbar.lower(widget)
            if hbar: hbar.lower(widget)
        hide()
        widget.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Enter>", lambda e: show())
        if vbar: vbar.bind("<Leave>", lambda e: hide())
        if hbar: hbar.bind("<Enter>", lambda e: show())
        if hbar: hbar.bind("<Leave>", lambda e: hide())
        widget.bind("<Leave>", lambda e: hide())
    
    def v_scrollbar(self,vbar, widget, x, y, w, h, pw, ph):
        widget.configure(yscrollcommand=vbar.set)
        vbar.config(command=widget.yview)
        vbar.place(relx=(w + x) / pw, rely=y / ph, relheight=h / ph, anchor='ne')
    def h_scrollbar(self,hbar, widget, x, y, w, h, pw, ph):
        widget.configure(xscrollcommand=hbar.set)
        hbar.config(command=widget.xview)
        hbar.place(relx=x / pw, rely=(y + h) / ph, relwidth=w / pw, anchor='sw')
    def create_bar(self,master, widget,is_vbar,is_hbar, x, y, w, h, pw, ph):
        vbar, hbar = None, None
        if is_vbar:
            vbar = Scrollbar(master)
            self.v_scrollbar(vbar, widget, x, y, w, h, pw, ph)
        if is_hbar:
            hbar = Scrollbar(master, orient="horizontal")
            self.h_scrollbar(hbar, widget, x, y, w, h, pw, ph)
        self.scrollbar_autohide(vbar, hbar, widget)
    def __tk_button_lyvdnkur(self,parent):
        btn = Button(parent, text="开始", takefocus=False,)
        btn.place(x=10, y=292, width=319, height=59)
        return btn
    def __key_zone_frame(self,parent):
        frame = Frame(parent,)
        frame.place(x=4, y=22, width=330, height=74)
        return frame
    def __key_label_x(self,parent):
        label = Label(parent,text="X:",anchor="center", )
        label.place(x=5, y=44, width=25, height=20)
        return label
    def __key_input_x(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=35, y=44, width=35, height=20)
        return ipt
    def __key_label_y(self,parent):
        label = Label(parent,text="Y:",anchor="center", )
        label.place(x=75, y=44, width=25, height=20)
        return label
    def __key_input_y(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=105, y=44, width=35, height=20)
        return ipt
    def __key_label_h(self,parent):
        label = Label(parent,text="Height:",anchor="center", )
        label.place(x=150, y=44, width=43, height=20)
        return label
    def __key_input_h(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=200, y=44, width=35, height=20)
        return ipt
    def __key_label_w(self,parent):
        label = Label(parent,text="Width:",anchor="center", )
        label.place(x=240, y=44, width=43, height=20)
        return label
    def __key_input_w(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=290, y=44, width=35, height=20)
        return ipt
    def __key_zone_button(self,parent):
        btn = Button(parent, text="Hekili技能快捷键区域", takefocus=False,)
        btn.place(x=17, y=5, width=140, height=30)
        return btn
    def __coodown_zone_frame(self,parent):
        frame = Frame(parent,)
        frame.place(x=5, y=107, width=330, height=74)
        return frame
    def __cooldown_label_x(self,parent):
        label = Label(parent,text="X:",anchor="center", )
        label.place(x=5, y=44, width=25, height=20)
        return label
    def __cooldown_input_x(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=35, y=44, width=35, height=20)
        return ipt
    def __cooldown_label_y(self,parent):
        label = Label(parent,text="Y:",anchor="center", )
        label.place(x=75, y=44, width=25, height=20)
        return label
    def __cooldown_input_y(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=105, y=44, width=35, height=20)
        return ipt
    def __cooldown_label_h(self,parent):
        label = Label(parent,text="Height:",anchor="center", )
        label.place(x=150, y=44, width=43, height=20)
        return label
    def __cooldown_input_h(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=200, y=44, width=35, height=20)
        return ipt
    def __cooldown_label_w(self,parent):
        label = Label(parent,text="Width:",anchor="center", )
        label.place(x=240, y=44, width=43, height=20)
        return label
    def __cooldown_input_w(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=290, y=44, width=35, height=20)
        return ipt
    def __cooldown_zone_button(self,parent):
        btn = Button(parent, text="Hekili技能冷却区域", takefocus=False,)
        btn.place(x=13, y=5, width=140, height=30)
        return btn
class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)
    def __event_bind(self):
        self.tk_button_lyvdnkur.bind('<Button-1>',self.ctl.start)
        self.key_zone_button.bind('<Button-1>',self.ctl.set_ability_key_zone)
        self.cooldown_zone_button.bind('<Button-1>',self.ctl.set_ability_cooldown_zone)
        pass
    def __style_config(self):
        pass
if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()