"""
System shell commands to retrieve resource metrics
"""

import subprocess

# Helper functions

def _shellexec(cmd):
    return subprocess.check_output(cmd, shell=True)

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

def ram_usage():
    cmd = "free -m | awk 'NR==2{printf \"%.2f\", $3/$2*100 }'"
    return float(_shellexec(cmd))