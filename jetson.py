# This is the main controller running on Jetson TX1 board

from zope.interface import implements
from twisted.web.iweb import IBodyProducer
from twisted.internet import reactor, task, defer, threads, protocol
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
import json
import time
import urllib
#import cv2
#import doorCtrl

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

class SimpleReceiver(protocol.Protocol):
    def __init__(self, d):
        self.buf = ''; self.d = d

    def dataReceived(self, data):
        self.buf += data

    def connectionLost(self, reason):
        self.d.callback(self.buf)

def httpRequest(url, values=None, headers=None, method='POST'):
    agent = Agent(reactor)
    data = urllib.urlencode(values) if values else None

    d = agent.request(method, url, Headers(headers) if headers else {},
        StringProducer(data) if data else None
        )

    def handle_response(response):
        if response.code == 204:
            d = defer.succeed('')
        else:
            d = defer.Deferred()
            response.deliverBody(SimpleReceiver(d))
        return d

    d.addCallback(handle_response)
    return d

def cbError(reason):
    print(reason)

def cbResponse(rsp):
    d = readBody(rsp)
    d.addCallback(cbBody)
    return d

def cbCheckoutResponse(rsp):
    print rsp

def completeOrder():
    url = 'http://localhost:5000'
    #url = 'http://121.40.127.65.2121'
    postData = { 'class': 'Refrigerator', 'method': 'completeOrder', 'id': 'xxx', 'user_id': '111', 'door_id': '222',
                'items[]':'[[sku_id=1,num=1],[sku_id=2,num=2]]'}
    d = httpRequest(url,
            postData,
            {'User-Agent': ['Jetson Tx1'], 'Content-Type': ['application/x-www-form-urlencoded']},
            'POST'
            )
    d.addCallback(cbCheckoutResponse)
    d.addErrback(cbError)

def inquiryCmd():

    # 1. stop camera
    # 2. checkout
    url = 'http://localhost:5000'
    #url = 'http://121.40.127.65.2121'
    postData = { 'class': 'Refrigerator', 'method': 'collectInfo', 'id': 'xxx', 'is_open': '0'}
    d = httpRequest(url,
            postData,
            {'User-Agent': ['Jetson Tx1'], 'Content-Type': ['application/x-www-form-urlencoded']},
            'POST'
            )
    d.addCallback(cbCheckoutResponse)
    d.addErrback(cbError)
    #body = {'request': 'checkout'}
    #body = json.dumps(body)
    #body = StringProducer(body)

    #d = agent.request(
    #        b'POST',
    #        b'http://localhost:5000/checkout',
    #        Headers({'User-Agent': ['HelloHello']}),
    #        body 
    #        )
    #d.addCallback(cbCheckoutResponse)
    #d.addErrback(cbError)
    #d = agent.request(
    #        b'GET',
    #        b'http://localhost:5000/hello',
    #        Headers({'User-Agent': ['HelloHello']}),
    #        None
    #        )
    #d.addCallback(cbResponse)
    #d.addErrback(cbError)

def cbBody(body):
    #global theDoorCtrl
    #print('response body:', body)
    parsed = json.loads(body)
    cmd = parsed['msg']
    print('>>> received command is ' + cmd)
    if cmd == 'openDoor':
        # open door and camera
        #dl = list()
        #dl.append(d)
        #deferList = defer.DeferredList(dl)
        #theDoorCtrl.open_the_door()
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
    #agent = Agent(reactor)
    #theDoorCtrl = doorCtrl.DoorCtrl(cbDoorClosed)

    cmd = task.LoopingCall(inquiryCmd)
    cmd.start(1.0)

    reactor.run()