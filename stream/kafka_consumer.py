from database.queries import *
import json
from kafka import KafkaConsumer
from dotenv import load_dotenv
import os

load_dotenv()

consumer = KafkaConsumer(
    "financial-transactions",
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    auto_offset_reset="earliest",
    group_id="fintrack-consumer",
    enable_auto_commit=False
)

print("Waiting for messages...")

for message in consumer:
    data = json.loads(message.value.decode("utf-8"))

    if insert(data):
        consumer.commit()
