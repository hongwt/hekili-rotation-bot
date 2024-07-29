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

    def press_ability_key(self, key, cooldown):
        # delay = random.uniform(0.1, 0.2)
        # if (cooldown > 0):
        #     delay = random.uniform(0.2, 0.5)
        # time.sleep(delay)
        key = key.lower()  # Convert key to lowercase
        print(f'Casting ability {key} with cooldown {cooldown} seconds.')
        pyautogui.press(key)


    def run(self):
        while not self.stopped:
            screenshot = ImageGrab.grab(bbox=(config.HEKILI_X, 
                                            config.HEKILI_Y, 
                                            config.HEKILI_X + config.HEKILI_W, 
                                            config.HEKILI_Y + config.HEKILI_H))
            if screenshot is None:
                continue

            screenshot_np = np.array(screenshot)
            loop_time = time.time()
            key = self.vision.get_ability_key(screenshot_np)
            print(f'vision FPS {1 / (time.time() - loop_time)}')
            if (key and key != ''):
                self.press_ability_key(key, 0)

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True