from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import ImageFont

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

large  = ImageFont.truetype("fonts/pixeloperator.ttf", 15)
medium = ImageFont.truetype("fonts/pixelmix.ttf", 8)
small  = ImageFont.truetype("fonts/pixelade.ttf", 12)

def _textwhite(draw, font):
    return lambda pos, msg: draw.text(pos, msg, fill="white", font=font)

def get_text(draw):
    return dotdict({
        "large": _textwhite(draw, large),
        "write": _textwhite(draw, medium),
        "small": _textwhite(draw, small)
    })

def get_device(sda_addr, i2c_port):
    serial = i2c(address=sda_addr, port=i2c_port)
    return sh1106(serial)

def _bar(draw, pos):
    draw.rectangle(pos, outline="white", fill="white")

def _frame(draw, pos):
    draw.rectangle(pos, outline="white", fill="black")

def _inset(pos, px):
    x, y, xmax, ymax = pos
    return (x + px, y + px, xmax - px, ymax - px)

def bar_gauge(draw, pos, perc = 0):
    (x, y, xmax, ymax) = _inset(pos, 2)
    max = xmax - x
    width = round(perc / 100 * max)
    _frame(draw, pos)
    _bar(draw, (x, y, x + width, ymax))