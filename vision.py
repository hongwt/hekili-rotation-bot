import cv2 as cv
import time
import torch
from torchvision import transforms as T
from PIL import Image

import config

class Vision:

    # properties
    model = None

    def __init__(self):
        # load the trained model
        # 2 指定运行设备，这里为单块GPU
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.model = torch.hub.load('baudm/parseq', 'parseq_tiny', pretrained=True).eval()
        self._preprocess = T.Compose([
            T.Resize((32, 128), T.InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(0.5, 0.5)
        ])

    def convertToText(self, image):
        if image is None:
            return ''
        image = Image.fromarray(image).convert('RGB')
        image = self._preprocess(image).unsqueeze(0)
        # Greedy decoding
        pred = self.model(image).softmax(-1)
        label, _ = self.model.tokenizer.decode(pred)
        raw_label, raw_confidence = self.model.tokenizer.decode(pred, raw=True)
        # Format confidence values
        max_len = len(label[0]) + 1
        conf = list(map('{:0.1f}'.format, raw_confidence[0][:max_len].tolist()))
        raw_output = label[0], [raw_label[0][:max_len], conf]
        if config.DEBUG:
            print('raw output: ', raw_output)
        # ('100', [['1', '0', '0', '[E]'], ['0.3', '0.4', '0.3', '0.4']])
        if float(conf[0]) > 0.8:
            return label[0]
        else:
            return ''

    def get_ability_key(self, screenshot_np):
        # 技能按键区域
        ability_key_image = screenshot_np[config.ABILITY_KEY_Y:config.ABILITY_KEY_Y+config.ABILITY_KEY_H,
                                        config.ABILITY_KEY_X:config.ABILITY_KEY_X+config.ABILITY_KEY_W]
        if ability_key_image.size == 0:
            print("技能按键区域图像为空，可能是配置的区域超出了原图的范围。")
            return ''
        loop_time = time.time()
        key_text = self.convertToText(ability_key_image)
        print(f"convertToText take time: {time.time() - loop_time}...")
        # if config.DEBUG:
        #     cv.imwrite('images/Key_{}_{}.jpg'.format(key_text, time.time()), ability_key_image)
        
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
        cooldown_text = self.convertToText(ability_cooldown_image)
        # if config.DEBUG:
        #     cv.imwrite('images/Cooldown_{}_{}.jpg'.format(cooldown_text, time.time()), ability_cooldown_image)

        if cooldown_text and cooldown_text.isdigit() and int(cooldown_text) > 0 and int(cooldown_text) < 10:
            return int(cooldown_text)
        else:
            return -1
