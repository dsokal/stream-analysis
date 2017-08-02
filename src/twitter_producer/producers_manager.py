import atexit
import json
import os
import signal
import subprocess

from dotenv import load_dotenv, find_dotenv
import zmq


class ProducersManager(object):
    def __init__(self):
        self.context = zmq.Context()
        self.producers = set()
        atexit.register(self.kill_children)

    def initialize_connection(self):
        load_dotenv(find_dotenv())
        producers_manager_address = os.environ.get('PRODUCERS_MANAGER_ADDRESS')
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(producers_manager_address)

    def kill_producer(self, pid):
        os.kill(pid, signal.SIGTERM)

    def kill_children(self):
        for pid in list(self.producers):
            self.kill_producer(pid)

    def handle_message(self, msg):
        print("Received request: %s" % msg)
        cmd = msg["cmd"]
        if cmd == "start":
            return self.start_producer(msg)
        elif cmd == "status":
            return self.check_status(msg)
        elif cmd == "stop":
            return self.stop_producer(msg)
        else:
            return { "error": "unsupported command" }

    def start_producer(self, msg):
        topic, filters = msg['topic'], msg['filters']
        process = subprocess.Popen(
            ["python", "-u", "twitter_producer.py", topic, json.dumps(filters)]
        )
        self.producers.add(process.pid)
        return { "status": "started", "pid": process.pid }

    def check_status(self, msg):
        pid = msg["pid"]
        if pid in self.producers:
            return { "status": "running" }
        else:
            return { "status": "not found" }

    def stop_producer(self, msg):
        pid = msg["pid"]
        if pid in self.producers:
            self.kill_producer(pid)
            self.producers.remove(pid)
            return { "status": "stopped" }
        else:
            return { "error": "producer not found" }

    def start(self):
        self.initialize_connection()
        while True:
            msg_json = self.socket.recv().decode("utf-8")
            msg = json.loads(msg_json)
            result = self.handle_message(msg)
            result_json = json.dumps(result)
            result_bytes = bytes(result_json, 'utf-8')
            self.socket.send(result_bytes)


if __name__ == '__main__':
    manager = ProducersManager()
    print("Waiting for messages")
    manager.start()
