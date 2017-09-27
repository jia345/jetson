# This is the main controller running on Jetson TX1 board

from zope.interface import implements
from twisted.web.iweb import IBodyProducer
from twisted.internet import reactor, task, defer, threads
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
import doorCtrl
import json
import time
import cv2

class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def cbError(reason):
    print(reason)

def cbResponse(rsp):
    d = readBody(rsp)
    d.addCallback(cbBody)
    return d

def cbCheckoutResponse(rsp):
    print('***** hihi ****')

def inquiryCmd():

    # 1. stop camera
    # 2. checkout
    body = {'request': 'checkout'}
    body = json.dumps(body)
    body = StringProducer(body)

    d = agent.request(
            b'POST',
            b'http://localhost:5000/checkout',
            Headers({'User-Agent': ['HelloHello']}),
            body 
            )
    d.addCallback(cbCheckoutResponse)
    d.addErrback(cbError)
    #d = agent.request(
    #        b'GET',
    #        b'http://localhost:5000/hello',
    #        Headers({'User-Agent': ['HelloHello']}),
    #        None
    #        )
    #d.addCallback(cbResponse)
    #d.addErrback(cbError)

def cbBody(body):
    global theDoorCtrl
    #print('response body:', body)
    parsed = json.loads(body)
    cmd = parsed['msg']
    print('>>> received command is ' + cmd)
    if cmd == 'openDoor':
        # open door and camera
        #dl = list()
        #dl.append(d)
        #deferList = defer.DeferredList(dl)
        theDoorCtrl.open_the_door()
        d = threads.deferToThread(openCamera)
        d.addCallback(cbOpenCamera)
        #threads.deferToThread(recognition)
        #openCamera()

def openCamera():
    time.sleep(1)
    print('*** camera openned')
    return False

def cbOpenCamera(result):
    d = threads.deferToThread(recognition)
    d.addCallback(cbRecognition)

def recognition():
    time.sleep(3)
    #count = 100000
    #while count > 0:
    #    count = count - 1
    print('*** recognited')
    result = '{item="a"}'
    #return jason.loads("{item='a'}")
    return result

def cbRecognition(result):
    print(result)
    d = threads.deferToThread(recognition)
    d.addCallback(cbRecognition)

def cbDoorClosed():
    print('*** processing door closed ***')

    #def cbResponse():
    #    print('***** hihi ****')
    #def cbError(reason):
    #    print(reason)

    ## 1. stop camera
    ## 2. checkout
    #body = {'request': 'checkout'}
    #body = json.dumps(obj)
    #body = StringBodyProducer(body)

    #d = agent.request(
    #        b'POST',
    #        b'http://localhost:5000/checkout',
    #        Headers({'User-Agent': ['HelloHello']}),
    #        body 
    #        )
    #d.addCallback(cbResponse)
    #d.addErrback(cbError)

if __name__ == "__main__":
    agent = Agent(reactor)
    theDoorCtrl = doorCtrl.DoorCtrl(cbDoorClosed)

    cmd = task.LoopingCall(inquiryCmd)
    cmd.start(1.0)

    reactor.run()
