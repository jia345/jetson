from twisted.internet import reactor, task, defer, threads
import cv2
import numpy as np

class CameraCtrl():
    def __init__(self):
        self.__cb_notify_item = None
        #self.__stop_monitor = True

    def init(self, cb_notify_item):
        # initialization for camera and thread
        self.__cb_notify_item = cb_notify_item

    def start(self):
        if self.__cb_notify_item is None:
            print "please call init(cb_notify_item) with a callback as input at first"
        else:
            print "ok, let's start"

    def stop(self):
        print "let's stop"

def cb_notify_item(sku_id,num):
    print "sku_id=%d, num=%d" % (sku_id, num)

def main():
    cameraCtrl = CameraCtrl()
    #threads.deferToThread(cameraCtrl.startMonitor())
    cameraCtrl.init(cb_notify_item)
    cameraCtrl.start()
    #key = cv2.waitKey(1) & 0xFF
    #if key == ord('q'):
    #    cameraCtrl.stopMonitor()
    reactor.run()

if __name__ == "__main__":
    main()
