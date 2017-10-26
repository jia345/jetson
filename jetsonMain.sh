#!/bin/bash

MM=`ps -ef|grep ModemManager` 
echo 'kill ModemManager'
echo 'ubuntu' | sudo -S kill ${MM:5:9}

#cd /home/ubuntu/jetson.jia345
#echo 'ubuntu' | sudo -S python /home/ubuntu/jetson.jia345/jetson.py &

