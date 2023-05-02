# System shell commands to retrieve resource metrics

import functools
import subprocess

# Helper functions

@functools.cache
def _distro_debian():
    cmd = "grep 'ID=debian' /etc/*release | wc -l"
    return int(_shellexec(cmd).rstrip())

def _shellexec(cmd):
    return subprocess.check_output(cmd, shell=True)

@functools.cache
def _cpu_cores():
    cores = _shellexec("grep -c ^processor /proc/cpuinfo").strip()
    return int(cores)

def _hwmon_exists(match):
    cmd = "grep -l '{}' /sys/class/hwmon/**/name".format(match)
    hwmon_file = _shellexec(cmd).decode().rstrip()
    return bool(hwmon_file), hwmon_file or "Not found"

# Last minute's load average
# NF-0 = 15 mins
# NF-1 = 10 mins
def _load_avg():
    la = _shellexec("uptime | awk '{printf \"%.2f\", $(NF-2)}'")
    return float(la)

# Public functions

def cpu_usage():
    return round(_load_avg() / _cpu_cores() * 100, 2)

def cpu_temp(match = "cpu"):
    return get_temp(match)

def get_temp(match):
    exists, hwmon_file = _hwmon_exists(match)
    if (exists):
        temp_file = hwmon_file.replace("name", "temp1_input")
        cmd = "awk '{{printf(\"%0.1f\", $1/1000)}}' {}".format(temp_file)
        return _shellexec(cmd).decode()
    else:
        return "0.0C"

def hostname():
    return _shellexec("hostname").decode().rstrip()

def ipaddr():
    return _shellexec("hostname -I | cut -d\' \' -f1").decode()

def mdns_enabled():
    cmd = "netstat --inet -lu | grep ':mdns' | wc -l"
    mdns = _shellexec(cmd).decode().strip()
    return int(mdns) == 1

def ram_temp(match = "ddr"):
    return get_temp(match)

def ram_usage():
    cmd = "free -m | awk 'NR==2{printf \"%.2f\", $3/$2*100 }'"
    return float(_shellexec(cmd))

# maxsize = calls, loop time 1.5s, 1.5 x 200 calls = 300s (5 mins)
@functools.lru_cache(maxsize=200)
def updates_available():
    if (_distro_debian()):
        debian = "apt list --upgradable 2>/dev/null | wc -l"
        return int(_shellexec(debian).rstrip()) > 1
    
    return False
