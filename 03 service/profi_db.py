from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import select


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    age = Column(Integer)
    
# Определение модели услуги
class Service(Base):
    __tablename__ = 'service'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    


# Определение модели заказа
class Order(Base):
    __tablename__ = 'order'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date_to_client=Column(Date, nullable=False)

def get_user(session : sessionmaker, username:str) -> User:
    return session.query(User).filter(User.username == username).first()

def get_users_all(session : sessionmaker) -> User:
    return session.query(User).all()

def create_user(session : sessionmaker, 
                username: str, email: str, 
                password: str, age: int):
        # Создание нового пользователя
    new_user = User(
        username=username,
        email=email,
        password=password,
        age=age
    )
    
    # Добавление нового пользователя в сессию
    session.add(new_user)
    
    # Коммит сессии для сохранения пользователя в базе данных
    session.commit()
    
    
    return new_user

def update_user(session: sessionmaker, user_id: int, 
                username: str = None, email: str = None, 
                password: str = None, age: int = None):
    # Найти пользователя по id
    user = session.query(User).filter(User.id == user_id).first()
    
    # Проверка, существует ли пользователь
    if user is None:
        print("Пользователь не найден")
        return None
    
    # Обновление полей, если они переданы
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password is not None:
        user.password = password
    if age is not None:
        user.age = age
    
    # Коммит изменений в сессии
    session.commit()
    
    # Возвращаем обновленного пользователя
    return user

def get_services(session: sessionmaker, service_id: int) -> Service:
    """Получить услугу по ID"""
    return session.query(Service).filter(Service.id == service_id).first()

def get_services_all(session: sessionmaker) -> list[Service]:
    """Получить все услуги"""
    return session.query(Service).all()

def create_service(session: sessionmaker, user_id: int, name: String, 
                   description: String, price: float) -> Service:
    """Создать новую услугу"""
    new_service = Service(
        user_id=user_id,
        name=name,
        description=description,
        price=price
    )
    
    session.add(new_service)
    session.commit()
    
    return new_service

def update_service(session: sessionmaker, service_id: int, 
                   name: String = None, description: String = None, 
                   price: float = None) -> Service:
    """Обновить услугу по  ID"""
    service = session.query(Service).filter(Service.id == service_id).first()
    
    if service is None:
        print("Услуга  не найдена")
        return None
    
    if name is not None:
        service.name = name
    if description is not None:
        service.description = description
    if price is not None:
        service.price = price
    
    session.commit()
    
    return service



def get_order(session: sessionmaker, order_id: int) -> Order:
    """Получить заказ по ID"""
    return session.query(Order).filter(Order.id == order_id).first()

def get_order_all(session: sessionmaker) -> list[Order]:
    """Получить все заказы"""
    return session.query(Order).all()

def create_order(session: sessionmaker, user_id: int,  name: String, 
                   description: String, price: float,date_to_client: Date) -> Order:
    """Создать новый заказ"""
    new_order = Order(
        user_id=user_id,
        name=name,
        description=description,
        price=price,
        date_to_client=date_to_client
    )
    
    session.add(new_order)
    session.commit()
    
    return new_order

def update_new_order(session: sessionmaker, order_id:int,  name: String= None, 
                   description: String= None, price: float= None,date_to_client: Date=None) -> Order:
    """Обновить заказ по  ID"""
    order = session.query(Order).filter(Order.id == order_id).first()
    
    if order is None:
        print("Заказ  не найден")
        return None
    
    if name is not None:
        order.name = name
    if description is not None:
        order.description = description
    if price is not None:
        order.price = price
    if date_to_client is not None:
        order.date_to_client=date_to_client
    
    session.commit()
    
    return order

