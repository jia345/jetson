# This is the main controller running on Jetson TX1 board

from zope.interface import implements
from twisted.web.iweb import IBodyProducer
from twisted.internet import reactor, task, defer, threads, protocol
from twisted.web.client import Agent, readBody, ProxyAgent
from twisted.internet.endpoints import HostnameEndpoint, TCP4ClientEndpoint
from twisted.web.http_headers import Headers
import json
import time
import urllib
#import cv2
import doorCtrl

#url = 'http://localhost:5000'
url = 'http://121.40.127.65:2121'
#theDoorCtrl = None

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
    endpoint = TCP4ClientEndpoint(reactor, "135.245.48.34", 8000)
    #endpoint = HostnameEndpoint(reactor, "135.245.48.34", 8000)
    agent = ProxyAgent(endpoint)
    #agent = Agent(reactor)
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

def cbCollectInfoResponse(rsp):
    global theDoorCtrl
    print '<<<<<<<<<< rsp is %s' % rsp
    parsed = None
    try:
        parsed = json.loads(rsp)
        cmd = parsed['response']
        #print('>>> received command is %s' % cmd)
        if cmd == 'openDoor':
            theDoorCtrl.open_the_door()
            print 'the door is opened'
    except:
        pass
        #rc = parsed['code']
        #if rc == 200:
        #    print 'okok'
        #else:
        #    print 'oops'

def cbCheckoutResponse(rsp):
    print "hihi %s" % rsp

def completeOrder():
    global url

    postData = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id', '0x000000017410b0c810000000150000c0'), ('items[]', "{'sku_id':33212,'num':2}"),
                ('items[]', "{'sku_id':33525,'num':1}"), ('items[]', "{'sku_id':33210,'num':8}") ]
    #postData = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': '0x000000017410b0c810000000150000c0') ]
    #postData = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': '0x000000017410b0c810000000150000c0') ]
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
    #url = 'http://localhost:5000'
    global theDoorCtrl
    global url
    status = theDoorCtrl.check_the_door()
    is_open = 0
    if status == True:
        is_open = 1

    postData = { 'class': 'Refrigerator', 'method': 'collectInfo', 'door_id': '0x000000017410b0c810000000150000c0', 'is_open': is_open }
    #print '>>>>>>>>>> %s' % postData
    d = httpRequest(url,
            postData,
            {'User-Agent': ['Jetson Tx1'], 'Content-Type': ['application/x-www-form-urlencoded']},
            'POST'
            )
    d.addCallback(cbCollectInfoResponse)
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

#def cbBody(body):
#    #global theDoorCtrl
#    #print('response body:', body)
#    parsed = json.loads(body)
#
#    cmd = parsed['msg']
#    print('>>> received command is ' + cmd)
#    if cmd == 'openDoor':
#        # open door and camera
#        #dl = list()
#        #dl.append(d)
#        #deferList = defer.DeferredList(dl)
#        theDoorCtrl.open_the_door()
#        is_open = 1
#        d = threads.deferToThread(openCamera)
#        d.addCallback(cbOpenCamera)
#        #threads.deferToThread(recognition)
#        #openCamera()
#    else:
#        is_open = 0

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
    print '******************************'
    print '*** processing door closed ***'
    print '******************************'
    completeOrder()

if __name__ == "__main__":
    #agent = Agent(reactor)

    #inquiryCmd()
    global theDoorCtrl
    theDoorCtrl = doorCtrl.DoorCtrl(cbDoorClosed)
    cmd = task.LoopingCall(inquiryCmd)
    cmd.start(1.0)

    reactor.run()
