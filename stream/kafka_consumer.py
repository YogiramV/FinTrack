import json
from kafka import KafkaConsumer

from database.queries import *

consumer = KafkaConsumer(
    "financial-transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    group_id="fintrack-consumer",
    enable_auto_commit=False
)

print("Waiting for messages...")

for message in consumer:
    data = json.loads(message.value.decode("utf-8"))

    if insert(data):
        consumer.commit()
