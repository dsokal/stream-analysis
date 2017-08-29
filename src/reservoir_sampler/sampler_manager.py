import sys
import os
import signal
import subprocess
from dotenv import load_dotenv, find_dotenv
import zmq

from lib.serializer import value_deserializer, value_serializer


class SamplerManager(object):
    STATE_WAITING = 'waiting'
    STATE_RUNNING = 'running'
    STATE_FINISHED = 'finished'
    STATE_STOPPED = 'stopeed'

    def __init__(self):
        self.context = zmq.Context()
        self.sampler = None
        self.state = self.STATE_WAITING

        def on_signal(*args):
            self.kill_sampler()
            sys.exit(1)

        for signal_name in (signal.SIGTERM, signal.SIGINT):
            signal.signal(signal_name, on_signal)

    def initialize_connection(self):
        load_dotenv(find_dotenv())
        sampler_manager_address = os.environ.get('SAMPLER_MANAGER_ADDRESS')
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(sampler_manager_address)

    def kill_sampler(self):
        if self.sampler is not None:
            os.kill(self.sampler.pid, signal.SIGTERM)

    def handle_message(self, msg):
        print('Received request: %s' % msg)
        cmd = msg['cmd']
        if cmd == 'start':
            return self.start_sampler(msg)
        elif cmd == 'status':
            return self.check_status()
        elif cmd == 'stop':
            return self.stop_sampler()
        else:
            return { 'error': 'unsupported command' }

    def start_sampler(self, msg):
        input_topic, output_topic = msg['input_topic'], msg['output_topic']
        size, limit = str(msg['size']), str(msg['limit'])
        self.sampler = subprocess.Popen([
            'python', '-u', '-m', 'reservoir_sampler.reservoir_sampler',
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
            self.state = self.STATE_FINISHED
            self.sampler = None

    def start(self):
        self.initialize_connection()

        while True:
            msg = value_deserializer(self.socket.recv())
            self.update_status()
            result = value_serializer(self.handle_message(msg))
            self.socket.send(result)


if __name__ == '__main__':
    manager = SamplerManager()
    print('Waiting for messages')
    manager.start()
