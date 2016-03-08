# -*- coding: utf-8 -*-

import sys
import binascii
from PIL import Image
import numpy

def save_dump(data):
    f = open("hex.dump", "w+")
    string = hex2str(data)
    f.write(string)
    f.close()

def hex2str(h):
    return binascii.b2a_qp(h).decode("utf-8")
     
def chr2hex(c):
    prepare_chr = c.encode('utf-8') # str to bytes-like object
    string_hex = binascii.hexlify(prepare_chr)
    return int(string_hex, 16)
    
def int2hex_str(value, n_pos):
    hex_str = hex(value)[2:]
    return hex_str.zfill(n_pos)
    
def int2bytes(value, n_pos):
    hex_str = int2hex_str(value, n_pos)
    b = bytearray.fromhex(hex_str)
    return b

def get_rgb_bytes_from_image(filename):
    im = Image.open(filename)   
    im = im.convert(mode='RGB')
    rgb888 = numpy.asarray(im)
    im.close()
    return rgb888.tobytes()
    
def get_rgb565_bytes_from_image(filename):
    im = Image.open(filename)
    im = im.convert(mode='RGB')
    (w,h) = im.size
    rgb888 = numpy.asarray(im)
    im.close()
    # check that image have 3 color components, each of 8 bits
    assert rgb888.shape[-1] == 3 and rgb888.dtype == numpy.uint8
    r5 = (rgb888[..., 0] >> 3 & 0x1f).astype(numpy.uint16)
    g6 = (rgb888[..., 1] >> 2 & 0x3f).astype(numpy.uint16)
    b5 = (rgb888[..., 2] >> 3 & 0x1f).astype(numpy.uint16)
    rgb565 = (r5 << 11 | g6 << 5 | b5).astype(numpy.uint16)
    if sys.byteorder == 'little':
        rgb565 = rgb565.byteswap()
    b = rgb565.tobytes()
    f = open("rgb.dump", "w")
    for y in range(0, h-1):
        d = b[y*(2*w):(y+1)*(2*w)]        
        s = binascii.b2a_qp(d).decode("utf-8")
        f.write(s + '\n\n')
    return b
