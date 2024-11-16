import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from profi_ru import Base, UserDB, ServiceDB, OrderDB

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/profi_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Загрузка тестовых данных
def load_test_data():
    db = SessionLocal()

    # Проверка существования пользователя перед добавлением
    def add_user(username, first_name, last_name, hashed_password, email):
        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            user = UserDB(
                username=username,
                first_name=first_name,
                last_name=last_name,
                hashed_password=hashed_password,
                email=email,
            )
            db.add(user)

    # Создание пользователей
    add_user(
        username="admin",
        first_name="Admin",
        last_name="Admin",
        hashed_password=pwd_context.hash("admin001"),
        email="admin@profi.com",
    )

    add_user(
        username="user1",
        first_name="Ivan",
        last_name="Ivanov",
        hashed_password=pwd_context.hash("user123"),
        email="ivan.ivanov@profi.com",
    )

    add_user(
        username="user2",
        first_name="Igor",
        last_name="Pavlov",
        hashed_password=pwd_context.hash("user456"),
        email="igor.pavlov@profi.com",
    )

    # Создание услуги
    def add_service(name, price, description,stock):
        service = db.query(ServiceDB).filter(ServiceDB.name == name).first()
        if not service:
            service = ServiceDB(
                name=name,
                price=price,
                description=description,
                stock=stock,
            )
            db.add(service)

    add_service("English", 1500, "English in  skype")
    add_service("Math", 2000, "Math in skype")
    add_service("Site", 6500, "Site in Wordpress")

    # Создание заказа
    def add_order(user_id):
        order = db.query(OrderDB).filter(OrderDB.user_id == user_id).first()
        if not order:
            order = OrderDB(user_id=user_id)
            db.add(order)

    add_order(1)  # admin
    add_order(2)  # user1
    add_order(3)  # user2



    db.commit()
    db.close()


if __name__ == "__main__":
    load_test_data()

