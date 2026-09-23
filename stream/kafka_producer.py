import json
from kafka import KafkaProducer
from dotenv import load_dotenv
import os

load_dotenv()


def produce_to_kafka(statement_data):

    producer = KafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        value_serializer=lambda data: json.dumps(data).encode("utf-8")
    )

    producer.send(
        "financial-transactions",
        value=statement_data
    )

    producer.flush()

    print("Message sent successfully.")
