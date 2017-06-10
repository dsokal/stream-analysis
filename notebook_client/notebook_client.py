import json
import os
import sys

from dotenv import find_dotenv, load_dotenv
import zmq


class NotebookClient(object):
    def __init__(self):
        self.context = zmq.Context()

    def initialize_producers_manager_connection(self):
        load_dotenv(find_dotenv())
        producers_manager_address = os.environ.get('PRODUCERS_MANAGER_ADDRESS')
        self.producers_manager = self.context.socket(ZMQ.REQ)
        self.producers_manager.connect(producers_manager_address)

    def start_streaming_command(self, topic, filters):
        return { 'cmd': 'start', 'topic': topic, 'filters': filters }

    def stop_streaming_command(self, pid):
        return { 'cmd': 'stop', 'pid': pid }

    def streaming_status_command(self, pid):
        return { 'cmd': 'status', 'pid': pid }

    def start_streaming(self, topic, filters):
        command = self.start_streaming_command(topic, filters)
        result = self.execute_producers_manager_command(command)
        return result.get('pid')

    def stop_streaming(self, pid):
        command = self.stop_streaming_command(pid)
        result = self.execute_producers_manager_command(command)
        return result.get('status')

    def streaming_status(self, pid):
        command = self.streaming_status_command(pid)
        result = self.execute_producers_manager_command(command)
        return result.get('status')

    def execute_producers_manager_command(self, command):
        payload = self.encode_command(command)
        self.producers_manager.send(payload)
        result = self.producers_manager.recv()
        if 'error' in result.keys():
            print(result['error'], file=sys.stderr)
            return {}
        else:
            return result

    def encode_command(self, command):
        return bytes(json.dumps(command), 'utf-8')
