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
        self.tk_label_window_name = self.__tk_label_window_name(self)
        self.tk_select_box_window_name = self.__tk_select_box_window_name(self)
        self.tk_button_set_hekili_zone = self.__tk_button_set_hekili_zone(self)
        self.tk_canvas_hekili_zone = self.__tk_canvas_hekili_zone(self)
        self.tk_button_start = self.__tk_button_start(self)
        self.tk_frame_hekili_zone = self.__tk_frame_hekili_zone(self)
        self.tk_label_hekili = self.__tk_label_hekili( self.tk_frame_hekili_zone) 
        self.tk_label_hekili_x = self.__tk_label_hekili_x( self.tk_frame_hekili_zone) 
        self.tk_input_hekili_x = self.__tk_input_hekili_x( self.tk_frame_hekili_zone) 
        self.tk_label_hekili_y = self.__tk_label_hekili_y( self.tk_frame_hekili_zone) 
        self.tk_input_hekili_y = self.__tk_input_hekili_y( self.tk_frame_hekili_zone) 
        self.tk_label_hekili_w = self.__tk_label_hekili_w( self.tk_frame_hekili_zone) 
        self.tk_input_hekili_w = self.__tk_input_hekili_w( self.tk_frame_hekili_zone) 
        self.tk_label_hekili_h = self.__tk_label_hekili_h( self.tk_frame_hekili_zone) 
        self.tk_input_hekili_h = self.__tk_input_hekili_h( self.tk_frame_hekili_zone) 
        self.tk_frame_ability_key_zone = self.__tk_frame_ability_key_zone(self)
        self.tk_label_ability_key = self.__tk_label_ability_key( self.tk_frame_ability_key_zone)
        self.tk_label_ability_key_x = self.__tk_label_ability_key_x( self.tk_frame_ability_key_zone) 
        self.tk_input_ability_key_x = self.__tk_input_ability_key_x( self.tk_frame_ability_key_zone) 
        self.tk_label_ability_key_y = self.__tk_label_ability_key_y( self.tk_frame_ability_key_zone) 
        self.tk_input_ability_key_y = self.__tk_input_ability_key_y( self.tk_frame_ability_key_zone) 
        self.tk_label_ability_key_w = self.__tk_label_ability_key_w( self.tk_frame_ability_key_zone) 
        self.tk_input_ability_key_w = self.__tk_input_ability_key_w( self.tk_frame_ability_key_zone) 
        self.tk_label_ability_key_h = self.__tk_label_ability_key_h( self.tk_frame_ability_key_zone) 
        self.tk_input_ability_key_h = self.__tk_input_ability_key_h( self.tk_frame_ability_key_zone) 
        self.tk_frame_ability_cooldown_zone = self.__tk_frame_ability_cooldown_zone(self)
        self.tk_label_ability_cooldown = self.__tk_label_ability_cooldown( self.tk_frame_ability_cooldown_zone) 
        self.tk_label_ability_cooldown_x = self.__tk_label_ability_cooldown_x( self.tk_frame_ability_cooldown_zone) 
        self.tk_input_ability_cooldown_x = self.__tk_input_ability_cooldown_x( self.tk_frame_ability_cooldown_zone) 
        self.tk_label_ability_cooldown_y = self.__tk_label_ability_cooldown_y( self.tk_frame_ability_cooldown_zone) 
        self.tk_input_ability_cooldown_y = self.__tk_input_ability_cooldown_y( self.tk_frame_ability_cooldown_zone) 
        self.tk_label_ability_cooldown_w = self.__tk_label_ability_cooldown_w( self.tk_frame_ability_cooldown_zone) 
        self.tk_input_ability_cooldown_w = self.__tk_input_ability_cooldown_w( self.tk_frame_ability_cooldown_zone) 
        self.tk_label_ability_cooldown_h = self.__tk_label_ability_cooldown_h( self.tk_frame_ability_cooldown_zone) 
        self.tk_input_ability_cooldown_h = self.__tk_input_ability_cooldown_h( self.tk_frame_ability_cooldown_zone) 
    def __win(self):
        self.title("Hekili辅助")
        # 设置窗口大小、居中
        width = 335
        height = 450
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
    def __tk_label_window_name(self,parent):
        label = Label(parent,text="游戏窗口：",anchor="center", )
        label.place(x=10, y=9, width=71, height=30)
        return label
    def __tk_select_box_window_name(self,parent):
        cb = Combobox(parent, state="readonly", )
        cb['values'] = ("列表框","Python","Tkinter Helper")
        cb.place(x=102, y=9, width=219, height=30)
        return cb
    def __tk_button_set_hekili_zone(self,parent):
        btn = Button(parent, text="设置截图区域（Hekili）", takefocus=False,)
        btn.place(x=10, y=59, width=314, height=30)
        return btn
    def __tk_canvas_hekili_zone(self,parent):
        canvas = Canvas(parent,bg="#aaa")
        canvas.place(x=10, y=100, width=315, height=115)
        return canvas
    def __tk_button_start(self,parent):
        btn = Button(parent, text="开始", takefocus=False,)
        btn.place(x=10, y=380, width=315, height=59)
        return btn
    def __tk_frame_hekili_zone(self,parent):
        frame = Frame(parent,)
        frame.place(x=10, y=225, width=315, height=35)
        return frame
    def __tk_label_hekili(self,parent):
        label = Label(parent,text="Hekili区域：",anchor="w", )
        label.place(x=0, y=2, width=80, height=30)
        return label
    def __tk_label_hekili_x(self,parent):
        label = Label(parent,text="X",anchor="w", )
        label.place(x=70, y=2, width=20, height=30)
        return label
    def __tk_input_hekili_x(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=88, y=2, width=40, height=30)
        return ipt
    def __tk_label_hekili_y(self,parent):
        label = Label(parent,text="Y",anchor="w", )
        label.place(x=130, y=2, width=20, height=30)
        return label
    def __tk_input_hekili_y(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=148, y=2, width=40, height=30)
        return ipt
    def __tk_label_hekili_w(self,parent):
        label = Label(parent,text="W",anchor="w", )
        label.place(x=190, y=2, width=20, height=30)
        return label
    def __tk_input_hekili_w(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=208, y=2, width=40, height=30)
        return ipt
    def __tk_label_hekili_h(self,parent):
        label = Label(parent,text="H",anchor="w", )
        label.place(x=250, y=2, width=20, height=30)
        return label
    def __tk_input_hekili_h(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=268, y=2, width=40, height=30)
        return ipt
    def __tk_frame_ability_key_zone(self,parent):
        frame = Frame(parent,)
        frame.place(x=10, y=275, width=315, height=35)
        return frame
    def __tk_label_ability_key(self,parent):
        label = Label(parent,text="按键区域：",anchor="w", )
        label.place(x=0, y=2, width=80, height=30)
        return label
    def __tk_label_ability_key_x(self,parent):
        label = Label(parent,text="X",anchor="w", )
        label.place(x=70, y=2, width=30, height=30)
        return label
    def __tk_input_ability_key_x(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=88, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_key_y(self,parent):
        label = Label(parent,text="Y",anchor="w", )
        label.place(x=130, y=2, width=30, height=30)
        return label
    def __tk_input_ability_key_y(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=148, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_key_w(self,parent):
        label = Label(parent,text="W",anchor="w", )
        label.place(x=190, y=2, width=30, height=30)
        return label
    def __tk_input_ability_key_w(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=208, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_key_h(self,parent):
        label = Label(parent,text="H",anchor="w", )
        label.place(x=250, y=2, width=30, height=30)
        return label
    def __tk_input_ability_key_h(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=268, y=2, width=40, height=30)
        return ipt
    def __tk_frame_ability_cooldown_zone(self,parent):
        frame = Frame(parent,)
        frame.place(x=10, y=325, width=315, height=35)
        return frame
    def __tk_label_ability_cooldown(self,parent):
        label = Label(parent,text="冷却区域：",anchor="w", )
        label.place(x=0, y=2, width=80, height=30)
        return label
    def __tk_label_ability_cooldown_x(self,parent):
        label = Label(parent,text="X",anchor="w", )
        label.place(x=70, y=2, width=30, height=30)
        return label
    def __tk_input_ability_cooldown_x(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=88, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_cooldown_y(self,parent):
        label = Label(parent,text="Y",anchor="w", )
        label.place(x=130, y=2, width=30, height=30)
        return label
    def __tk_input_ability_cooldown_y(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=148, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_cooldown_w(self,parent):
        label = Label(parent,text="W",anchor="w", )
        label.place(x=190, y=2, width=30, height=30)
        return label
    def __tk_input_ability_cooldown_w(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=208, y=2, width=40, height=30)
        return ipt
    def __tk_label_ability_cooldown_h(self,parent):
        label = Label(parent,text="H",anchor="w", )
        label.place(x=250, y=2, width=30, height=30)
        return label
    def __tk_input_ability_cooldown_h(self,parent):
        ipt = Entry(parent, )
        ipt.place(x=268, y=2, width=40, height=30)
        return ipt
class Win(WinGUI):
    def __init__(self, controller):
        self.ctl = controller
        super().__init__()
        self.__event_bind()
        self.__style_config()
        self.ctl.init(self)
    def __event_bind(self):
        self.tk_button_set_hekili_zone.bind('<Button-1>',self.ctl.set_hekili_zone)
        self.tk_button_start.bind('<Button-1>',self.ctl.start_rotation)
        pass
    def __style_config(self):
        pass
if __name__ == "__main__":
    win = WinGUI()
    win.mainloop()