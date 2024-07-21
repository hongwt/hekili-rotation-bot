import pyautogui
import random
import time

class WowBot:
    # properties
    window_offset = (0,0)
    window_w = 0
    window_h = 0

    def __init__(self, window_offset, window_size):
        # for translating window positions into screen positions, it's easier to just
        # get the offsets and window size from WindowCapture rather than passing in 
        # the whole object
        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

    def press_ability_key(self, key):
        print(f'Pressing key: {key}')
        
        delay = random.uniform(0.1, 0.2)
        time.sleep(delay)
        
        pyautogui.press(key)

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the WindowCapture __init__ constructor.
    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])