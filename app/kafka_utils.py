from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os

KAFKA = os.environ["KAFKA"] if "KAFKA" in os.environ else "none"
KAFKA_TOPIC = os.environ["KAFKA_TOPIC"] if "KAFKA_TOPIC" in os.environ else "test-topic"


def create_topic():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA, client_id="user-post-client"
        )
        topic = NewTopic(name=KAFKA_TOPIC, num_partitions=1, replication_factor=1)
        admin_client.create_topics(new_topics=[topic], validate_only=False)
    except KafkaError as exc:
        print("kafka admin - Exception during creating topic - {}".format(exc))


def create_producer():
    create_topic()
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        return producer
    except KafkaError as exc:
        print("kafka producer - Exception during connecting to broker - {}".format(exc))
        return None
