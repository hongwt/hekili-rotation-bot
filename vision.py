import time
import numpy as np
import hashlib
import torch

from PIL import Image, ImageGrab
from torchvision import transforms as T

from strhub.data.module import SceneTextDataModule
from strhub.models.utils import load_from_checkpoint, parse_model_args

import config

class Vision:

    # properties
    model_name = 'parseq'
    image_cache = {}  # Initialize the image cache as a list

    def __init__(self):
        model_path = 'parseq-onekey.ckpt'
        self._model =     model = load_from_checkpoint(model_path).eval().to('cpu').eval()
        self._preprocess = T.Compose([
            T.Resize((32, 128), T.InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(0.5, 0.5)
        ])

    @torch.inference_mode()
    def convertToText(self, image):
        if image is None:
            return '', []
        
        image = Image.fromarray(image)

        image = self._preprocess(image.convert('RGB')).unsqueeze(0)
        # Greedy decoding
        pred = self._model(image).softmax(-1)
        label, _ = self._model.tokenizer.decode(pred)
        raw_label, raw_confidence = self._model.tokenizer.decode(pred, raw=True)
        # Format confidence values
        max_len = len(label[0]) + 1
        conf = list(map('{:0.1f}'.format, raw_confidence[0][:max_len].tolist()))
        raw_output = label[0], [raw_label[0][:max_len], conf]
        if config.DEBUG:
            print('raw output: ', raw_output)
        # ('100', [['1', '0', '0', '[E]'], ['0.3', '0.4', '0.3', '0.4']])
        if float(conf[0]) >= 0.8:
            return label[0]
        else:
            return ''

    def get_ability_key(self, screenshot_np=None):
        # 技能按键区域
        ability_key_image = screenshot_np[config.ABILITY_KEY_Y:config.ABILITY_KEY_Y+config.ABILITY_KEY_H,
                                        config.ABILITY_KEY_X:config.ABILITY_KEY_X+config.ABILITY_KEY_W]

        if ability_key_image.size == 0:
            print("技能按键区域图像为空，可能是配置的区域超出了原图的范围。")
            return ''
            
        # 计算图像的哈希值
        image_hash = hashlib.sha256(ability_key_image.tobytes()).hexdigest()
        if image_hash in self.image_cache:
            return self.image_cache[image_hash]  # Return the cached key_text

        if len(self.image_cache) > 100:
            oldest_image = next(iter(self.image_cache))
            del self.image_cache[oldest_image]  # Remove the oldest screenshot from the cache

        key_text = self.convertToText(ability_key_image)
        if (key_text == '' or key_text == 'NA'):
            return ''

        self.image_cache[image_hash] = key_text  # Add the screenshot and key_text to the cache
        if config.DEBUG and key_text != 'NA':
            screenshot = Image.fromarray(ability_key_image)
            screenshot.save(f'images/valid_{key_text}_{time.time()}.png')
        
        return key_text

if __name__ == '__main__':
    vision = Vision()
    while True:
        screenshot_np = ImageGrab.grab(bbox=(config.HEKILI_X, 
                                       config.HEKILI_Y, 
                                       config.HEKILI_X + config.HEKILI_W, 
                                       config.HEKILI_Y + config.HEKILI_H))
        screenshot_np = np.array(screenshot_np)
        loop_time = time.time()
        key = vision.get_ability_key(screenshot_np)
        print(f'vision FPS {1 / (time.time() - loop_time)}')
        print('key output: ', key)
