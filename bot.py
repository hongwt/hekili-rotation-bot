
import time
import random
import pyautogui

import numpy as np

from threading import Thread, Lock

class WowBot:

    # threading properties
    stopped = True
    lock = None

    capture = None
    vision = None

    def __init__(self, capture, vision):
        # create a thread lock object
        self.lock = Lock()
        
        self.capture = capture
        self.vision = vision

    def press_ability_key(self, key, cooldown):
        print(f'Pressing key: {key}')
        
        delay = random.uniform(0.1, 0.2)
        if (cooldown > 0):
            delay = random.uniform(0.2, 0.5)
        
        time.sleep(delay)
        
        pyautogui.press(key)

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            if self.capture.screenshot is None:
                continue
            screenshot_np = np.array(self.capture.screenshot)
            ability_key = self.vision.get_ability_key(screenshot_np)
            if (ability_key and ability_key != ''):
                ability_cooldown = self.vision.get_ability_cooldown(screenshot_np)
                if (ability_cooldown > 1):
                    print(f'Ability {ability_key} is on cooldown for {ability_cooldown} seconds.')
                else:
                    print(f'Pressing ability {ability_key}.')
                    self.bot.press_ability_key(ability_key, ability_cooldown)