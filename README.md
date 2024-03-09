Basic IP camera for Raspberry Pi. Tested only with Rasperry Pi 4 and Camera Module v3.

To install:

    sudo cp ipcam.py /usr/bin
    sudo cp ipcam.service /lib/systemd/system
    sudo systemctl enable ipcam.service
    sudo systemctl restart ipcam.service

Point browser at http://myhostname.local:8000.

CAUTION: provides no security whatsoever. Anyone with access to the network that the Pi is on can view.
