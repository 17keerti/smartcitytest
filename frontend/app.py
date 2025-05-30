from flask import Flask, request, jsonify, render_template, Response, stream_with_context
from confluent_kafka import Consumer, KafkaException
import threading
import queue
import json
import os
from collections import defaultdict

app = Flask(__name__, template_folder='templates')

PORT = 6001
SERVICE_NAME = "frontend"
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:9092")
print(f"DEBUG: KAFKA_BROKER = {KAFKA_BROKER}") 

# Queues to hold messages for SSE clients
message_queues = defaultdict(queue.Queue)

def create_kafka_consumer(topics):
    consumer_conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'frontend-consumers',
        'auto.offset.reset': 'earliest'
    }
    print(f"DEBUG: Consumer config: {consumer_conf}")  # Debug: Print config
    consumer = Consumer(consumer_conf)
    consumer.subscribe(topics)
    print(f"DEBUG: Subscribed to topics: {topics}")  # Debug: Print subscribed topics
    return consumer

def consume_from_kafka():
    consumer = create_kafka_consumer(["traffic"])
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"DEBUG: Kafka error: {msg.error()}")
                continue

            # Add this check to handle None messages
            if msg.value() is not None:
                try:
                    message_value = json.loads(msg.value().decode('utf-8'))
                    print(f"DEBUG: Received message: {message_value}")
                except json.JSONDecodeError:
                    print(f"DEBUG: Could not decode message as JSON: {msg.value()}")
                    continue

                topic = msg.topic()
                message_queues[topic].put(message_value)
                print(f"DEBUG: Message queued for topic '{topic}'")
            else:
                print("DEBUG: Received a Kafka message with None value")  # Debug

    except KafkaException as e:
        print(f"DEBUG: Kafka consumer error: {e}")
    finally:
        consumer.close()

threading.Thread(target=consume_from_kafka, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    topic = request.args.get("topic")
    if not topic:
        return "❌ Topic required in query params", 400

    def event_stream():
        q = message_queues[topic]
        try:
            while True:
                msg = q.get()
                print(f"DEBUG: Sending SSE message: {msg} for topic: {topic}")
                yield f"data: {json.dumps(msg)}\n\n"
        except GeneratorExit:  # Corrected placement of except block
            print(f"DEBUG: SSE client disconnected from topic: {topic}")

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

if __name__ == '__main__':
    print(f"🚀 Subscriber frontend running at http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
