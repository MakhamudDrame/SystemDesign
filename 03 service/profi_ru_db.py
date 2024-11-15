from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/profi_ru_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели данных
class User(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    hashed_password: str
    email: str


class Service(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None

class Order(BaseModel):
    id: int
    user_id: int
    order_ids: List[int]

# SQLAlchemy models

class UserDB(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    
    
# Определение модели услуги
class ServiceDB(Base):
    __tablename__ = 'service'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    

# Определение модели заказа
class OrderDB(Base):
    __tablename__ = 'order'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_ids = Column(String)


# Зависимости для получения текущего пользователя
async def get_current_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        else:
            return username
    except JWTError:
        raise credentials_exception
    

    # Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    db.close()

    if user and pwd_context.verify(form_data.password, user.hashed_password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Создание нового пользователя
@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    db_user = UserDB(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return user



# Поиск пользователя по логину
@app.get("/users/{username}", response_model=User)
def get_user_by_username(username: str, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    user = db.query(UserDB).filter(UserDB.username == username).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



# Создание услуги
@app.post("/service", response_model=Service)
def create_product(service: Service, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    db_service = ServiceDB(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    db.close()
    return service


# Получение списка услуг
@app.get("/service", response_model=List[Service])
def get_user_service(user_id: int, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    services = db.query(ServiceDB).filter(ServiceDB.user_id == user_id).all()
    db.close()
    return services




# Добавление услуги в заказ
@app.post("/orders/{user_id}", response_model=Order)
def add_to_order(user_id: int, service_id: int, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    order = db.query(OrderDB).filter(OrderDB.user_id == user_id).first()

    if not order:
        order = OrderDB(user_id=user_id, order_ids=str([service_id]))
        db.add(order)
    else:
        current_order_ids = order.order_ids.split(",")
        if str(service_id) not in current_order_ids:
            current_order_ids.append(str(service_id))
            order.order_ids = ",".join(current_order_ids)

    db.commit()
    db.refresh(order)
    db.close()
    return order



# Получение заказов пользователя
@app.get("/orders/{user_id}", response_model=Order)
def get_orders(user_id: int, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    order = db.query(OrderDB).filter(OrderDB.user_id == user_id).first()
    db.close()

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    return order


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

