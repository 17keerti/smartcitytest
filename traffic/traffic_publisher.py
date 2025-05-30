import time
import random
from confluent_kafka import Producer
import os
import json # Import json

TOPIC = "traffic"
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")

# Kafka Producer configuration
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"✅ Message delivered to topic {msg.topic()} [{msg.partition()}]")

while True:
    congestion = random.choice(["low", "medium", "high"])
    priority = {"low": 2, "medium": 1, "high": 0}[congestion]

    traffic_data = {
        "congestion": congestion,
        "accident_reported": random.choice([True, False]),
        "location": "Main St"
    }

    message = {
        "topic": TOPIC,
        "data": traffic_data,
        "priority": priority,
    }

    try:
        # Produce the message to Kafka
        producer.produce(topic=TOPIC, value=json.dumps(message).encode('utf-8'), callback=delivery_report) # Use json.dumps()
        producer.flush()  # Ensure all messages are delivered
        print(f"➡️ Published to Kafka topic '{TOPIC}': {message}")

    except Exception as e:
        print(f"❌ Failed to publish to Kafka: {e}")

    time.sleep(10)
