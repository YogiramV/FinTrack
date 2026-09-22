import json
from kafka import KafkaProducer


def produce_to_kafka(statement_data):

    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda data: json.dumps(data).encode("utf-8")
    )

    producer.send(
        "financial-transactions",
        value=statement_data
    )

    producer.flush()

    print("Message sent successfully.")
