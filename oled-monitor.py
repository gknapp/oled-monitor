#!/usr/bin/env python3

"""
Display system stats on an I2C OLED screen

Originally written for Orange Pi boards connected to 
an SH1106 1.3" OLED I2C display via GPIO pins.

Repo:
    https://github.com/gknapp/oled-monitor
"""

from luma.core.render import canvas

import argparse
import screen
import shell
import signal
import sys
import time

parser = argparse.ArgumentParser(
    description="Show SBC resource statistics on an I2C OLED display.",
    epilog="Origin: http://github.com/gknapp/oled-monitor"
)
parser.add_argument(
    "-sda", default=0x3c, required=False,
    help="a hexidecimal pin address, usually obtained using i2cdetect"
)
parser.add_argument(
    "-port", default=3, required=False,
    help="I2C port, ls /dev/i2c-* to see what ports exist"
)
parser.add_argument(
    "-tf", action="store_true",
    help="Use Fahrenheit temperature prefix (F). Default is Celsuis (C)"
)
parser.add_argument(
    "-q", action="store_true", help="Quiet mode"
)
args = parser.parse_args()

# TODO: fuzzing and swapping

DEG = u'\N{DEGREE SIGN}'
SCALE = "F" if args.tf else "C"

def on_terminate(device):
    def clear_screen():
        device.clear()
        sys.exit(0)
    return clear_screen

def thermals(text, offset):
    y = 29 + offset
    text.write((2, y), "{}{}: {}".format(
        DEG, SCALE, shell.cpu_temp(), shell.ram_temp()
    ))
    text.write((43, y), "/")
    text.write((49, y), shell.ram_temp())
    text.write((76, y), "CPU")
    text.write((97, y), "/")
    text.write((104, y), "RAM")

def display_stats(device):
    with canvas(device) as draw:
        text = screen.get_text(draw)
        gauge = screen.get_gauge(draw, text)
        mdns = shell.mdns_enabled()

        if (mdns):
            text.bold((1, 1), str(shell.hostname() + ".local").upper())
            text.write((3, 18), "IP: " + shell.ipaddr())
            # only room for this with host title
            if shell.updates_available():
                screen.updates_notice(draw, text)
        else:
            text.bold((1, 1), "IP: " + shell.ipaddr())

        offset = 0 if mdns else -6
        thermals(text, offset) # CPU / RAM temperature
        gauge((1, 41 + offset), "CPU", shell.cpu_usage())
        gauge((1, 53 + offset), "RAM", shell.ram_usage())

        time.sleep(1.5)

if __name__ == "__main__":
    try:
        device = screen.get_device(args.sda, args.port)
        clean_exit = on_terminate(device)

        signal.signal(signal.SIGTERM, clean_exit)
        signal.signal(signal.SIGABRT, clean_exit)

        if args.q is not True:
            print("Running ...")

        while True:
            display_stats(device)
    except KeyboardInterrupt:
        # Exit cleanly on Ctrl + C without displaying an exception
        on_terminate(device)()
    except OSError as ex:
        if (ex.errno == 6):
            print("Display not found on port {} at address {}".format(
                args.port, hex(args.sda)
            ))
            print("Check available ports with:\n")
            print("  ls -l /dev/i2c-*\n")
            print("Check device address with (eg. port 3):\n")
            print("  sudo i2cdetect -y {}\n".format(args.port))
        else:
            print(ex.message if hasattr(ex, "message") else ex)

        sys.exit(1)
