import cv2 as cv
import time

import config
from recognition import Recognition

class Vision:

    # properties
    recog = Recognition()

    def __init__(self):
        self.recog = Recognition()

    def get_ability_key(self, screenshot_np):
        # 技能按键区域
        ability_key_image = screenshot_np[config.ABILITY_KEY_Y:config.ABILITY_KEY_Y+config.ABILITY_KEY_H,
                                        config.ABILITY_KEY_X:config.ABILITY_KEY_X+config.ABILITY_KEY_W]
        if ability_key_image.size == 0:
            print("技能按键区域图像为空，可能是配置的区域超出了原图的范围。")
            return ''
        key_text = self.recog.convertToText(ability_key_image)
        if config.DEBUG:
            cv.imwrite('images/Key_{}_{}.jpg'.format(key_text, time.time()), ability_key_image)
        
        if key_text is None or len(key_text) != 1:
            return ''
        key = key_text[0]
        # 正确识别技能快捷键
        if key and (key >= '1' and key <= 'Z'):
            return key
        else:
            return ''


    def get_ability_cooldown(self, screenshot_np):
        # 技能冷却时间区域
        ability_cooldown_image = screenshot_np[config.ABILITY_COOLDOWN_Y:config.ABILITY_COOLDOWN_Y+config.ABILITY_COOLDOWN_H,
                                           config.ABILITY_COOLDOWN_X:config.ABILITY_COOLDOWN_X+config.ABILITY_COOLDOWN_W]
        if ability_cooldown_image.size == 0:
            print("技能冷却时间区域图像为空，可能是配置的区域超出了原图的范围。")
            return
        cooldown_text = self.recog.convertToText(ability_cooldown_image)
        if config.DEBUG:
            cv.imwrite('images/Cooldown_{}_{}.jpg'.format(cooldown_text, time.time()), ability_cooldown_image)

        if cooldown_text and cooldown_text.isdigit() and int(cooldown_text) > 0 and int(cooldown_text) < 10:
            return int(cooldown_text)
        else:
            return -1
