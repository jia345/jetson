#!/usr/bin/env python

import serial, time
import logging

SERIALPORT = "/dev/ttyUSB0"
BAUDRATE = 115200

class usbModemCtrl() :
    def __init__(self):
        try:
            self.ser = serial.Serial(SERIALPORT, BAUDRATE)
            self.ser.bytesize = serial.EIGHTBITS #number of bits per bytes
            self.ser.parity = serial.PARITY_NONE #set parity check: no parity
            self.ser.stopbits = serial.STOPBITS_ONE #number of stop bits
            self.ser.timeout = 2              #timeout block read
            self.ser.xonxoff = False     #disable software flow control
            self.ser.rtscts = False     #disable hardware (RTS/CTS) flow control
            self.ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
            self.ser.writeTimeout = 0     #timeout for write
            logging.info('Starting Up Serial %s' % SERIALPORT)
        except IOError:
            self.ser.close()
            self.ser.open()
            logging.info("port was already open, was closed and opened again!")
            
    def setup4Gconnect(self):
        if self.ser.isOpen() :
            try:
                self.ser.flushInput() #flush input buffer, discarding all its contents
                #self.ser.flushOutput()#flush output buffer, aborting current output
                self.ser.write("AT+CFUN=0\015")
                logging.info("AT+CFUN=0") 
                time.sleep(3)
                self.ser.flushInput() #flush input buffer, discarding all its contents
                self.ser.write("AT+CFUN=1\015")
                logging.info("AT+CFUN=1") 
                time.sleep(0.5)
                setup_step = 0
                wait_counter = 45
                retry = 0
                while True:
                    response = self.ser.readline()
                    logging.info("read data: " + response)
                    if (setup_step == 0) and ((response[0:9] == '+CEREG: 1') or (response[0:7] == '+CREG: ') or (response[0:9] == '+CGDCONT:') or (response[0:2]=='OK')):

                        setup_step = 1
                        wait_counter = 51
                        retry = 0
                        logging.info("read data: " + response)
                        logging.info("AT+CFUN=1 done, next step %d" % setup_step)
                    elif (setup_step == 1) and ((response[0:9] == '+ZGIPDNS:')) :
                        setup_step = 2
                        wait_counter = 51
                        retry = 0
                        logging.info("read data: " + response)
                        logging.info("AT+CGACT=1 done, next step %d" % setup_step)
                    elif (setup_step == 2) and ((response[0:9] == '+ZCONSTAT')):
                        setup_step = 3
                        wait_counter = 51
                        retry = 0
                        logging.info("read data: " + response)
                        logging.info("AT+ZGACT=1 done, next step %d" % setup_step)
                    elif (response[0:5] == '+CME E') :
                        wait_counter = 51
 
                    if (setup_step == 0) and (wait_counter > 50) :
                        self.ser.flushInput() #flush input buffer, discarding all its contents
                        #self.ser.flushOutput()#flush output buffer, aborting current output
 
                        self.ser.write("AT+CFUN=1\015")
                        #time.sleep(0.4)
                        logging.info("AT+CFUN=1") 
                        wait_counter = 30
                        retry += 1
                        if retry == 10:
                            logging.info("retry over 3 time on AT+CFUN=1") 
                            return False
                        continue

                    if (setup_step == 1) and (wait_counter > 50) :
                        self.ser.flushInput() #flush input buffer, discarding all its contents
                        #self.ser.flushOutput()#flush output buffer, aborting current output
 
                        self.ser.write("AT+CGACT=1,1\015")
                        #time.sleep(0.5)
                        logging.info("AT+CGACT=1,1") 
                        wait_counter = 20 
                        #time.sleep(1)
                        retry += 1
                        if retry == 7:
                            logging.info("retry over 3 time on AT+CGACT=1,1") 
                            return False
                        continue

                    if (setup_step == 2) and (wait_counter > 50) :
                        self.ser.flushInput() #flush input buffer, discarding all its contents
                        #self.ser.flushOutput()#flush output buffer, aborting current output
 
                        self.ser.write("AT+ZGACT=1,1\015")
                        #time.sleep(0.5)
                        logging.info("AT+ZGACT=1,1") 
                        wait_counter = 2 
                        retry += 1
                        if retry == 5:
                            logging.info("retry over 3 time on AT+ZGACT=1,1") 
                            return False
                        continue

                    if (setup_step >= 3):
                        logging.info("Set is Done!!!") 
                        wait_counter = 0
                        break;
                    wait_counter += 1
                    #if wait_counter == 50 :
                    logging.info("wait counter %d step = %d retry=%d " % (wait_counter,setup_step,retry))

                self.ser.close()
                return True
            except Exception, e:
                logging.info("error communicating...: " + str(e))
                return False
        else :
            self.ser.open()
            logging.info("ttyUSB0 opened again!!!")
         
        return False


if __name__=='__main__':
    modem = usbModemCtrl()
    modem.setup4Gconnect()
