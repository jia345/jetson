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
import swUpdate
#import doorCtrl
#import Jetson as JT

url = 'http://localhost:5000'
#url = 'http://121.40.127.65:2121'
#url = 'http://getway.52ywy.com:2121'
shopping_cart = []

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
    #endpoint = TCP4ClientEndpoint(reactor, "135.245.48.34", 8000)
    #agent = ProxyAgent(endpoint)
    agent = Agent(reactor)
    data = urllib.urlencode(values) if values else None

    print "begin request"
    d = agent.request(method,
                      url,
                      Headers(headers) if headers else {},
                      StringProducer(data) if data else None)
    print "end request"

    def handle_response(response):
        print response.code
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

#is_door_opened = 0
def cb_collect_info_response(rsp):
    #global is_door_opened
    print u'<<<<<<<<<< rsp is %s' % rsp
    parsed = None
    #if is_door_opened == 0:
    #    the_door_ctrl.open_the_door()
    #    is_door_opened = 1
    #    the_camera_ctrl.start()
    try:
        parsed = json.loads(rsp)
        cmd = parsed['response']if u'response' in parsed else ""
        if cmd == 'openDoor':
            print 'the door is opened'
        print "before download"
        if a_update_test.has_update(rsp) :
            a_update_test.sw_download(rsp) 
        print "after download"
    except:
        print 'do nothing'
        #rc = parsed['code']
        #if rc == 200:
        #    print 'okok'
        #else:
        #    print 'oops'

def collect_info_cmd():
    global url
    global a_update_test
   # print a_update_test.get_current_ver().items()
    post_data = { 'class': 'Refrigerator', 'method': 'collectInfo', 'door_id': "1", 'is_open': '1' }
    post_data = dict(post_data.items()+a_update_test.get_current_ver().items())
    print '&&&&& post data %s' % post_data
    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                     'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cb_collect_info_response)
    d.addErrback(cb_error)

def cb_after_download():
    print "call back after download"
    a_update_test.sw_update()

def cb_after_update():
    print "call back after update"

def main():
    global a_update_test
    a_update_test=swUpdate.swUpdate( cb_after_download, cb_after_update )
    #print a_update_test.get_current_ver()
    cmd = task.LoopingCall(collect_info_cmd)
    cmd.start(1.0)
    reactor.run()

if __name__ == "__main__":
    main()
