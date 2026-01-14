import time
import os
import numpy as np
import hashlib
import torch

from PIL import Image, ImageGrab
from torchvision import transforms as T

from inference import CharacterPredictor

import config

class Vision:

    # properties
    model_name = 'pixelnet'
    image_cache = {}  # Initialize the image cache as a dict

    def __init__(self):
        model_path = os.path.join(config.application_path, 'best_model.pth')
        self._predictor = CharacterPredictor(model_path, device='cpu')
        self._preprocess = T.Compose([
            T.Resize((24, 24), T.InterpolationMode.BILINEAR),
            T.ToTensor()
        ])

    @torch.inference_mode()
    def convertToText(self, image):
        if image is None:
            return '', []
        
        # 使用 PixelNet 进行预测
        try:
            predicted_char, confidence = self._predictor.predict(image, return_confidence=True)
            
            if config.DEBUG:
                print(f'raw output: {predicted_char} (confidence: {confidence:.2f})')
            
            # 如果置信度小于阈值，返回空字符
            if confidence < config.CONFIDENCE_THRESHOLD:
                if config.DEBUG and confidence > 0.2:
                    screenshot = Image.fromarray(image)
                    image_path = os.path.join(config.application_path, 'images', f'LowConfidence_{predicted_char}_{time.time()}.png')
                    screenshot.save(image_path)
                return ''
            return predicted_char
        except Exception as e:
            if config.DEBUG:
                print(f'Prediction error: {e}')
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
        if (key_text == ''):
            return ''

        self.image_cache[image_hash] = key_text  # Add the screenshot and key_text to the cache
        if config.DEBUG and key_text != 'NA':
            screenshot = Image.fromarray(ability_key_image)
            image_path = os.path.join(config.application_path, 'images', f'valid_{key_text}_{time.time()}.png')
            screenshot.save(image_path)
        
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
