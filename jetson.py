# This is the main controller running on Jetson TX1 board

from zope.interface import implements
from twisted.web.iweb import IBodyProducer
from twisted.internet import reactor, task, defer, threads, protocol
from twisted.web.client import Agent, readBody, ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.web.http_headers import Headers
import json
import time
import urllib
#import cv2
import doorCtrl

#url = 'http://localhost:5000'
#url = 'http://121.40.127.65:2121'
url = 'http://getway.52ywy.com:2121'
shopping_cart = [{'sku_id':33212,'num':2},
                 {'sku_id':33525,'num':1},
                 {'sku_id':33210,'num':8}]

def get_door_id():
    return '0x000000017410b0c810000000150000c0'

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
        self.buf = ''
        self.d = d

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

    d = agent.request(method,
                      url,
                      Headers(headers) if headers else {},
                      StringProducer(data) if data else None)

    def handle_response(response):
        if response.code == 204:
            d = defer.succeed('')
        else:
            d = defer.Deferred()
            response.deliverBody(SimpleReceiver(d))
        return d

    d.addCallback(handle_response)
    return d

def cb_error(reason):
    print reason

def cbCollectInfoResponse(rsp):
    global theDoorCtrl
    print u'<<<<<<<<<< rsp is %s' % rsp
    parsed = None
    try:
        parsed = json.loads(rsp)
        cmd = parsed['response']
        if cmd == 'openDoor':
            theDoorCtrl.open_the_door()
            print 'the door is opened'
    except:
        print 'do nothing'
        #rc = parsed['code']
        #if rc == 200:
        #    print 'okok'
        #else:
        #    print 'oops'

def cb_complete_order_response(rsp):
    print u"hihi %s" % rsp

def complete_order():
    global url
    global shopping_cart

    post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id', get_door_id()) ]
    #  ('items[]', "{'sku_id':33212,'num':2}"),
    #             ('items[]', "{'sku_id':33525,'num':1}"), ('items[]', "{'sku_id':33210,'num':8}") ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    for item in shopping_cart:
        post_data.append(tuple(['items[]', json.dumps(item, separators=(',',':'))]))

    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                    'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cb_complete_order_response)
    d.addErrback(cb_error)

def collect_info_cmd():
    global theDoorCtrl
    global url
    status = theDoorCtrl.check_the_door()
    is_open = 0
    if status == True:
        is_open = 1

    post_data = { 'class': 'Refrigerator', 'method': 'collectInfo', 'door_id': get_door_id(), 'is_open': is_open }
    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                     'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cbCollectInfoResponse)
    d.addErrback(cb_error)

def openCamera():
    time.sleep(1)
    print '*** camera openned'
    return False

def cbOpenCamera(result):
    d = threads.deferToThread(recognition)
    d.addCallback(cbRecognition)

def recognition():
    time.sleep(3)
    #count = 100000
    #while count > 0:
    #    count = count - 1
    print '*** recognited'
    result = '{item="a"}'
    #return jason.loads("{item='a'}")
    return result

def cbRecognition(result):
    print u'%s' % result
    d = threads.deferToThread(recognition)
    d.addCallback(cbRecognition)

def cb_door_closed():
    print '******************************'
    print '*** processing door closed ***'
    print '******************************'
    complete_order()

if __name__ == "__main__":
    global theDoorCtrl
    theDoorCtrl = doorCtrl.DoorCtrl(cb_door_closed)
    cmd = task.LoopingCall(collect_info_cmd)
    cmd.start(1.0)

    reactor.run()
