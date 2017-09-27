# This is the main controller running on Jetson TX1 board

from twisted.internet import reactor, task
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
import doorCtrl
import json

agent = Agent(reactor)
theDoorCtrl = doorCtrl.DoorCtrl()

def inquiryCmd():
    d = agent.request(
            b'GET',
            b'http://localhost:5000/hello',
            Headers({'User-Agent': ['HelloHello']}),
            None
            )
    d.addCallback(cbResponse)

def cbResponse(rsp):
    #print('Response version:', rsp.version)
    #print('Response code:', rsp.code)
    #print('Response phrase:', rsp.phrase)
    d = readBody(rsp)
    d.addCallback(cbBody)
    return d

def cbBody(body):
    global theDoorCtrl
    print('response body:', body)
    # !!!! don't know why there is always an error "Unhandled error in Deferred:"
    # !!!! if below line is enabled
    parsed = json.loads(body)
    cmd = parsed['msg']
    print('cmd=' + cmd)
    print(len(cmd))
    if cmd == 'openDoor':
        print('haha')
        theDoorCtrl.open_the_door()
    else:
        print('no cmd')

if __name__ == "__main__":
    cmd = task.LoopingCall(inquiryCmd)
    cmd.start(1.0)

    reactor.run()
