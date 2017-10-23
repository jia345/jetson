# -*- coding: utf-8 -*-

import os
from twisted.internet import reactor,threads
import time
import logging


class UsbModem_4G_Ctrl():
    def __init__(self):
        self.modem_pluggedIn = False
        self.modem_connected = False
        self.modem_sq = 0

    def open_modem(self):
        if self.modem_pluggedIn == True:
            if self.modem_connected == True:
                return ;
            output = open('/dev/ttyUSB0','w+')
            output.write("AT+CFUN=1\n")
            output.flush()
            logging.info("send AT+CFUN=1")
            time.sleep(20)

            output.write("AT+CGACT=1,1\n")
            output.flush()
            logging.info("send AT+CGACT=1")
            time.sleep(10)

            output.write("AT+ZGACT=1,1\n")
            output.flush()
            logging.info("send AT+ZGACT=1")
            time.sleep(5)
            logging.info("modem is oppened & connected!!")
            self.modem_connected = True 

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
            return state

        try:
            op = open("/dev/ttyUSB0")
            logging.info("Usb Modem is aviliable !")
            return True
        except IOError,e:
            logging.warn(e) 
            self.modem_pluggedIn = False
            self.modem_connected = False
            logging.warn("Usb Modem is unviliable !")
            return False
               
    def run_loop(self):
        time.sleep(30)
        while(1) :
            time.sleep(15)
            if self.check_modem_dev() :
                self.open_modem()


if __name__ == "__main__":
    log_path = "/home/ubuntu/usbModem.log"
    fmt = "%(asctime)-15s %(levelname)s %(message)s"
    datefmt = "%a %d %b %Y %H:%M:%S"
    logging.basicConfig(filename=log_path,level=logging.INFO,format=fmt,datefmt=datefmt)

    modem = UsbModem_4G_Ctrl()
    modem.run_loop()
