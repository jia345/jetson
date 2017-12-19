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
import doorPcCtrl as doorCtrl
#import Jetson as JT
import logging

#url = 'http://localhost:5000'
#url = 'http://121.40.127.65:2121'
url = 'http://getway.52ywy.com:2121'
#shopping_cart = [{'sku_id':33212,'num':2},
#                 {'sku_id':33525,'num':1},
#                 {'sku_id':33210,'num':8}]
shopping_cart = []
is_open = 0
#the_door_ctrl = doorCtrl.DoorCtrl(cb_door_closed)
#the_camera_ctrl = JT.Classfication()

def get_mac_addr():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return mac

def get_door_id():
    return '0x000000017410b0c810000000150000c0'
    #return get_mac_addr()

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
    logging.info(reason)

#is_door_opened = 0
def cb_collect_info_response(rsp):
    global the_door_ctrl
    global the_camera_ctrl
    #global is_door_opened
    logging.info(u'<<<<<<<<<< rsp is %s' % rsp)
    parsed = None
    #if is_door_opened == 0:
    #    the_door_ctrl.open_the_door()
    #    is_door_opened = 1
    #    the_camera_ctrl.start()
    try:
        parsed = json.loads(rsp)
        cmd = parsed['response']
        if cmd == 'openDoor':
            the_door_ctrl.open_the_door()
            logging.info('the door is opened')
            #the_camera_ctrl.start()
    except:
        logging.info('do nothing')
        #rc = parsed['code']
        #if rc == 200:
        #    logging.info('okok')
        #else:
        #    logging.info('oops')

def cb_complete_order_response(rsp):
    logging.info(u"<<<<<<<< complete_order %s" % rsp)
    global shopping_cart
    shopping_cart = []

def test_complete_order():
    global url
    global shopping_cart
    #global the_camera_ctrl
    logging.basicConfig(filename='/home/hj/jetsond.log',level=logging.INFO)

    post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id', get_door_id()) ]
    #  ('items[]', "{'sku_id':33212,'num':2}"),
    #             ('items[]', "{'sku_id':33525,'num':1}"), ('items[]', "{'sku_id':33210,'num':8}") ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    logging.info(post_data)
    logging.info("YYYYY %s" % shopping_cart)
    for item in shopping_cart:
        post_data.append(tuple(['items[]', json.dumps(item, separators=(',',':'))]))

    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                    'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cb_complete_order_response)
    d.addErrback(cb_error)
    reactor.run()

def complete_order():
    global url
    global shopping_cart
    #global the_camera_ctrl

    post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id', get_door_id()) ]
    #  ('items[]', "{'sku_id':33212,'num':2}"),
    #             ('items[]', "{'sku_id':33525,'num':1}"), ('items[]', "{'sku_id':33210,'num':8}") ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    #post_data = [ ('class', 'Refrigerator'), ('method', 'completeOrder'), ('door_id': get_door_id()) ]
    logging.info(post_data)
    logging.info("YYYYY %s" % shopping_cart)
    for item in shopping_cart:
        post_data.append(tuple(['items[]', json.dumps(item, separators=(',',':'))]))

    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                    'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cb_complete_order_response)
    d.addErrback(cb_error)

    #the_camera_ctrl.stop()

def collect_info_cmd():
    global the_door_ctrl
    global url
    global is_open

    old_status = is_open

    logging.info('checking door status...')
 
    status = the_door_ctrl.check_the_door()
    logging.info('current door status is %d' % status)

    if old_status == 1 and status == 0:
        # door closed
        logging.info('door is closed...')
        cb_door_closed()

    if status == True:
        is_open = 1
    else:
        is_open = 0

    post_data = { 'class': 'Refrigerator', 'method': 'collectInfo', 'door_id': get_door_id(), 'is_open': is_open }
    logging.info('&&&&& post data %s' % post_data)
    d = httpRequest(url,
                    post_data,
                    {'User-Agent': ['Jetson Tx1'],
                     'Content-Type': ['application/x-www-form-urlencoded']},
                    'POST')
    d.addCallback(cb_collect_info_response)
    d.addErrback(cb_error)

def cb_door_closed():
    logging.info('******************************')
    logging.info('*** processing door closed ***')
    logging.info('******************************')
    complete_order()

def cb_notify_item(sku_id, num):
    global shopping_cart
    #item = {'sku_id': sku_id, 'num': num}
    is_found = 0
    for x in shopping_cart:
        if x.get('sku_id') == sku_id:
            x['num'] = x['num'] - num
            is_found = 1
        else:
            pass
            #x['sku_id'] = sku_id
            #x['num'] = num
    if is_found == 0:
        shopping_cart.append({'sku_id':sku_id,'num':-num})
    logging.info('HHHHHHHHHHHH %s' % shopping_cart)
    # shopping_cart.append(item)

def cb_notify_1():
    logging.info('HHHHHHHHHHHHHHHHHH')

def main():
    logging.basicConfig(filename='/home/hj/jetsond.log',level=logging.INFO)
    logging.info('starting ...')
    global the_door_ctrl
    #the_door_ctrl = doorCtrl.DoorCtrl(cb_door_closed)
    the_door_ctrl = doorCtrl.DoorCtrl()
    #time.sleep(40)
    cmd = task.LoopingCall(collect_info_cmd)
    cmd.start(1.0)

    #global the_camera_ctrl
    #the_camera_ctrl.init(cb_notify_item)

    reactor.run()

if __name__ == "__main__":
    main()
