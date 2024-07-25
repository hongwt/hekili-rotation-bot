import os
import time
import numpy as np

import config
# 导入布局文件
import ui
# from windowcapture import WindowCapture
# from vision import Vision
# from bot import WowBot

# Change the working directory to the folder this script is in.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# initialize the WindowCapture class
# wincap = WindowCapture(config.WOW_WINDOW_NAME)
# # load the vision
# vision = Vision()
# # initialize the bot
# bot = WowBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

# wincap.start()

# 将窗口控制器 传递给UI

# loop_time = time.time()

# while(True):
#     if wincap.screenshot is None:
#         continue
    
#     screenshot_np = np.array(wincap.screenshot)
    
#     # Inside the while loop
#     ability_key = vision.get_ability_key(screenshot_np)
#     if (ability_key and ability_key != ''):
#         ability_cooldown = vision.get_ability_cooldown(screenshot_np)
#         if (ability_cooldown > 0):
#             print(f'Ability {ability_key} is on cooldown for {ability_cooldown} seconds.')
#         else:
#             print(f'Pressing ability {ability_key}.')
#             bot.press_ability_key(ability_key)

#     if config.DEBUG:
#         print(f'FPS {1 / (time.time() - loop_time)}')
#     loop_time = time.time()

# print('Done.')

if __name__ == "__main__":
    # 启动
    ui.main()