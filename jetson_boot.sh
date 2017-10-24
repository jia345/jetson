#! /bin/sh

### BEGIN INIT INFO
# Provides:          ywy.com
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: ywy service
# Description:       ywy service daemon
### END INIT INFO

echo 'ubuntu' | sudo -S python /home/ubuntu/jetson.jia345/usbmodem4g.py &

