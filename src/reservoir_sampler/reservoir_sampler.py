import os
import sys

from dotenv import load_dotenv, find_dotenv
from kafka import KafkaConsumer, KafkaProducer

from reservoir import Reservoir
from utils import log_progress


@log_progress('Loading environment')
def load_environment():
    load_dotenv(find_dotenv())


@log_progress('Loading Kafka configuration')
def kafka_configuration():
    return {
        'bootstrap_servers': os.environ.get('KAFKA_BOOTSTRAP_SERVER')
    }

@log_progress('Initializing Kafka consumer')
def initialize_kafka_consumer(topic, bootstrap_servers):
    return KafkaConsumer(topic, bootstrap_servers=bootstrap_servers)


@log_progress('Initializing Kafka producer')
def initialize_kafka_producer(bootstrap_servers):
    return KafkaProducer(bootstrap_servers=bootstrap_servers)


@log_progress('Populating reservoir')
def populate_reservoir(kafka_consumer, reservoir, limit):
    for i in range(limit):
        element = kafka_consumer.__next__().value
        print(".")
        reservoir.process_element(element)
    return reservoir


@log_progress('Streaming reservoir to kafka')
def stream_reservoir_to_kafka(kafka_producer, topic, reservoir):
    for element in reservoir:
        kafka_producer.send(topic, element)
    kafka_producer.flush()


def main(input_topic, output_topic, reservoir_size, limit):
    load_environment()
    bootstrap_servers = kafka_configuration()['bootstrap_servers']
    kafka_consumer = initialize_kafka_consumer(input_topic, bootstrap_servers)
    kafka_producer = initialize_kafka_producer(bootstrap_servers)
    reservoir = Reservoir(reservoir_size)
    reservoir = populate_reservoir(kafka_consumer, reservoir, limit)
    stream_reservoir_to_kafka(kafka_producer, output_topic, reservoir)


if __name__ == '__main__':
    input_topic, output_topic = sys.argv[1], sys.argv[2]
    reservoir_size, limit = int(sys.argv[3]), int(sys.argv[4])
    main(input_topic, output_topic, reservoir_size, limit)
