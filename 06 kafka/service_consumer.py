from kafka import KafkaConsumer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from profi_ru import ServiceDB, Base
import json

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/profi_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройка Kafka
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "service_created"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='service-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def save_service_to_db(service):
    db = SessionLocal()
    db_service = ServiceDB(**service)
    db.add(db_service)
    db.commit()
    db.close()

if __name__ == "__main__":
    for message in consumer:
        service = message.value
        save_service_to_db(service)
        print(f"Service saved: {service}")