import time
import random
import pyautogui

import numpy as np

from PIL import ImageGrab

from threading import Thread, Lock

from vision import Vision

import config

class WowBot:

    # threading properties
    stopped = True
    lock = None

    vision = None

    def __init__(self):
        # create a thread lock object
        self.lock = Lock()
        self.vision = Vision()

    def convert_to_key(self, key_text):
        if not key_text:
            return ''
        # drop all keys that are not in the valid keys list
        key_text = [key for key in key_text if (key >= '0' and key <= 'z')]
        key_text = ''.join(key_text)
        # add some special cases
        if ("11" == key_text):
            return '1'
        if len(key_text) == 1:
            return key_text[0]
        else:
            return ''
        
    def press_ability_key(self, key, cooldown):
        # delay = random.uniform(0.1, 0.2)
        # if (cooldown > 0):
        #     delay = random.uniform(0.2, 0.5)
        # time.sleep(delay)
        key = key.lower()  # Convert key to lowercase
        print(f'Casting ability {key} with cooldown {cooldown} seconds.')
        pyautogui.press(key)


    # 创建一个函数，将所有非黑色像素转换为白色
    def to_white_or_black(self, value):
        threshold = 1
        if value < threshold:
            return 0  # 返回黑色
        else:
            return 255  # 返回白色
    
    def run(self):
        while not self.stopped:
            screenshot = ImageGrab.grab(bbox=(config.HEKILI_X, 
                                            config.HEKILI_Y, 
                                            config.HEKILI_X + config.HEKILI_W, 
                                            config.HEKILI_Y + config.HEKILI_H))
            if screenshot is None:
                continue

            screenshot = screenshot.convert('L')
            # 使用point方法应用这个函数
            screenshot = screenshot.point(self.to_white_or_black)
            
            screenshot_np = np.array(screenshot)
            loop_time = time.time()
            key_text = self.vision.get_ability_key(screenshot_np)
            print(f'vision FPS {1 / (time.time() - loop_time)}')
            key = self.convert_to_key(key_text)
            if (key and key != ''):
                if key in config.VALID_KEYS:
                    self.press_ability_key(key, 0)
                else:
                    screenshot.save(f'images/invalid_{key}_{time.time()}.png')
            delay = random.uniform(0.05, 0.15)
            time.sleep(delay)

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True