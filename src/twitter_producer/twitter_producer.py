import json
import os
import sys

from dotenv import load_dotenv, find_dotenv
from kafka import KafkaProducer
from TwitterAPI import TwitterAPI

from lib.progress import log_progress
from lib.serializer import value_serializer


@log_progress('Loading environment')
def load_environment():
    load_dotenv(find_dotenv())


@log_progress('Loading Twitter credentials')
def load_twitter_credentials():
    return {
        'consumer_key': os.environ.get('TWITTER_CONSUMER_KEY'),
        'consumer_secret': os.environ.get('TWITTER_CONSUMER_SECRET'),
        'access_token_key': os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
        'access_token_secret': os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
    }


@log_progress('Initializing Twitter api client')
def initialize_twitter_api_client(credentials):
    return TwitterAPI(
        credentials['consumer_key'], credentials['consumer_secret'],
        credentials['access_token_key'], credentials['access_token_secret']
    )


@log_progress('Creating a stream of tweets')
def twitter_stream(twitter_client, filters):
    return twitter_client.request('statuses/filter', filters)


@log_progress('Streaming tweets to Kafka')
def stream_tweets_to_kafka(tweets_stream, kafka_client, topic):
    for tweet in tweets_stream:
        if not tweet.get('retweeted') and tweet.get('in_reply_to_user_id', None) is None:
            data = parse_tweet(tweet)
            print('.')
            kafka_client.send(topic, data)


def parse_tweet(tweet):
    return value_serializer(tweet)


@log_progress('Loading Kafka configuration')
def kafka_configuration():
    return {
        'bootstrap_servers': os.environ.get('KAFKA_BOOTSTRAP_SERVER')
    }


@log_progress('Initializing Kafka producer')
def initialize_kafka_producer(bootstrap_servers):
    return KafkaProducer(bootstrap_servers=bootstrap_servers)


def main(topic, filters):
    load_environment()
    credentials = load_twitter_credentials()
    twitter_client = initialize_twitter_api_client(credentials)
    stream = twitter_stream(twitter_client, filters)
    bootstrap_servers = kafka_configuration()['bootstrap_servers']
    kafka_producer = initialize_kafka_producer(bootstrap_servers)
    stream_tweets_to_kafka(stream, kafka_producer, topic)


if __name__ == '__main__':
    topic, filters_json = sys.argv[1], sys.argv[2]
    filters = json.loads(filters_json)
    print("Starting producer with params:", topic, filters)
    while True:
        try:
            main(topic, filters)
        except:
            print("An error occurred. Restarting.")
