#!/bin/bash

MAIN_SCRIPT="oled-monitor.py"
PACKAGES="python3-virtualenv virtualenv"
SYSD_SVC="oled-monitor.service"
SYSD_FILE="/lib/systemd/system/$SYSD_SVC"

std='\033[0m'

echo_ok() {
    local green='\033[0;32m'
    printf "${green}$1${std}\n"
}

echo_error() {
    local red='\033[0;31m'
    printf "${red}$1${std}\n"
}

check_packages() {
    local deps=$(echo $PACKAGES | tr ' ' '|')
    local installed=$(apt list --installed 2>/dev/null | grep -E "^$deps" | wc -l)
    echo $installed
}

ensure_executable() {
    if [[ ! -x $MAIN_SCRIPT ]]; then
        chmod u+x,o-x $MAIN_SCRIPT
    fi
}

install_packages() {
    echo "Installing required system packages ..."
    apt update
    apt install -y $PACKAGES
}

install_python_env() {
    echo "Creating virtual environment ..."
    python3 -m venv .env && source .env/bin/activate
    
    if [ "$?" -eq 0 ]; then
        echo "Installing dependencies ..."
        pip install -r requirements.txt
    else
        echo "Failed to create virtual environment."
        echo_error "Install aborted"
        exit 1
    fi
}

remove_python_env() {
    rm -rf .env
    echo "Removed virtual environment"
}

install_service_prompt() {
    echo ""
    read -p "Start OLED Monitor automatically on boot? [Y/n] " -n 1 -r

    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! "$REPLY" == "" ]]; then
        echo 0
    else
        echo 1
    fi
}

install_service() {
    echo "Installing OLED monitor to run at system start ..."

    cat << EOF > $SYSD_FILE
[Unit]
Description=OLED system resource service
After=network.target

[Service]
ExecStart=$(pwd)/.env/bin/python $(pwd)/$MAIN_SCRIPT
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable $SYSD_SVC
}

is_root() {
    if [ "$(id -u)" -eq 0 ]; then echo "y"; else echo "n"; fi
}

start_service() {
    echo -n "Starting service ... "
    systemctl start $SYSD_SVC

    if [ "$?" -eq 0 ]; then
        echo_ok "OK"
        echo "Installation successful!"
        echo ""
        echo "You can check the service status with:"
        echo "  sudo systemctl status $SYSD_SVC"
        echo ""
        echo "To uninstall:"
        echo "  sudo systemctl disable $SYSD_SVC"
        echo "  sudo systemctl stop $SYSD_SVC"
        echo ""
    else
        echo_error "failed!"
        echo "Service could not be started."
    fi
}

ensure_executable

if [[ ! "$1" == "--root" ]]; then # not elevated, checks not run
    echo -n "Checking required system packages are installed ... "
    installed=$(check_packages)

    if [[ $installed -lt 2 ]]; then
        echo "Enter password to install required packages"
        [ $(is_root) == "n" ] && exec sudo -- "$0" --root
    else
        echo_ok "OK"
    fi
else # running with --root, suppress prompts
    [ $(check_packages) -lt 2 ] && install_packages
fi

if [[ "$1" == "--reinstall-venv" ]]; then
    # Force re-installation of python venv
    if [ -d ".env" ]; then remove_python_env; fi
    install_python_env
else
    # Only install dependencies if virtualenv doesn't exist
    if [ ! -d ".env" ]; then install_python_env; fi
fi

if [[ "$1" == "--root" ]]; then
    # suppress prompt
    install_service
    start_service
else
    if [[ ! "$1" == "--reinstall-venv" && $(install_service_prompt) -eq "1" ]]; then
        echo ""

        if [ $(is_root) == "n" ]; then
            sudo -- "$0" --root
        else # already root
            install_service
            start_service
        fi
    else
        echo ""
        echo "Installation complete"
    fi
fi