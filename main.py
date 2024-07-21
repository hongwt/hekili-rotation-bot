import cv2 as cv
import numpy as np
from PIL import Image

import os

import time

import config

from windowcapture import WindowCapture
from recognition import Recognition
from bot import WowBot

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the WindowCapture class
wincap = WindowCapture(config.WOW_WINDOW_NAME)
# load the recognition
recog = Recognition()
# initialize the bot
bot = WowBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

wincap.start()

loop_time = time.time()

while(True):
    if wincap.screenshot is None:
        continue
    
    screenshot_np = np.array(wincap.screenshot)
    
    # 技能按键区域
    ability_key_image = screenshot_np[config.ABILITY_KEY_Y:config.ABILITY_KEY_Y+config.ABILITY_KEY_H,
                                       config.ABILITY_KEY_X:config.ABILITY_KEY_X+config.ABILITY_KEY_W]
    if ability_key_image.size == 0:
        print("技能按键区域图像为空，可能是配置的区域超出了原图的范围。")
        continue
    key_text = recog.convertToText(ability_key_image)
    if config.DEBUG:
        cv.imwrite('images/Key_{}_{}.jpg'.format(key_text, loop_time), ability_key_image)
        
    if key_text and len(key_text) == 1:
        # 技能冷却时间区域
        ability_cooldown_image = screenshot_np[config.ABILITY_COOLDOWN_Y:config.ABILITY_COOLDOWN_Y+config.ABILITY_COOLDOWN_H,
                                           config.ABILITY_COOLDOWN_X:config.ABILITY_COOLDOWN_X+config.ABILITY_COOLDOWN_W]
        if ability_cooldown_image.size == 0:
            print("技能冷却时间区域图像为空，可能是配置的区域超出了原图的范围。")
            continue
        cooldown_text = recog.convertToText(ability_cooldown_image)
        if config.DEBUG:
            cv.imwrite('images/Cooldown_{}_{}.jpg'.format(cooldown_text, loop_time), ability_cooldown_image)

        if cooldown_text and cooldown_text.isdigit() and int(cooldown_text) > 0 and int(cooldown_text) < 10:
            continue

        key = key_text[0] 
        if key and (key >= '1' and key <= 'Z'):
            bot.press_ability_key(key)

    if config.DEBUG:
        print(f'FPS {1 / (time.time() - loop_time)}')
    loop_time = time.time()

    print('Done.')
