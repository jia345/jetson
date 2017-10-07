# -*- coding: utf-8 -*-

from sysfs.gpio import Controller
from twisted.internet import reactor
import time


def door_is_closed(pin, state):
    dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print format("the door is closed !!! at %s " % dateTime)
    print format("pin = %d state = %d" % (pin,state))

OPEN_THE_DOOR=186
CHECK_THE_DOOR=187

 class DoorCtrl():
    def __init__(self):
        Controller.available_pins = [OPEN_THE_DOOR,CHECK_THE_DOOR]
        Controller.alloc_pin(number=OPEN_THE_DOOR, direction='out')
        Controller.alloc_pin(number=CHECK_THE_DOOR, direction='in',callback=door_is_closed,edge='falling')

    def open_the_door(self):
        Controller.set_pin(OPEN_THE_DOOR)
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print format("the door is opend !!! at %s " % dateTime)
        sleep(2)
        Controller.reset_pin(OPEN_THE_DOOR)

    def check_the_door(self):
        return Controller.get_pin_state(CHECK_THE_DOOR)





if __name__ == "__main__":
    theDoorCtrl = DoorCtrl()
    reactor.run()