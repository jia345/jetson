# The purpose of this script is to provide a mimic web server in cloud
# 1. dump the messages between web server and main controller in unmanned box
# 2. interactively sending request or receiving response

#from threading import Lock
#import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, render_template, request
#from flask_socketio import SocketIO, emit
import time
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
async_mode = None
thread = None
#thread_lock = Lock()

#socketio = SocketIO(app, async_mode=async_mode)

'''
def bg_thread():
    count = 0
    while True:
        socketio.sleep(1)
        count += 1
        socketio.emit('notify_items', {'data': count}, namespace='/notify')
'''

isCmdSent = True
cmd = 'None'

@app.route('/_open_door')
def openDoor():
    global cmd
    cmd = 'openDoor'
    app.logger.info('web request opendoor')
    return jsonify(cmd='openDoor')

# @app.route('/_send_cmd')
# def send_cmd():
#     # global isCmdSend
#     # isCmdSend = False
#     cmd = request.args.get('cmd', 0, type=str)
#     # ts = request.args.get('timestamp', 0, type=int)
#     ts = time.time()
#     # need to poll until Jetson board takes away the command
#     result = {
#         'result' : 'ok',
#         'cmd'    : cmd,
#         'ts'     : ts
#     }
#     return jsonify(result)

# @app.route('/_long_run')
# def long_run():
#     time.sleep(10)
#     count = 10000000000
#     while count < 0:
#         print 'the count is:', count
#         count = count - 1
#     result = {
#         'result' : 'zzzz',
#     }
#     return jsonify(result)

# @app.route('/')
# def index():
#     #return render_template('index.html', async_mode=socketio.async_mode)
#     return render_template('index.html')

# @app.route('/hello')
# def hello():
#     global cmd
#     preCmd = cmd
#     cmd = 'None'
#     return jsonify(msg=preCmd)

@app.route('/', methods=['GET','POST'])
def root():
    #cmd = request.args.get('request', 0, type=str)
    global cmd
    data = request.data
    classValue = request.values.get('class')
    stateValue = request.values.get('state')
    dataValue = request.values.get('data')
    methodValue = request.values.get('method')

    app.logger.info('classValue = %s' % classValue)
    app.logger.info('dataValue = %s' % dataValue)
    msg = None
    if classValue == 'Refrigerator':
        if methodValue == 'completeOrder':
            chipId = request.values.get('id')
            items = request.values.get('items[]')
            msg = {
                'id' : chipId,
                'items[]' : items
            }
        if methodValue == 'collectInfo':
            preCmd = cmd
            cmd = None
            chipId = request.values.get('id')
            isOpened = request.values.get('is_open')
            app.logger.info('jetson tells me the door status is ' + isOpened)

            doorState = 0
            if preCmd == 'openDoor':
                doorState = 1
            app.logger.info('I need the door status is %d' % doorState)
            msg = {
                'id': 'xxxx',
                'openDoor': doorState
            }
            sw_msg= {'ver': { 'web':'http://135.251.101.152:80/html.gz', 'model':'http://135.251.101.152:80/model.gz', 'main':'http://135.251.101.152:80/main.gz' } }
            msg=dict(msg.items()+sw_msg.items())

#    else:
    #    return render_template('index.html')

    if stateValue == 'maintenance':
        if eval(dataValue)['cmd']=='readyupdate':
            msg={'cmd':'','ret':{'action':'upgrade'}}
    return jsonify(msg)

'''
@socketio.on('connect', namespace='/notify')
def socketio_connect():
    emit('response', {'data': 'connected'})
'''

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', threaded=True)
    #app.host = '0.0.0.0'
    #app.threaded = True
    #app.debug = True
    #socketio.run(app)
