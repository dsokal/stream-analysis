import json
import os
import sys

from dotenv import find_dotenv, load_dotenv
import zmq


class NotebookClient(object):
    def __init__(self):
        self.context = zmq.Context()
        load_dotenv(find_dotenv())

    def initialize_producers_manager_connection(self):
        producers_manager_address = os.environ.get('PRODUCERS_MANAGER_ADDRESS')
        self.producers_manager = self.context.socket(zmq.REQ)
        self.producers_manager.connect(producers_manager_address)

    def initialize_sampler_manager_connection(self):
        sampler_manager_address = os.environ.get('SAMPLER_MANAGER_ADDRESS')
        self.sampler_manager = self.context.socket(zmq.REQ)
        self.sampler_manager.connect(sampler_manager_address)

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

    def start_sampling_command(self, input_topic, output_topic, size, limit):
        return {
            'cmd': 'start',
            'input_topic': input_topic, 'output_topic': output_topic,
            'size': size, 'limit': limit
        }

    def stop_sampling_command(self):
        return { 'cmd': 'stop' }

    def sampling_status_command(self):
        return { 'cmd': 'status' }

    def start_sampling(self, input_topic, output_topic, size, limit):
        command = self.start_sampling_command(
            input_topic, output_topic, size, limit
        )
        result = self.execute_sampler_manager_command(command)
        return result.get('pid')

    def stop_sampling(self):
        command = self.stop_sampling_command()
        result = self.execute_sampler_manager_command(command)
        return result.get('status')

    def sampling_status(self):
        command = self.sampling_status_command()
        result = self.execute_sampler_manager_command(command)
        return result.get('status')

    def execute_producers_manager_command(self, command):
        return self.execute_command(self.producers_manager, command)

    def execute_sampler_manager_command(self, command):
        return self.execute_command(self.sampler_manager, command)

    def execute_command(self, manager, command):
        payload = self.encode_command(command)
        manager.send(payload)
        result_json = manager.recv().decode('utf-8')
        result = json.loads(result_json)
        if 'error' in result.keys():
            print(result['error'], file=sys.stderr)
            return {}
        else:
            return result

    def encode_command(self, command):
        return bytes(json.dumps(command), 'utf-8')
