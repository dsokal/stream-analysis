import zmq
import json
import subprocess
import atexit
import os
import signal

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("ipc://../producers-manager")

producers = set()

def kill_producer(pid):
    os.kill(pid, signal.SIGTERM)

def kill_children():
    for pid in list(producers):
        kill_producer(pid)

def handle_message(msg):
    print("Received request: %s" % msg)
    cmd = msg["cmd"]
    if cmd == "start":
        return start_producer(msg)
    elif cmd == "status":
        return check_status(msg)
    elif cmd == "stop":
        return stop_producer(msg)
    else:
        return { "error": "unsupported command" }


def start_producer(msg):
    global producers

    topic, filters = msg['topic'], msg['filters']
    process = subprocess.Popen(["python", "twitter_producer.py", topic, json.dumps(filters)])
    producers.add(process.pid)
    return { "status": "started", "pid": process.pid }

def check_status(msg):
    global producers

    pid = msg_json["pid"]
    if pid in producers:
        return { "status": "running" }
    else:
        return { "status": "not found" }

def stop_producer(msg):
    global producers

    pid = msg_json["pid"]
    if pid in producers:
        kill_producer(pid)
        return { "status": "stopped" }
    else:
        return { "error": "producer not found" }


if __name__ == '__main__':
    atexit.register(kill_children)
    while True:
        print("Waiting for messages")
        msg_json = socket.recv().decode("utf-8")

        msg = json.loads(msg_json)
        result = handle_message(msg)
        result_json = json.dumps(result)
        result_bytes = bytes(result_json, 'utf-8')

        socket.send(result_bytes)
