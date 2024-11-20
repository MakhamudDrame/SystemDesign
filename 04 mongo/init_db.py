import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from profi_ru import Base, ServiceDB

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/profi_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц
Base.metadata.create_all(bind=engine)


# Загрузка тестовых данных
def load_test_data():
    db = SessionLocal()



        # Создание услуги
    def add_service(name, price, description):
        service = db.query(ServiceDB).filter(ServiceDB.name == name).first()
        if not service:
            service = ServiceDB(
                name=name,
                price=price,
                description=description,
            )
            db.add(service)

    add_service("English", 1500, "English in  skype")
    add_service("Math", 2000, "Math in skype")
    add_service( "Site", 6500, "Site in Wordpress")

    

    db.commit()
    db.close()


def wait_for_db(retries=10, delay=5):
    for _ in range(retries):
        try:
            engine.connect()
            print("Database is ready!")
            return
        except Exception as e:
            print(f"Database not ready yet: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to the database")


if __name__ == "__main__":
    load_test_data()
