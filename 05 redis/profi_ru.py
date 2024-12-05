from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Float,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pymongo import MongoClient
from bson import ObjectId
import redis
import os
import json 

# Настройка PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:archdb@db/profi_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Настройка Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

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

# Подключение к MongoDB
MONGO_URI = "mongodb://root:pass@mongo:27017/"
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["profi_db"]
mongo_users_collection = mongo_db["users"]


# Модели данных
class UserMongo(BaseModel):
    id: str
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





# SQLAlchemy models
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)


class ServiceDB(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, index=True)
    





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
        expire = datetime.utcnow() + timedelta(minutes=15)
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
@app.post("/users", response_model=UserMongo)
def create_user(user: UserMongo, current_user: str = Depends(get_current_client)):
    user_dict = user.dict()
    user_dict["hashed_password"] = pwd_context.hash(user_dict["hashed_password"])
    user_id = mongo_users_collection.insert_one(user_dict).inserted_id
    user_dict["id"] = str(user_id)
    return user_dict

# Поиск пользователя по логину
@app.get("/users/{username}", response_model=UserMongo)
def get_user_by_username(username: str, current_user: str = Depends(get_current_client)):
    user = mongo_users_collection.find_one({"username": username})
    if user:
        user["id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/services", response_model=List[Service])
def get_user_services(user_id: int, current_user: str = Depends(get_current_client)):
    # Ключ для кэширования услуг по user_id
    cache_key = f"services:user_id:{user_id}"
    
    # Попытка получить услуги из кэша Redis
    cached_services = redis_client.get(cache_key)
    
    if cached_services:
        # Если найдено в кэше, вернуть кэшированные услуги
        return json.loads(cached_services)
    
    # Если не найдено в кэше, запросить базу данных
    db = SessionLocal()
    services = db.query(ServiceDB).filter(ServiceDB.user_id == user_id).all()
    db.close()
    
    # Преобразовать услуги в список словарей
    services_list = [service.__dict__ for service in services]
    
    # Кэшировать услуги в Redis
    redis_client.set(cache_key, json.dumps(services_list))
    
    return services_list


# Получение услуг пользователя
@app.post("/services", response_model=Service)
def create_service(service: Service, current_user: str = Depends(get_current_client)):
    db = SessionLocal()
    db_service = ServiceDB(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    db.close()
    
    # Инвалидировать кэш для услуг пользователя
    cache_key = f"services:user_id:{db_service.user_id}"
    redis_client.delete(cache_key)
    
    return service






    

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
