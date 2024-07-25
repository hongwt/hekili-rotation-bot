import pyautogui
import random
import time

class WowBot:

    def __init__(self):
        pass

    def press_ability_key(self, key, cooldown):
        print(f'Pressing key: {key}')
        
        delay = random.uniform(0.1, 0.2)
        if (cooldown > 0):
            delay = random.uniform(0.2, 0.5)
        
        time.sleep(delay)
        
        pyautogui.press(key)
