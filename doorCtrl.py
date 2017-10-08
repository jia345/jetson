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
        Controller.available_pins = [OPEN_THE_DOOR_GPIO,CHECK_THE_DOOR_GPIO]
        Controller.alloc_pin(number=OPEN_THE_DOOR_GPIO, direction='out')
        Controller.alloc_pin(number=CHECK_THE_DOOR_GPIO, direction='in',callback=self.door_is_closed,edge='falling')

    def door_is_closed(self,pin, state):
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print format("the door is closed !!! at %s " % dateTime)
        print format("pin = %d state = %d" % (pin, state))
        self.door_state = DOOR_IN_CLOSE

        if self.door_closed_cb != None :
            self.door_closed_cb()

    def open_the_door(self):
        Controller.set_pin(OPEN_THE_DOOR_GPIO)
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print format("the door is opend !!! at %s " % dateTime)
        sleep(2)
        Controller.reset_pin(OPEN_THE_DOOR_GPIO)
        self.door_state = DOOR_IN_OPEN

    def check_the_door(self):
        state = Controller.get_pin_state(CHECK_THE_DOOR_GPIO)

        return self.door_state





if __name__ == "__main__":
    theDoorCtrl = DoorCtrl()
    reactor.run()