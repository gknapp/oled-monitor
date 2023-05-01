from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import ImageFont

# Assumes a 128x64 display using the SH1106 driver

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

bold   = ImageFont.truetype("fonts/pixeloperator-sc-bold.ttf", 15)
# large  = ImageFont.truetype("fonts/pixeloperator.ttf", 15)
medium = ImageFont.truetype("fonts/pixelmix.ttf", 8)
small  = ImageFont.truetype("fonts/pixelade.ttf", 12)

# Internal module helper functions

def _bar(draw, pos):
    draw.rectangle(pos, outline="white", fill="white")

def _frame(draw, pos):
    draw.rectangle(pos, outline="white", fill="black")

def _inset(pos, px):
    x, y, xmax, ymax = pos
    return (x + px, y + px, xmax - px, ymax - px)

def _text(draw, font):
    def partial(pos, msg, color="white"):
        draw.text(pos, msg, fill=color, font=font)
    return partial

# Public functions

def bar_gauge(draw, pos, perc = 0):
    (x, y, xmax, ymax) = _inset(pos, 2)
    max = xmax - x
    width = round(perc / 100 * max)
    _frame(draw, pos)
    _bar(draw, (x, y, x + width, ymax))

def get_device(sda_addr, i2c_port):
    serial = i2c(address=sda_addr, port=i2c_port)
    return sh1106(serial)

def get_gauge(draw, text):
    def gauge(pos, label, percent):
        (x, y) = pos
        bar_gauge(draw, (x + 21, y, x + 96, y + 8), percent)
        text.small((x, y - 2), label)
        text.small((x + 99, y - 2), str(round(percent, 1)) + "%")
    
    return gauge

def get_text(draw):
    return dotdict({
        "bold": _text(draw, bold),
        # "large": _textwhite(draw, large),
        "small": _text(draw, small),
        "write": _text(draw, medium)
    })

def updates_notice(draw, text):
    def backfill_box(x, y, w, h):
        # rounded corners
        dia = 5
        draw.ellipse((x, y, x + dia, y + dia), fill="white") # top left corner
        draw.ellipse((x, y + dia, x + dia, y + h), fill="white") # bot left corner
        draw.ellipse((x + w - dia, y, x + w, y + dia), fill="white") # top right corner
        draw.ellipse((x + w - dia, y + h - dia, x + w, y + h), fill="white") # bot right corner
        # backfill
        inset = round(dia / 2)
        draw.rectangle((x + inset, y, x + w - inset, y + h), fill="white")
        draw.rectangle((x, y + inset, x + w, y + h - inset), fill="white")

    backfill_box(100, 17, 25, 10)    
    text.write((104, 18), "UPD!", "black")