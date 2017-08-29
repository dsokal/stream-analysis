import json
import os
import signal
import subprocess
import zmq
import sys
from dotenv import load_dotenv, find_dotenv

from lib.serializer import value_deserializer, value_serializer


class ProducersManager(object):
    def __init__(self):
        self.context = zmq.Context()
        self.producers = set()

        def on_signal(*args):
            for pid in list(self.producers):
                self.kill_producer(pid)
            sys.exit(1)

        for signal_name in (signal.SIGTERM, signal.SIGINT):
            signal.signal(signal_name, on_signal)

    def initialize_connection(self):
        load_dotenv(find_dotenv())
        producers_manager_address = os.environ.get('PRODUCERS_MANAGER_ADDRESS')
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(producers_manager_address)

    def kill_producer(self, pid):
        os.kill(pid, signal.SIGTERM)

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
            ["python", "-u", "-m", "twitter_producer.twitter_producer", topic, json.dumps(filters)]
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
            msg = value_deserializer(self.socket.recv())
            result = value_serializer(self.handle_message(msg))
            self.socket.send(result)


if __name__ == '__main__':
    manager = ProducersManager()
    print("Waiting for messages")
    manager.start()
