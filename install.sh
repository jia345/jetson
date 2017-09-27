#!/bin/sh

pip install -r requirements.txt
INSTALL_DIR=/usr/local/unmanned-counter
[ -d ${INSTALL_DIR} ] || sudo mkdir ${INSTALL_DIR}
sudo cp *.py /usr/local/unmanned-counter
echo "\n=========================================="
echo "    unmanned-counter is ready to run"
echo "==========================================\n"
