# -*- coding: utf-8 -*-

import os
import time
import logging
from serialCom import usbModemCtrl
from jetson import main


class UsbModem_4G_Ctrl():
    def __init__(self):
        self.modem_pluggedIn = False
        self.modem_connected = False
        self.modem_sq = 0
        #self.modem = usbModemCtrl()
        self.modem = None
        self.mainloop = False

    def open_modem(self):
        if self.modem_pluggedIn == True:
            if self.modem_connected == True:
                return ;
            self.modem_connected = True
            if self.modem == None:
                self.modem = usbModemCtrl()

            self.modem_connected = self.modem.setup4Gconnect()
            logging.info("setting up 4G connection (%d) !! "  % self.modem_connected)

            if (self.mainloop == False) and self.modem_connected:
                #main()
                #os.system('. /home/ubuntu/jetsonMain.sh')
                self.mainloop = True


    def check_modem_dev(self):
        state = os.path.exists('/dev/ttyUSB0')
        if state == self.modem_pluggedIn:
            #print("modem_pluggedIn state None change %d" % state)
            return state
        self.modem_pluggedIn = state
        logging.info("modem_pluggedIn = %d" % state)

        if state == False :
            self.modem_pluggedIn = False
            self.modem_connected = False
            logging.info("USB Modem is unplugged!!")
	elif (state == True) and (self.modem == None):
            logging.info("USB Modem is created!!")
            self.modem = usbModemCtrl()

        return state
               
    def run_loop(self):
        time.sleep(5)
        os.system('/home/ubuntu/jetsonMain.sh')
        while(True) :
            if self.check_modem_dev() :
                self.open_modem()
            time.sleep(5)


if __name__ == "__main__":
    log_path = "/home/ubuntu/usbModem.log"
    fmt = "%(asctime)-15s %(levelname)s %(message)s"
    datefmt = "%a %d %b %Y %H:%M:%S"
    logging.basicConfig(filename=log_path,level=logging.INFO,format=fmt,datefmt=datefmt)

    modem = UsbModem_4G_Ctrl()
    modem.run_loop()
