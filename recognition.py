import torch
from torchvision import transforms as T
from PIL import Image

import config

class Recognition:

    # properties
    model = None

    def __init__(self):
        # load the trained model
        self.model = torch.hub.load('baudm/parseq', 'parseq', pretrained=True).eval()
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
