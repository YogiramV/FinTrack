import subprocess
import time
import os

from dotenv import load_dotenv
from kafka import KafkaAdminClient
from kafka.errors import KafkaError, TopicAlreadyExistsError
from kafka.admin import NewTopic


load_dotenv()


KAFKA_DIR = "kafka_2.13-4.3.1"

BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
TOPIC_NAME = "financial-transactions"


# ============================================================
# LOCAL KAFKA WORKFLOW
# ============================================================

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
    else:
        print("Topic may already exist.")


# ============================================================
# CONSUMER
# ============================================================

def start_consumer():
    print("Starting consumer...")

    consumer_process = subprocess.Popen(
        ["python3", "-m", "stream.kafka_consumer"]
    )

    return consumer_process


# ============================================================
# DOCKER KAFKA FUNCTIONS
# ============================================================

def wait_for_kafka_docker():
    print(f"Waiting for Kafka at {BOOTSTRAP_SERVER}...")

    while True:
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=BOOTSTRAP_SERVER,
                client_id="fintrack-setup"
            )

            admin_client.list_topics()
            admin_client.close()

            print("Kafka broker is ready.")
            break

        except KafkaError:
            print("Kafka is not ready yet...")
            time.sleep(2)


def create_topic_docker():
    print(f"Creating topic: {TOPIC_NAME}")

    admin_client = KafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVER,
        client_id="fintrack-setup"
    )

    topic = NewTopic(
        name=TOPIC_NAME,
        num_partitions=1,
        replication_factor=1
    )

    try:
        admin_client.create_topics(
            new_topics=[topic],
            validate_only=False
        )

        print("Topic created successfully.")

    except TopicAlreadyExistsError:
        print("Topic already exists. Skipping creation.")

    finally:
        admin_client.close()


def docker_setup():
    """
    Docker workflow.

    Kafka broker is already running in the Kafka container.

    Docker only:
    1. Waits for Kafka
    2. Creates the topic

    The consumer is started separately by Docker.
    """

    print("\nStarting Docker Kafka setup...\n")

    wait_for_kafka_docker()

    create_topic_docker()

    print("\nDocker Kafka setup completed.")
    print(f"Broker: {BOOTSTRAP_SERVER}")
    print(f"Topic: {TOPIC_NAME}")


# ============================================================
# NORMAL / LOCAL WORKFLOW
# ============================================================

def normal_setup():
    """
    Normal local workflow.

    1. Start local Kafka
    2. Wait for Kafka
    3. Create topic
    4. Start consumer
    """

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


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    environment = os.getenv("ENVIRONMENT", "local")

    if environment == "docker":
        docker_setup()
    else:
        normal_setup()
