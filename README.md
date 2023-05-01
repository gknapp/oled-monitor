# OLED System Stats

Display system resource utilisation on a 1.3" I2C display.

This script was built using an SH1106 display. It uses the Python 3 
[luma-oled](https://github.com/rm-hull/luma.oled) library.

![1.3" OLED display with oled-monitor running](https://imgur.com/5frUtRU.jpg)

This script was originally written to provide resource stats at a glance and a hostname or IP.

If multi-cast DNS is not detected, no `.local` host will be shown, instead only an IP.

![1.3" OLED display with oled-monitor running](https://imgur.com/BATsBDw.jpg)

## Install

1) `git clone git@github.com:gknapp/oled-monitor.git && cd oled-monitor`
2) `virtualenv .env && source .env/bin/activate && pip install -r requirements.txt`

## Run

`chmod a+x oled-monitor.py`  
`./oled-monitor.py`

## Options

```bash
usage: oled-monitor.py [-h] [-sda SDA] [-port PORT] [-tf] [-q]

Show SBC resource statistics on an I2C OLED display.

optional arguments:
  -h, --help  show this help message and exit
  -sda SDA    a hexidecimal pin address, usually obtained using i2cdetect
  -port PORT  I2C port, ls /dev/i2c-* to see what ports exist
  -tf         Use Fahrenheit temperature prefix (F). Default is Celsuis (C)
  -q          Quiet mode
```