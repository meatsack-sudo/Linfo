#!/bin/bash
export DISPLAY=$(echo $DISPLAY)
export XAUTHORITY=$(echo $XAUTHORITY)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$(pgrep -o gnome-session)/environ | cut -d= -f2-)

USER_PYTHON=$(which python3)

pkexec env DISPLAY=$DISPLAY XAUTHORITY=$XAUTHORITY DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS $USER_PYTHON /home/meatsack/Desktop/hwinfo_clone/hwtop.py
