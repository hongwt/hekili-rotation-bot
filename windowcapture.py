import numpy as np
import win32gui, win32ui, win32con
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
import ctypes

from threading import Thread, Lock


class WindowCapture:

    # threading properties
    stopped = True
    lock = None
    screenshot = None
    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, window_name=None):
        # create a thread lock object
        self.lock = Lock()

        # find the handle for the window we want to capture.
        # if no window name is given, capture the entire screen
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception('Window not found: {}'.format(window_name))

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        border_pixels = 0
        titlebar_pixels = 25
        self.w = self.w - (border_pixels * 2)
        self.h = self.h - titlebar_pixels - border_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    def get_screenshot(self):

        # get the window image data
        # 魔兽世界有句柄保护，所以使用hwnd编码是无法进行句柄截图
        # wDC = win32gui.GetWindowDC(self.hwnd)
        wDC = win32gui.GetWindowDC(0)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel, or cv.matchTemplate() will throw an error like:
        #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type() 
        #   && _img.dims() <= 2 in function 'cv::matchTemplate'
        img = img[...,:3]

        # make image C_CONTIGUOUS to avoid errors that look like:
        #   File ... in draw_rectangles
        #   TypeError: an integer is required (got type tuple)
        # see the discussion here:
        # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
        img = np.ascontiguousarray(img)

        return img

    # find the name of the window you're interested in.
    # once you have it, update window_capture()
    # https://stackoverflow.com/questions/55547940/how-to-get-a-list-of-the-name-of-every-open-window
    @staticmethod
    def list_window_names():
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                print(hex(hwnd), win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(winEnumHandler, None)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.offset_x, pos[1] + self.offset_y)

    # threading methods

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            # get an updated image of the game
            screenshot = self.get_screenshot()
            # lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()


# 获取屏幕的缩放比
def get_screen_scaling():
    return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
 
class ScreenshotWidget(QWidget):

    # properties
    x1, y1, x2, y2 = 0, 0, 0, 0

    def __init__(self):
        super().__init__()
        self.begin = None
        self.end = None
        # Qt.WindowStaysOnTopHint 置顶窗口
        # Qt.FramelessWindowHint 产生一个无窗口边框的窗口，此时用户无法移动该窗口和改变它的大小
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # setWindowOpacity() 只能作用于顶级窗口，取值为0.0~1.0，0.0为完全透明，1.0为完全不透明
        self.setWindowOpacity(0.5)  # 设置窗口透明度为 0.5，如果不加这行代码的话，运行代码后屏幕会被不透明白屏铺满
        self.setWindowState(Qt.WindowFullScreen)  # 铺满全屏幕
        self.screen_scaling = get_screen_scaling()
 
    def mousePressEvent(self, event):
        self.begin = event.pos() 
        self.end = event.pos()
 
    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()
 
    # 根据坐标进行截图保存
    def mouseReleaseEvent(self, event):
        self.close()
        # 坐标乘以缩放比后再进行抓取
        self.x1, self.y1 = self.begin.x() * self.screen_scaling, self.begin.y() * self.screen_scaling
        self.x2, self.y2 = self.end.x() * self.screen_scaling, self.end.y() * self.screen_scaling
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
        
 
    # 在截图时绘制矩形，目的是为了清楚看到自己所选的区域
    def paintEvent(self, event):
        if not self.begin:
            return
        painter = QPainter(self)  # 创建QPainter对象
        # painter.setPen(Qt.green)
        # painter.setPen(Qt.red) #设置画笔的颜色
        pen = QPen(Qt.red)
        pen.setWidth(2)  # 设置画笔的宽度
        painter.setPen(pen)
 
        # drawRect来绘制矩形，四个参数分别是x,y,w,h
        painter.drawRect(self.begin.x(), self.begin.y(),
                         self.end.x() - self.begin.x(), self.end.y() - self.begin.y())
        
def main():
    app = QApplication([])
    widget = ScreenshotWidget()
    widget.show()
# app.exec_()是PyQt中的一个方法，用于启动应用程序的事件循环。它会在调用之后开始监视事件，并根据事件的发生自动执行相应的函数。
    app.exec_()
 
 
if __name__ == '__main__':
    main()