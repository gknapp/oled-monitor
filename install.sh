#!/bin/bash
if [ ! -d ".env" ]; then
    echo "Creating virtual environment ..."
    python3 -m venv .env && source .env/bin/activate
    
    if [ "$?" -eq 0 ]; then
        echo "Installing dependencies ..."
        pip install -r requirements.txt
    else
        echo "Failed to create virtual environment. Install aborted."
        exit 1
    fi
fi

if [ ! "$1" == "--install-service" ]; then
    read -p "Start OLED Monitor automatically on boot? [Y/n] " -n 1 -r

    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! "$REPLY" == "" ]]; then
        echo ""
        echo "Installation complete."
        exit
    fi

    [ "$(id -u)" -ne 0 ] && exec sudo -- "$0" --install-service
fi

SYSD_SVC="oled-monitor.service"
SYSD_FILE="/lib/systemd/system/$SYSD_SVC"

echo "Installing OLED monitor to run at system start ..."

cat << EOF > $SYSD_FILE
[Unit]
Description=OLED system resource service
After=multi-user.target

[Service]
ExecStart=$(pwd)/.env/bin/python $(pwd)/oled-monitor.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SYSD_SVC

echo -n "Starting service ... "

systemctl start $SYSD_SVC

if [ "$?" -eq 0 ]; then
    echo "done."
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
    echo "failed!"
    echo "Service could not be started."
fi
