from kafka import KafkaProducer
import json

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "service_created"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_service_created(service):
    producer.send(KAFKA_TOPIC, service)
    producer.flush()