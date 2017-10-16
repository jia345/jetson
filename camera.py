from twisted.internet import reactor, task, defer, threads
import cv2
import time
import numpy as np

class CameraCtrl():
    def __init__(self, cb_new_item=None):
        self.__cb_new_item = cb_new_item
        self.__is_started = False

    def __the_thread(self, cb_notify_item):
        while True:
            if self.__is_started is True:
                time.sleep(1.5)
                # send msg to main controller
                msg = {'sku_id': 123,'num': 2}
                self.__cb_new_item(msg)
            else:
                pass

    def run(self):
        '''start loop to wait for the main controller demands
        '''
        while True:

    def start_monitor(self):
        self.__is_started = True

    def stop_monitor(self):
        self.__is_started = False

if __name__ == "__main__":
    camera_ctrl = CameraCtrl()
    camera_ctrl.run()
    reactor.run()

