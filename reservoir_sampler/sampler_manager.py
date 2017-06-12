import atexit
import json
import os
import signal
import subprocess

from dotenv import load_dotenv, find_dotenv
import zmq


class SamplerManager(object):
    STATE_WAITING = 'waiting'
    STATE_RUNNUNG = 'running'
    STATE_FINISHED = 'finished'
    STATE_STOPPED = 'stopeed'

    def __init__(self):
        self.context = zmq.Context()
        self.sampler = None
        self.state = self.STATE_WAITING
        atexit.register(self.kill_sampler)

    def initialize_connection(self):
        load_dotenv(find_dotenv())
        sampler_manager_address = os.environ.get('SAMPLER_MANAGER_ADDRESS')
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(sampler_manager_address)

    def kill_sampler(self):
        os.kill(self.sampler, signal.SIGTERM)

    def handle_message(self, msg):
        print('Received request: %s' % msg)
        cmd = msg['cmd']
        if cmd == 'start':
            return self.start_sampler(msg)
        elif cmd == 'status':
            return self.check_status(msg)
        elif cmd == 'stop':
            return self.stop_sampler(msg)
        else:
            return { 'error': 'unsupported command' }

    def start_sampler(self, msg):
        input_topic, output_topic = msg['input_topic'], msg['output_topic']
        size, limit = msg['size'], msg['limit']
        self.sampler = subprocess.Popen([
            'python', 'reservoir_sampler.py',
            input_topic, output_topic, size, limit
        ])
        self.state = self.STATE_RUNNING
        return { 'status': 'started' }

    def check_status(self):
        return { 'status': self.state }

    def stop_sampler(self):
        if self.sampler:
            self.kill_sampler()
            self.sampler = None
            self.state = self.STATE_STOPPED
            return { 'status': 'stopped' }
        else:
            return { 'error': 'sampler not running' }

    def update_status(self):
        if self.sampler and self.sampler.poll() is not None:
            self.status = self.STATE_FINISHED
            self.sampler = None

    def start(self):
        self.initialize_connection()
        while True:
            msg_json = self.socket.recv().decode('utf-8')
            self.update_status()
            msg = json.loads(msg_json)
            result = self.handle_message(msg)
            result_json = json.dumps(result)
            result_bytes = bytes(result_json, 'utf-8')
            self.socket.send(result_bytes)


if __name__ == '__main__':
    manager = SamplerManager()
    print('Waiting for messages')
    manager.start()
