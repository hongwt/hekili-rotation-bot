import os
import sys

import configparser

# 创建配置对象
config = configparser.ConfigParser()

# 获取应用程序路径
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

print(application_path)

# 配置文件路径
config_file_path = os.path.join(application_path, 'config.ini')

# 读取配置文件
config.read(config_file_path, encoding='utf-8')

# 获取配置值
DEBUG = config.getboolean('Global', 'DEBUG')

VALID_KEYS = config.get('Global', 'VALID_KEYS')

HEKILI_X = config.getint('Hekili', 'HEKILI_X')
HEKILI_Y = config.getint('Hekili', 'HEKILI_Y')
HEKILI_W = config.getint('Hekili', 'HEKILI_W')
HEKILI_H = config.getint('Hekili', 'HEKILI_H')
ABILITY_KEY_X = config.getint('Hekili', 'ABILITY_KEY_X')
ABILITY_KEY_Y = config.getint('Hekili', 'ABILITY_KEY_Y')
ABILITY_KEY_W = config.getint('Hekili', 'ABILITY_KEY_W')
ABILITY_KEY_H = config.getint('Hekili', 'ABILITY_KEY_H')

def save_config():
    """
    将当前配置变量的值保存到config.ini文件
    """
    # 更新配置对象中的值
    # Global部分
    config['Global']['DEBUG'] = str(DEBUG)
    config['Global']['VALID_KEYS'] = VALID_KEYS
    
    # Hekili部分
    config['Hekili']['HEKILI_X'] = str(HEKILI_X)
    config['Hekili']['HEKILI_Y'] = str(HEKILI_Y)
    config['Hekili']['HEKILI_W'] = str(HEKILI_W)
    config['Hekili']['HEKILI_H'] = str(HEKILI_H)
    
    config['Hekili']['ABILITY_KEY_X'] = str(ABILITY_KEY_X)
    config['Hekili']['ABILITY_KEY_Y'] = str(ABILITY_KEY_Y)
    config['Hekili']['ABILITY_KEY_W'] = str(ABILITY_KEY_W)
    config['Hekili']['ABILITY_KEY_H'] = str(ABILITY_KEY_H)
    
    # 将配置写入文件
    try:
        with open(config_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"配置已保存到 {config_file_path}")
        return True
    except Exception as e:
        print(f"保存配置时出错: {e}")
        return False