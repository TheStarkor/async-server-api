import numpy as np
import base64
import sys

def base64_encode_image(img):
    return base64.b64encode(img).decode('utf-8')

def base64_decode_image(img, dtype, shape):
    img = bytes(img, encoding='utf-8')

    img = np.frombuffer(base64.decodestring(img), dtype=dtype)
    img = img.reshape(shape)

    return img