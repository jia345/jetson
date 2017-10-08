# The purpose of this script is to provide a mimic web server in cloud
# 1. dump the messages between web server and main controller in unmanned box
# 2. interactively sending request or receiving response
from flask import Flask, jsonify, render_template, request
import time
app = Flask(__name__)

isCmdSent = True

@app.route('/_send_cmd')
def send_cmd():
    # global isCmdSend
    # isCmdSend = False
    cmd = request.args.get('cmd', 0, type=str)
    # ts = request.args.get('timestamp', 0, type=int)
    ts = time.time()
    # need to poll until Jetson board takes away the command
    result = {
        'result' : 'ok',
        'cmd'    : cmd,
        'ts'     : ts
    }
    return jsonify(result)

@app.route('/_long_run')
def long_run():
    time.sleep(10)
    count = 10000000000
    while (count < 0):
        print 'the count is:', count
        count = count - 1
    result = {
        'result' : 'zzzz',
    }
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', threaded=True)