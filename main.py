# -*- coding: utf-8 -*-

import sys
from oledbutton import OledButton

btn = OledButton()
btn.connect()
image = len(sys.argv) > 1 and sys.argv[1] or "test.bmp"
btn.transfer_image(image)
r = btn.response()
if r:
    btn.save_image(len(sys.argv) > 2 and sys.argv[2] or 0)
btn.disconnect()
