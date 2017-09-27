from twisted.internet import reactor, task, defer, threads
import cv2
import numpy as np

class CameraCtrl():
    def __init__(self, cbUpdateShoppingCart=None):
        self.cbUpdateShoppingCart = cbUpdateShoppingCart
        self._stopMonitor = True

    def startMonitor(self):
        camera = cv2.VideoCapture(2)
        #camera = cv2.VideoCapture(0)
        #camera2 = cv2.VideoCapture(0)
        self._stopMonitor = False

        if (camera.isOpened()):
            print('Camera opened')
        else:
            print('oops, camera fails')

        #if (camera2.isOpened()):
        #    print('Camera 2 opened')
        #else:
        #    print('oops, camera 2 fails')

        es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
        kernel = np.ones((5, 5), np.uint8)
        bg = None
        while not self._stopMonitor:
            grabbed, frame = camera.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21,21), 0)
            if bg is None:
                bg = gray 
                continue
            diff = cv2.absdiff(bg, gray)
            diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            diff = cv2.dilate(diff, es, iterations=2)

            contours, hierarchy = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                if cv2.contourArea(c) < 1500:
                    continue
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow('contours', frame)
            cv2.imshow('dis', diff)
        camera.release()
        cv2.destroyAllWindows()

    def stopMonitor(self):
        self._stopMonitor = True

if __name__ == "__main__":
    cameraCtrl = CameraCtrl()
    #threads.deferToThread(cameraCtrl.startMonitor())
    cameraCtrl.startMonitor()
    #key = cv2.waitKey(1) & 0xFF
    #if key == ord('q'):
    #    cameraCtrl.stopMonitor()
    #reactor.run()

