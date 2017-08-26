import sys
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
import msgpack

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


brokers = 'kafka:9092'
topic_name = 'lol_topic'


def populate_test_topic():
    producer = KafkaProducer(bootstrap_servers=brokers, value_serializer=msgpack.dumps)
    for i in range(100):
        obj = {"x": i}
        producer.send(topic_name, obj)
    producer.flush()
    producer.close()
    print('done')

# populate_test_topic()

def read_test_topic():
    consumer = KafkaConsumer(bootstrap_servers=brokers, value_deserializer=msgpack.loads)
    partition = TopicPartition(topic_name, 0)
    consumer.assign([partition])

    end = consumer.position(partition)
    consumer.seek(partition, end - 100)
    # print(consumer.seek_to_end())
    # from pprint import pprint
    # pprint(consumer.metrics())
    # print(consumer.partitions_for_topic(topic_name))
    for msg in consumer:
        print(msg)
    # print (type(consumer.partitions_for_topic(topic_name)))

# read_test_topic()

def integration():
    sc = SparkContext(appName="testApp")
    ssc = StreamingContext(sc, 2)

    kvs = KafkaUtils.createDirectStream(ssc, [topic_name], {"metadata.broker.list": brokers})
    lines = kvs.map(lambda x: x[1])
    # counts = lines.flatMap(lambda line: line.split(" ")) \
    #     .map(lambda word: (word, 1)) \
    #     .reduceByKey(lambda a, b: a + b)
    # counts.pprint()

    # ssc.start()
    # ssc.awaitTermination()

integration()
