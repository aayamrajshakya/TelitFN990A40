#!/bin/bash

devices=$(ls /dev/cdc-wdm* 2>/dev/null)

if [ -z "$devices" ]; then
    echo "No device found"
    exit 1
fi

device=$(echo "$devices" | head -n 1)
wwan_interface="wwan0"

sudo qmicli -d $device --dms-set-operating-mode='low-power'
sleep 1
sudo qmicli -d $device --dms-set-operating-mode='online'
sleep 1
sudo ip link set $wwan_interface down
sleep 1
echo 'Y' | sudo tee /sys/class/net/$wwan_interface/qmi/raw_ip
sleep 2
sudo ip link set $wwan_interface up
sleep 1
sudo qmicli -p -d $device --device-open-net='net-raw-ip|net-no-qos-header' --wds-start-network="apn='internet',ip-type=4" --client-no-release-cid
sleep 2
sudo qmicli -p -d $device --wds-get-packet-service-status
sudo qmicli -p -d $device --wds-get-current-settings
sleep 2
sudo udhcpc -q -f -i $wwan_interface
