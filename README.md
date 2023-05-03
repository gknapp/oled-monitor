# OLED System Stats

Display system resource utilisation on a 1.3" SH1106 I2C display.

This script uses the Python 3 [luma-oled](https://github.com/rm-hull/luma.oled) library.

![1.3" OLED display with oled-monitor running](https://imgur.com/5frUtRU.jpg)

This script provides resource stats at a glance and advertises the hostname or IP.

If multi-cast DNS is not detected, only the IP address will be displayed.

![1.3" OLED display with oled-monitor running](https://imgur.com/BATsBDw.jpg)

## Install

1) `git clone git@github.com:gknapp/oled-monitor.git`
2) `cd oled-monitor && ./install.sh`

> If you run into issues with systemd not being able to run oled-monitor, check the log with:
> `sudo journalctl -e`

## Run

To run the script standalone without `install.sh`:

```bash
python3 -m venv .env && . .env/bin/activate
pip install -r requirements.txt
chmod u+x oled-monitor.py && ./oled-monitor.py
```

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

This script could be extended to work other I2C displays supported by luma-oled.