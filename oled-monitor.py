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
import time
import sys
import screen
import shell

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
    "-q", "--quiet", nargs="?", default=None, help="Quiet mode"
)
args = parser.parse_args()

# TODO: fuzzing

def display_stats(device):
    with canvas(device) as draw:
        text = screen.get_text(draw)

        if (shell.mdns_enabled()):
            text.large((2, 0), str(shell.hostname()).lower() + ".local")

        text.write((2, 17), "IP: " + shell.ipaddr())

        cpu_usage = shell.cpu_usage()
        screen.bar_gauge(draw, (22, 29, 97, 37), cpu_usage)
        text.small((2, 27), "CPU")
        text.small((100, 27), str(round(cpu_usage, 1)) + "%")

        ram_usage = shell.ram_usage()
        screen.bar_gauge(draw, (22, 41, 97, 49), ram_usage)
        text.small((2, 39), "RAM")
        text.small((101, 39), str(round(ram_usage, 1)) + "%")

        text.small((1, 52), "TEMP {} / ".format(shell.cpu_temp()))
        time.sleep(1.5)

if __name__ == "__main__":
    try:
        device = screen.get_device(args.sda, args.port)

        if args.quiet is None:
            print("Running ...")

        while True:
            display_stats(device)
    except KeyboardInterrupt:
        # Exit cleanly on Ctrl + C without displaying an exception
        sys.exit(0)
