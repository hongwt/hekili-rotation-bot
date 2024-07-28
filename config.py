import os
import sys

import configparser

# 创建配置对象
config = configparser.ConfigParser()

# 读取配置文件
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

print(application_path)

config.read(application_path + '/config.ini', encoding='utf-8')

# 获取配置值
DEBUG = config.getboolean('Global', 'DEBUG')
WOW_WINDOW_NAME = config.get('Global', 'WOW_WINDOW_NAME')
HEKILI_X = config.getint('Hekili', 'HEKILI_X')
HEKILI_Y = config.getint('Hekili', 'HEKILI_Y')
HEKILI_W = config.getint('Hekili', 'HEKILI_W')
HEKILI_H = config.getint('Hekili', 'HEKILI_H')
ABILITY_KEY_X = config.getint('Hekili', 'ABILITY_KEY_X')
ABILITY_KEY_Y = config.getint('Hekili', 'ABILITY_KEY_Y')
ABILITY_KEY_W = config.getint('Hekili', 'ABILITY_KEY_W')
ABILITY_KEY_H = config.getint('Hekili', 'ABILITY_KEY_H')
ABILITY_COOLDOWN_X = config.getint('Hekili', 'ABILITY_COOLDOWN_X')
ABILITY_COOLDOWN_Y = config.getint('Hekili', 'ABILITY_COOLDOWN_Y')
ABILITY_COOLDOWN_W = config.getint('Hekili', 'ABILITY_COOLDOWN_W')
ABILITY_COOLDOWN_H = config.getint('Hekili', 'ABILITY_COOLDOWN_H')
