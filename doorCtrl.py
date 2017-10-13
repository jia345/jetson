# -*- coding: utf-8 -*-

from sysfs.gpio import Controller
from twisted.internet import reactor
import time

OPEN_THE_DOOR_GPIO  =  186
CHECK_THE_DOOR_GPIO =  187

DOOR_IN_OPEN  = True
DOOR_IN_CLOSE = False

class DoorCtrl():
    def __init__(self,cb_door_close=None):
        self.door_closed_cb = cb_door_close
        self.door_state = DOOR_IN_CLOSE
        self.controller = Controller()
        self.controller.available_pins = [OPEN_THE_DOOR_GPIO,CHECK_THE_DOOR_GPIO]
        self.controller.alloc_pin(number=OPEN_THE_DOOR_GPIO, direction='out')
        self.controller.alloc_pin(number=CHECK_THE_DOOR_GPIO, direction='in',callback=self.door_is_closed,edge='falling')
        self.controller.set_pin(OPEN_THE_DOOR_GPIO)

    def door_is_closed(self,pin, state):
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print format("the door is closed !!! at %s " % dateTime)
        print format("pin = %d state = %d" % (pin, state))
        if state == False:
            if self.door_state == DOOR_IN_CLOSE:
                return
            self.door_state = DOOR_IN_CLOSE
            if self.door_closed_cb != None :
                self.door_closed_cb()
        else:
            self.controller.set_pin(OPEN_THE_DOOR_GPIO)


    def open_the_door(self):
        if self.door_state == DOOR_IN_OPEN:
            return 
        self.controller.reset_pin(OPEN_THE_DOOR_GPIO)
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print format("the door is opend !!! at %s " % dateTime)
        time.sleep(2)
        self.controller.set_pin(OPEN_THE_DOOR_GPIO)
        self.door_state = DOOR_IN_OPEN

    def check_the_door(self):
        state = self.controller.get_pin_state(CHECK_THE_DOOR_GPIO)
        if state == True:
            #print "The door state is open !"
            return DOOR_IN_OPEN
        else :
            #print "The door state is close !"
            return DOOR_IN_CLOSE
        pass
    
    def set_callback_door_closed(self, cb):
        self.door_closed_cb = cb

if __name__ == "__main__":
    theDoorCtrl = DoorCtrl()
    reactor.run()
