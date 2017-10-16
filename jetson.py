# -*- coding: utf-8 -*-
'''This is the main controller running on Jetson TX1 board
'''

import time
import json
import urllib
from zope.interface import implements
from twisted.web.iweb import IBodyProducer
from twisted.internet import reactor, task, defer, threads, protocol
from twisted.web.client import Agent, ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.web.http_headers import Headers
#import cv2
import doorCtrl as DoorCtrl

class StringProducer(object):
    '''A simple implementation of IBodyProducer
    '''
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        '''simple implementation
        '''
        consumer.write(self.body)
        return defer.succeed(None)

    def pauseProducing(self):
        '''do nothing
        '''
        pass

    def stopProducing(self):
        '''do nothing
        '''
        pass

class SimpleReceiver(protocol.Protocol):
    '''A simple implementation of receiver
    '''
    def __init__(self, obj_defer):
        self.buf = ''
        self.obj_defer = obj_defer

    def dataReceived(self, data):
        self.buf += data

    def connectionLost(self, reason):
        self.obj_defer.callback(self.buf)

class HttpClient(object):
    '''A simple http client based on twisted web client APIs
    '''
    def __init__(self, proxy=None):
        self.proxy = proxy

    def request(self, url, values=None, headers=None, method='POST', cb_response=None, cb_error=None):
        '''Send request to specified URL
        The default method is POST.
        If you don't input callback, it will use default callbacks which are defined internally.
        '''
        if self.proxy is None:
            agent = Agent(reactor)
        else:
            endpoint = TCP4ClientEndpoint(reactor, self.proxy[0], self.proxy[1])
            agent = ProxyAgent(endpoint)

        data = urllib.urlencode(values) if values else None

        def __cb_response(response):
            if response.code == 204:
                rc_defer = defer.succeed('')
            else:
                rc_defer = defer.Deferred()
                response.deliverBody(SimpleReceiver(rc_defer))
            return rc_defer

        def __cb_error(reason):
            print reason

        rc_defer = agent.request(method,
                                 url,
                                 Headers(headers) if headers else {},
                                 StringProducer(data) if data else None)

        if cb_response is None:
            rc_defer.addCallback(__cb_response)
        else:
            rc_defer.addCallback(cb_response)

        if cb_error is None:
            rc_defer.addErrback(__cb_error)
        else:
            rc_defer.addCallback(cb_error)
        return rc_defer

class Jetson(object):
    '''main class for controlling unmanned counter
    '''
    DEFAULT_POST_HEADER = {'User-Agent': ['Jetson Tx1'],
                           'Content-Type': ['application/x-www-form-urlencoded']}
    def __init__(self, door_ctrl, camera_ctrl, http_client=None):
        self.door_ctrl = door_ctrl
        self.camera_ctrl = camera_ctrl
        self.http_client = http_client
        self.url = 'http://localhost:5000'
        self.shopping_cart = {}
        #self.url = 'http://121.40.127.65:2121'

    def __collect_info(self):
        status = self.door_ctrl.check_the_door()
        is_open = 0
        if status is True:
            is_open = 1

        def __cb_collect_info_response(rsp):
            print '<<<<<<<<<< response is %s' % rsp
            try:
                parsed = json.loads(rsp)
                if 'response' in parsed.keys():
                    cmd = parsed['response']
                    if cmd == 'openDoor':
                        self.door_ctrl.open_the_door()
                        print 'the door is opened'
                        # TODO: we shall start the camera

                if 'code' in parsed.keys():
                    code = parsed.get('code')
                    msg = parsed.get('msg')
                    print 'code %d msg %s' % code, msg
            except ValueError:
                print 'response is not a valid JSON string'

        post_data = {'class': 'Refrigerator',
                     'method': 'collectInfo',
                     'door_id': '0x000000017410b0c810000000150000c0',
                     'is_open': is_open}
        #print '>>>>>>>>>> %s' % postData
        obj_defer = self.http_client.request(self.url,
                                             post_data,
                                             Jetson.DEFAULT_POST_HEADER,
                                             'POST')
        obj_defer.addCallback(__cb_collect_info_response)

    def __cb_complete_order_response(self, rsp):
        print "hihi %s" % rsp

    def __complete_order(self):
        post_data = [('class', 'Refrigerator'),
                     ('method', 'completeOrder'),
                     ('door_id', '0x000000017410b0c810000000150000c0'),
                     ('items[]', "{'sku_id':33212,'num':2}"),
                     ('items[]', "{'sku_id':33525,'num':1}"),
                     ('items[]', "{'sku_id':33210,'num':8}")]
        obj_defer = self.http_client.request(self.url,
                                             post_data,
                                             Jetson.DEFAULT_POST_HEADER,
                                             'POST')
        obj_defer.addCallback(self.__cb_complete_order_response)

    def __cb_door_closed(self):
        print '******************************'
        print '*** processing door closed ***'
        print '******************************'
        self.__complete_order()

    def start(self):
        '''start the heart-beat task and register the callbacks of processing
        door control and camera control

        door control: when the door is closed, the camera will informed to be
        sleep and stop scanning.

        camera control: when new item is added to/removed from shopping cart,
        camera shall inform main controller to update shopping cart
        '''
        cmd = task.LoopingCall(self.__collect_info)
        cmd.start(1.0)

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

if __name__ == "__main__":
    theDoorCtrl = DoorCtrl()
    theCameraCtrl = CameraCtrl()
    jetson = Jetson(theDoorCtrl, theCameraCtrl)
    jetson.start()

    reactor.run()
