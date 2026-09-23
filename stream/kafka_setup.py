import subprocess
import time

KAFKA_DIR = "kafka_2.13-4.3.1"

BOOTSTRAP_SERVER = "localhost:9092"
TOPIC_NAME = "financial-transactions"


def start_kafka():
    print("Starting Kafka broker...")

    kafka_process = subprocess.Popen(
        [
            f"{KAFKA_DIR}/bin/kafka-server-start.sh",
            f"{KAFKA_DIR}/config/server.properties"
        ]
    )

    return kafka_process


def wait_for_kafka():
    print("Waiting for Kafka broker...")

    while True:
        result = subprocess.run(
            [
                f"{KAFKA_DIR}/bin/kafka-topics.sh",
                "--list",
                "--bootstrap-server",
                BOOTSTRAP_SERVER
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if result.returncode == 0:
            print("Kafka broker is ready.")
            break

        time.sleep(2)


def create_topic():
    print(f"Creating topic: {TOPIC_NAME}")

    result = subprocess.run(
        [
            f"{KAFKA_DIR}/bin/kafka-topics.sh",
            "--create",
            "--topic",
            TOPIC_NAME,
            "--bootstrap-server",
            BOOTSTRAP_SERVER,
            "--partitions",
            "1",
            "--replication-factor",
            "1"
        ]
    )

    if result.returncode == 0:
        print("Topic created successfully.")


def start_consumer():
    consumer_process = subprocess.Popen(
        ["python3", "-m", "stream.kafka_consumer"]
    )


if __name__ == "__main__":
    kafka_process = start_kafka()

    try:
        wait_for_kafka()
        create_topic()
        start_consumer()

        print("\nKafka is running.")
        print(f"Topic: {TOPIC_NAME}")
        print(f"Broker: {BOOTSTRAP_SERVER}")
        print("\nPress Ctrl+C to stop Kafka.")

        kafka_process.wait()

    except KeyboardInterrupt:
        print("\nStopping Kafka...")
        kafka_process.terminate()
        kafka_process.wait()
        print("Kafka stopped.")
