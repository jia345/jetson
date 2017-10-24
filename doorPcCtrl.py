
from ctypes import *
from time import sleep
import ControlGPIO

DOOR_IN_OPEN  = True
DOOR_IN_CLOSE = False

class DoorCtrl():
    def __init__(self, cb_door_close=None):
        self.door_closed_cb = cb_door_close
        self.door_state = DOOR_IN_CLOSE
        self.nRet = c_int(0)
        self.deviceOpened = self.openDevice()
        if not self.deviceOpened:
            print("ERROR: DoorCtrl Initial Failed !!!")

    def openDevice(self):
        self.nRet = ControlGPIO.VGI_ScanDevice(1)
        if(self.nRet <= 0):
            print("No device connect!")
            return False
        else:
            print("Connected device number is:"+repr(self.nRet))

        self.nRet = ControlGPIO.VGI_OpenDevice(ControlGPIO.VGI_USBGPIO,0,0)
        if(self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Open device error!")
            return False
        else:
            print("Open device success!")
        sleep(1)
        return self.initGpioState()

    def closeDevice(self):
        if not self.deviceOpened:
            print("Device was Not Opened!!!")
            return True
        self.nRet = ControlGPIO.VGI_CloseDevice(ControlGPIO.VGI_USBGPIO, 0)
        if(self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Close device error!")
            return False
        else:
            print("Close device success!")
        return True

    def initGpioState(self):
        self.nRet = ControlGPIO.VGI_SetOutput(ControlGPIO.VGI_USBGPIO, 0, ControlGPIO.VGI_GPIO_PIN7 | ControlGPIO.VGI_GPIO_PIN8)
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Set GPIO_8 to output error!")
            return False
        else:
            print("Set GPIO_8 to output success!")
        self.nRet = ControlGPIO.VGI_ResetPins(ControlGPIO.VGI_USBGPIO, 0, ControlGPIO.VGI_GPIO_PIN7 | ControlGPIO.VGI_GPIO_PIN8);
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Set GPIO_8 low error!")
            return False
        else:
            print("Set GPIO_8 low success!")

        sleep(0.5)

        self.nRet = ControlGPIO.VGI_SetInput(ControlGPIO.VGI_USBGPIO, 0, ControlGPIO.VGI_GPIO_PIN5);
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Set GPIO_5 to input error!")
            return False
        else:
            print("Set GPIO_5 to input success!")

        sleep(0.5)
        pin_value = c_ushort(0)
        self.nRet = ControlGPIO.VGI_ReadDatas(ControlGPIO.VGI_USBGPIO, 0,ControlGPIO.VGI_GPIO_PIN5, byref(pin_value))
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Get pin data error!")
            return False
        else:
            if ((pin_value.value & ControlGPIO.VGI_GPIO_PIN5) != 0):
                print("GPIO_5 is high-level!")
            else:
                print("GPIO_5 is low-level!")
        sleep(0.5)
        return True

    def set_gpio8(self):
        self.nRet = ControlGPIO.VGI_SetPins(ControlGPIO.VGI_USBGPIO, 0, ControlGPIO.VGI_GPIO_PIN7 | ControlGPIO.VGI_GPIO_PIN8);
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Set GPIO_8 high error!")
        else:
            print("Set GPIO_8 high success!")

    def reset_gpio8(self): 
        print("reset_gpio8!")
        self.nRet = ControlGPIO.VGI_ResetPins(ControlGPIO.VGI_USBGPIO, 0, ControlGPIO.VGI_GPIO_PIN7 | ControlGPIO.VGI_GPIO_PIN8);
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Set GPIO_8 low error!")
        else:
            print("Set GPIO_8 low success!")

    def get_gpio5(self):
        pin_value = c_ushort(0)
        self.nRet = ControlGPIO.VGI_ReadDatas(ControlGPIO.VGI_USBGPIO, 0,ControlGPIO.VGI_GPIO_PIN5, byref(pin_value))
        if (self.nRet != ControlGPIO.ERR_SUCCESS):
            print("Get pin data error!")
            return False
        else:
            if ((pin_value.value & ControlGPIO.VGI_GPIO_PIN5) != 0):
                print("GPIO_5 is high-level!")
                return DOOR_IN_OPEN
            else:
                print("GPIO_5 is low-level!")
                return DOOR_IN_CLOSE



    def open_the_door(self):
        if not self.deviceOpened:
            print("ERROR:open_the_door:  Device Not Opened!!!")
            return

        if self.door_state == DOOR_IN_OPEN:
            return

        self.set_gpio8()
        #dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #print "the door is opend !!! at %s " % dateTime
        sleep(6)
        self.reset_gpio8()
        self.door_state = DOOR_IN_OPEN

    def check_the_door(self):
        if not self.deviceOpened:
            print("ERROR:check_the_door:  Device Not Opened!!!")
            return

        return self.get_gpio5()
if __name__ == "__main__":
    theDoorCtrl = DoorCtrl()
    theDoorCtrl.set_gpio8()
    sleep(30)
