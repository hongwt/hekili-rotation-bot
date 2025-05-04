import sys
import datetime
import time
import os
import win32gui
import win32process
import psutil
import ctypes
from PySide6 import QtWidgets, QtCore, QtGui
import subprocess
from PySide6.QtCore import QSharedMemory
import win32api

def is_admin():
    """
    检查当前用户是否拥有管理员权限
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin(argv=None):
    """
    重新启动程序并请求管理员权限
    """
    shell32 = ctypes.windll.shell32
    if argv is None and sys.argv:
        argv = sys.argv
    if not argv:
        argv = ['']
    executable = sys.executable
    params = ' '.join([f'"{arg}"' for arg in argv])
    show_cmd = 1  # SW_NORMAL
    lpVerb = 'runas'
    try:
        ret = shell32.ShellExecuteW(None, lpVerb, executable, params, None, show_cmd)
        if ret <= 32:
            return False
        return True
    except:
        return False

def restart_program():
    """
    重启当前程序，保持管理员权限
    """
    try:
        if is_admin():
            # 获取当前执行的可执行文件路径pip install PySide6
            if hasattr(sys, 'frozen'):
                executable = sys.executable
            else:
                executable = sys.argv[0]
            # 使用 subprocess 重新启动程序
            subprocess.Popen([executable] + sys.argv[1:], shell=True)
            sys.exit(0)
        else:
            # 以管理员身份重新启动程序
            if run_as_admin(sys.argv):
                sys.exit(0)
            else:
                QtWidgets.QMessageBox.warning(None, "管理员权限", "需要管理员权限才能运行此程序。")
                sys.exit()
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "重启错误", f"无法重启程序: {e}")
        sys.exit(1)

def get_current_time():
    """
    获取当前本地时间，包含时区信息
    """
    return datetime.datetime.now(datetime.timezone.utc).astimezone()

def get_active_process_info(window):
    """
    获取当前活动窗口的进程名称和窗口标题，排除程序自身和系统窗口
    """
    try:
        hwnd = win32gui.GetForegroundWindow()
        # 获取窗口类名和窗口标题
        class_name = win32gui.GetClassName(hwnd)
        window_text = win32gui.GetWindowText(hwnd)

        # 获取当前程序的窗口句柄和进程 ID
        current_hwnd = int(window.winId())  # PySide6 中获取窗口句柄
        current_pid = os.getpid()

        # 获取活动窗口的进程 ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        # 检查是否为程序自身的窗口
        if hwnd == current_hwnd or pid == current_pid:
            return None, None

        # 检查是否为系统窗口
        system_classes = [
            "Shell_TrayWnd", "TrayNotifyWnd", "NotifyIconOverflowWindow",
            "SysListView32", "WorkerW", "Progman", "Button",
            "Windows.UI.Core.CoreWindow", "MultitaskingViewFrame", "TaskSwitcherWnd"
        ]
        if class_name in system_classes:
            return None, None

        # 获取进程名称
        process = psutil.Process(pid)
        process_name = process.name()

        # 排除特定的系统进程
        system_processes = ["explorer.exe", "searchui.exe", "startmenuexperiencehost.exe"]
        if process_name.lower() in system_processes:
            return None, None

        return process_name, window_text
    except Exception as e:
        print(f"Error getting active process info: {e}")
        return None, None

def format_timedelta(td):
    """
    将时间差格式化为小时:分钟:秒
    """
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

class Reminder:
    def __init__(self, reminder_type, duration, start_time):
        self.reminder_type = reminder_type  # 'app_time', 'countdown'
        self.duration = duration  # timedelta
        self.start_time = start_time  # 传入的开始时间
        self.target_time = self.start_time + self.duration

class ProgressBarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, filled_color="#64C864", background_color="#C8C8C8"):
        super().__init__(parent)
        self.progress = 0  # 进度百分比，0 到 100
        self.setMinimumWidth(10)  # 设置最小宽度
        self.setMinimumHeight(30)  # 设置最小高度
        self.filled_color = filled_color
        self.background_color = background_color

    def set_progress(self, progress):
        self.progress = progress
        self.update()  # 触发重绘

    def set_filled_color(self, color):
        self.filled_color = color
        self.update()

    def set_background_color(self, color):
        self.background_color = color
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # 开启反锯齿
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # 绘制背景矩形
        rect = self.rect()
        painter.setBrush(QtGui.QColor(self.background_color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, 5, 5)
        # 计算已填充部分
        filled_width = rect.width() * self.progress / 100
        filled_rect = QtCore.QRectF(
            rect.x(),
            rect.y(),
            filled_width,
            rect.height()
        )
        # 绘制已填充部分
        painter.setBrush(QtGui.QColor(self.filled_color))
        painter.drawRoundedRect(filled_rect, 5, 5)

class ReminderDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.reminder_type = None
        self.duration = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("设置提醒")
        layout = QtWidgets.QVBoxLayout()

        # 提醒类型选择（使用单选按钮）
        type_layout = QtWidgets.QHBoxLayout()
        type_label = QtWidgets.QLabel("提醒类型:")
        self.app_time_radio = QtWidgets.QRadioButton("游戏时间")
        self.countdown_radio = QtWidgets.QRadioButton("倒计时")
        self.app_time_radio.setChecked(True)  # 默认选中游戏时间
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.app_time_radio)
        type_layout.addWidget(self.countdown_radio)
        layout.addLayout(type_layout)

        # 时间输入
        duration_layout = QtWidgets.QHBoxLayout()
        duration_label = QtWidgets.QLabel("时间 (分钟):")
        self.duration_edit = QtWidgets.QLineEdit()
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_edit)
        layout.addLayout(duration_layout)

        # 按钮
        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        try:
            duration_value = int(self.duration_edit.text())
            if duration_value <= 0:
                raise ValueError("时间必须是正数")
            self.duration = duration_value * 60  # 将分钟转换为秒
            if self.app_time_radio.isChecked():
                self.reminder_type = "app_time"
            elif self.countdown_radio.isChecked():
                self.reminder_type = "countdown"
            super().accept()
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "输入错误", "请输入有效的正数时间（分钟）")

class TransparentWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.recent_apps = {}  # 存储最近切换的应用程序
        self.reminders = []  # 存储提醒对象
        self.is_fullscreen = False  # 是否处于全屏状态
        self.is_window_shown = True  # 窗口是否显示
        self.previous_position = None  # 记录窗口之前的位置
        self.initUI()
        # 初始化 last_process_name 和 last_process_start_time
        self.last_process_info = get_active_process_info(self)
        self.last_process_name = self.last_process_info[0]
        self.last_window_title = self.last_process_info[1]
        self.last_process_start_time = get_current_time()
        # 启动定时器更新界面
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(500)  # 每 500 毫秒更新一次

        # 启动置顶定时器，每 50 毫秒置顶一次
        self.raise_timer = QtCore.QTimer()
        self.raise_timer.timeout.connect(self.keep_on_top)
        self.raise_timer.start(50)  # 每 50 毫秒置顶一次

        # 启动全屏检测定时器
        self.fullscreen_timer = QtCore.QTimer()
        self.fullscreen_timer.timeout.connect(self.check_fullscreen)
        self.fullscreen_timer.start(100)  # 每100ms检查一次

    def paintEvent(self, event):
        """
        重写 paintEvent 以绘制一个几乎完全透明的背景，
        这样窗口的所有区域都能拦截鼠标事件。
        """
        painter = QtGui.QPainter(self)
        # 设置组合模式为 Source，确保绘制的颜色覆盖所有像素
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
        # 绘制一个几乎透明的背景（Alpha 值为1）
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 1))

    def initUI(self):
        try:
            # 设置窗口无边框、置顶、工具窗口和背景透明
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            # 使窗口可拖动
            self.offset = None

            # 创建标签
            self.app_name_label = QtWidgets.QLabel("", self)
            self.app_time_label = QtWidgets.QLabel("", self)

            # 设置标签样式（字体颜色和大小）
            label_style = f"color: '#000000'; font-size: 16px;"
            self.app_name_label.setStyleSheet(label_style)
            self.app_time_label.setStyleSheet(label_style)

            # 设置标签不拦截鼠标事件
            self.app_name_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self.app_time_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

            # 设置标签的最小高度，确保在窗口高度降低时能够正常显示
            self.app_name_label.setMinimumHeight(10)
            self.app_time_label.setMinimumHeight(10)

            # 创建进度条小部件
            self.progress_bar = ProgressBarWidget(
                self,
                filled_color='#64C864',
                background_color='#C8C8C8'
            )
            progress_bar_width = 135
            self.progress_bar.setFixedSize(progress_bar_width, 10)  # 调整尺寸

            # 布局设置
            self.layout = QtWidgets.QHBoxLayout()
            self.layout.setSpacing(2)
            self.layout.setContentsMargins(0, 0, 0, 0)

            # 动态调整进度条位置
            self.update_layout()

            self.setLayout(self.layout)

            # 设置窗口大小和位置
            self.update_window_geometry()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "初始化错误", f"初始化界面时发生错误: {e}")
            
    def show_about_dialog(self):
        """
        显示关于对话框，包含作者名称和 GitHub 地址
        """
        try:
            # 创建一个对话框
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("关于")
            dialog.setFixedSize(300, 150)

            layout = QtWidgets.QVBoxLayout()

            # 添加作者名称
            author_label = QtWidgets.QLabel("作者：洪运宁")
            author_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(author_label)

            # 添加参考信息
            reference_label = QtWidgets.QLabel("本程序参考ShowTime，感谢liaanj！")
            reference_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(reference_label)

            # 添加关闭按钮
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "关于对话框错误", f"无法显示关于对话框: {e}")

    def check_fullscreen(self):
        """
        检查当前前台窗口是否全屏，并更新状态
        """
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            self_hwnd = self.effectiveWinId().__int__()
            if hwnd == self_hwnd:
                # 前台窗口是自身，忽略，不改变 is_fullscreen 状态
                return
            else:
                # 获取前台窗口所在屏幕
                monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromWindow(hwnd))
                monitor_area = monitor_info['Monitor']
                work_area = monitor_info['Work']
                # 获取前台窗口大小
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                screen_width = monitor_area[2] - monitor_area[0]
                screen_height = monitor_area[3] - monitor_area[1]
                new_fullscreen_state = (width >= screen_width and height >= screen_height)
                # 排除桌面窗口
                window_class = win32gui.GetClassName(hwnd)
                desktop_classes = ["Progman", "WorkerW"]
                if window_class in desktop_classes:
                    new_fullscreen_state = False
                if new_fullscreen_state != self.is_fullscreen:
                    self.is_fullscreen = new_fullscreen_state
                    if self.is_fullscreen:
                        print("进入全屏模式")
                        self.on_enter_fullscreen()
                    else:
                        print("退出全屏模式")
                        self.on_exit_fullscreen()
        else:
            # 无前台窗口，可能性较小，忽略
            pass


    def on_enter_fullscreen(self):
        # 移动到记录的全屏位置
        pos = None
        if pos is not None:
            self.move(pos['x'], pos['y'])
        # 移除贴边隐藏相关逻辑

    def on_exit_fullscreen(self):
        # 移动到记录的非全屏位置
        pos = None
        if pos is not None:
            self.move(pos['x'], pos['y'])
        # 如果窗口被隐藏，确保它显示出来
        self.show()

    def update_layout(self):
        try:
            # 清除现有布局
            while self.layout.count():
                item = self.layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

            # 更新标签样式
            label_style = f"color: '#000000'; font-size: 16px;"
            self.app_name_label.setStyleSheet(label_style)
            self.app_time_label.setStyleSheet(label_style)

            # 根据配置添加控件
            main_layout = QtWidgets.QVBoxLayout()
            main_layout.addWidget(self.progress_bar)

            text_layout = QtWidgets.QVBoxLayout()
            text_layout.addWidget(self.app_name_label)
            text_layout.addWidget(self.app_time_label)
            text_layout.setSpacing(0)
            text_layout.setContentsMargins(0, 0, 0, 0)

            main_layout.addLayout(text_layout)

            self.layout.addLayout(main_layout)

            # 更新布局间距
            self.layout.setSpacing(2)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "布局更新错误", f"更新布局时发生错误: {e}")

    def update_window_geometry(self):
        try:
            window_width = 200
            window_height = 60
            x = None
            y = None

            # 更新窗口尺寸
            self.resize(window_width, window_height)

            if x is not None and y is not None:
                self.move(x, y)
            else:
                screen_rect = QtWidgets.QApplication.primaryScreen().availableGeometry()
                taskbar_height = 40  # 假设任务栏高度为 40px
                offset_from_right = 100  # 从屏幕右侧向左偏移 100 像素
                self.move(screen_rect.width() - window_width - offset_from_right,
                          screen_rect.height() - taskbar_height - window_height)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "窗口几何错误", f"更新窗口几何时发生错误: {e}")

    def mousePressEvent(self, event):
        """
        记录鼠标按下的位置
        """
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.offset = event.position().toPoint()
        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            self.contextMenuEvent(event)
        # if event.button() == QtCore.Qt.RightButton:
        #     self.contextMenuEvent(event)
        # super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        拖动窗口
        """
        if self.offset is not None and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)

    def mouseReleaseEvent(self, event):
        """
        释放鼠标时清除偏移
        """
        self.offset = None

    def moveEvent(self, event):
        """
        当窗口移动时，更新配置中的窗口位置
        """
        super().moveEvent(event)
    
    def contextMenuEvent(self, event):
        """
        右键菜单
        """
        try:
            menu = QtWidgets.QMenu(self)
            reset_time_action = menu.addAction("清除时间")
            set_reminder_action = menu.addAction("设置提醒")
            exit_action = menu.addAction("退出应用")
            about_action = menu.addAction("关于")
            
            # 计算菜单位置，避免被遮挡
            screen_rect = QtWidgets.QApplication.primaryScreen().availableGeometry()
            menu_x = event.globalPos().x()
            menu_y = event.globalPos().y()
            menu_height = menu.sizeHint().height()
            if menu_y + menu_height > screen_rect.height():
                menu_y = screen_rect.height() - menu_height

            action = menu.exec(QtCore.QPoint(menu_x, menu_y))
            if action == reset_time_action:
                self.reset_time()
            elif action == set_reminder_action:
                self.set_reminder()
            elif action == about_action:  
                self.show_about_dialog()
            elif action == exit_action:
                self.close()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "右键菜单错误", f"打开右键菜单时发生错误: {e}")

    def reset_time(self):
        """
        清除时间
        """
        try:
            # 重置游戏时间
            self.last_process_start_time = get_current_time()
            self.last_process_info = get_active_process_info(self)
            self.last_process_name = self.last_process_info[0]
            self.last_window_title = self.last_process_info[1]
            # 清空提醒
            self.reminders.clear()
            self.progress_bar.set_progress(0)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "重置时间错误", f"重置时间时发生错误: {e}")

    def set_reminder(self):
        try:
            dialog = ReminderDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                reminder_type_map = {
                    "app_time": "app_time",
                    "countdown": "countdown"
                }
                reminder_type = reminder_type_map.get(dialog.reminder_type)
                duration = datetime.timedelta(seconds=dialog.duration)
                # 获取当前已用时间
                current_time = get_current_time()

                if reminder_type == 'app_time':
                    if self.last_process_start_time:
                        elapsed_time = current_time - self.last_process_start_time
                        if duration <= elapsed_time:
                            QtWidgets.QMessageBox.warning(self, "输入错误", "提醒时间必须大于当前已用的游戏时间")
                            return
                        start_time = self.last_process_start_time
                    else:
                        QtWidgets.QMessageBox.warning(self, "设置错误", "无法获取游戏时间")
                        return

                elif reminder_type == 'countdown':
                    start_time = current_time

                # 创建提醒对象
                reminder = Reminder(reminder_type, duration, start_time)
                self.reminders.append(reminder)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "设置提醒错误", f"设置提醒时发生错误: {e}")

    def show_notification(self, reminder):
        """
        显示提醒通知
        """
        try:
            message_map = {
                'app_time': '游戏时间',
                'countdown': '倒计时'
            }
            message = f"您的{message_map.get(reminder.reminder_type, '未知类型')}已达到设定时间！"
            QtWidgets.QMessageBox.information(self, "提醒", message)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "通知错误", f"显示通知时发生错误: {e}")

    def update_time(self):
        try:
            # 获取当前本地时间，包含时区信息
            current_time = get_current_time()

            # 更新当前应用使用时间
            current_process_info = get_active_process_info(self)
            current_process_name = current_process_info[0]
            current_window_title = current_process_info[1]

            if current_process_name and current_process_name != self.last_process_name:
                # 活动应用程序发生变化
                switch_away_time = current_time  # 记录离开时间

                # 计算在上一个应用程序上花费的时间
                app_time = current_time - self.last_process_start_time

                # 将上一个应用程序的信息存储到 recent_apps
                self.recent_apps[self.last_process_name] = {
                    'last_start_time': self.last_process_start_time,
                    'accumulated_time': app_time,
                    'switch_away_time': switch_away_time
                }

                # 移除离开时间超过一分钟的应用程序
                to_remove = []
                for app_name, data in self.recent_apps.items():
                    time_since_switch = (current_time - data['switch_away_time']).total_seconds()
                    if time_since_switch > 60:
                        to_remove.append(app_name)
                for app_name in to_remove:
                    del self.recent_apps[app_name]

                # 检查当前应用程序是否在 recent_apps 中（即是否在一分钟内返回）
                if current_process_name in self.recent_apps:
                    # 恢复之前的应用程序计时
                    prev_data = self.recent_apps[current_process_name]
                    self.last_process_start_time = prev_data['last_start_time']
                    # 调整开始时间，补偿离开的时间
                    time_away = current_time - prev_data['switch_away_time']
                    self.last_process_start_time += time_away
                    # 从 recent_apps 中移除该应用程序
                    del self.recent_apps[current_process_name]
                else:
                    # 超过一分钟，重置计时
                    self.last_process_start_time = current_time

                self.last_process_name = current_process_name

            elif current_process_name is None:
                # 活动窗口为系统窗口或自身窗口，不做处理
                pass
            else:
                # 活动游戏程序未发生变化，继续计时
                pass

            if self.last_process_name:
                app_uptime = current_time - self.last_process_start_time
                self.app_name_label.setText(f"游戏名称: {current_window_title}")
                self.app_time_label.setText(f"游戏时间: {format_timedelta(app_uptime)}")
            else:
                self.app_name_label.setText("游戏名称: N/A")
                self.app_time_label.setText("游戏时间: N/A")

            # 检查提醒
            if self.reminders:
                # 更新依赖于游戏时间的提醒
                for reminder in self.reminders[:]:
                    if reminder.reminder_type == 'app_time':
                        if self.last_process_start_time and self.last_process_start_time > reminder.start_time:
                            reminder.start_time = self.last_process_start_time
                            reminder.target_time = reminder.start_time + reminder.duration

                    time_remaining = (reminder.target_time - current_time).total_seconds()
                    total_duration = (reminder.target_time - reminder.start_time).total_seconds()
                    if total_duration > 0:
                        progress = max(0, min(100, (1 - time_remaining / total_duration) * 100))
                    else:
                        progress = 100
                    self.progress_bar.set_progress(progress)

                    # 检查是否有提醒到达
                    if reminder.target_time <= current_time:
                        # 提醒到达
                        self.show_notification(reminder)
                        # 删除已完成的提醒
                        self.reminders.remove(reminder)
            else:
                # 没有提醒，重置进度条
                self.progress_bar.set_progress(0)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "更新时间错误", f"更新时间时发生错误: {e}")

    def keep_on_top(self):
        """
        将窗口置顶
        """
        try:
            self.raise_()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "置顶错误", f"保持置顶时发生错误: {e}")

    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        try:
            # 停止所有定时器
            self.timer.stop()
            self.raise_timer.stop()
            self.fullscreen_timer.stop()
            # self.mouse_timer.stop()
            # 释放共享内存
            shared_memory.detach()
            event.accept()
            QtWidgets.QApplication.quit()  # 确保应用程序退出
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "关闭错误", f"关闭窗口时发生错误: {e}")
            event.ignore()

def main():
    global shared_memory
    # 防止重复启动
    shared_memory = QSharedMemory("MyTransparentAppUniqueKey")
    if not shared_memory.create(1):
        # 共享内存已存在，说明已有实例在运行
        app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QMessageBox.warning(None, "程序已在运行", "程序已经在运行。")
        sys.exit()

    try:
        if not is_admin():
            if run_as_admin(sys.argv):
                sys.exit()
            else:
                QtWidgets.QMessageBox.warning(None, "管理员权限", "需要管理员权限才能运行此程序。")
                sys.exit()

        app = QtWidgets.QApplication(sys.argv)
        window = TransparentWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "程序错误", f"程序发生未处理的错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()