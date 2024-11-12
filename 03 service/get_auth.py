
# Файл второй лабораторной с get и post запросами и авторизацией





from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Модель данных для пользователя
class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

# Модель данных для услуги
class Service(BaseModel):
    id: int
    name: str
    price: float

# Временное хранилище для пользователей
users_db = []
service_db = []

# Псевдо-база данных пользователей
client_db = {
    "admin": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hashed "secret"
}


# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    password_check = False
    if form_data.username in client_db:
        password = client_db[form_data.username]
        if pwd_context.verify(form_data.password, password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[User])
def get_users(current_user: str = Depends(get_current_client)):
    return users_db

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: str = Depends(get_current_client)):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_client)):
    for u in users_db:
        if u.id == user.id:
            raise HTTPException(status_code=404, detail="User already exist")
    users_db.append(user)
    return user

# PUT /users/{user_id} - Обновить пользователя по ID (требует аутентификации)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: str = Depends(get_current_client)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, current_user: str = Depends(get_current_client)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(index)
            return deleted_user
    raise HTTPException(status_code=404, detail="User not found")

# GET /service - Получить список услуг (требует аутентификации)
@app.get("/service", response_model=List[Service])
def get_service(current_user: str = Depends(get_current_client)):
    return service_db

# POST /service - Создать новую услугу (требует аутентификации)
@app.post("/service", response_model=Service)
def create_service(service: Service, current_user: str = Depends(get_current_client)):
    for s in service_db:
        if s.id == service.id:
            raise HTTPException(status_code=404, detail="Service already exists")
    service_db.append(service)
    return service

# PUT /service/{service_id} - Обновить информацию о услуге (требует аутентификации)
@app.put("/service/{service_id}", response_model=Service)
def update_service(service_id: int, updated_service: Service, current_user: str = Depends(get_current_client)):
    for index, service in enumerate(service_db):
        if  service.id == service_id:
            service_db[index] = updated_service
            return updated_service
    raise HTTPException(status_code=404, detail="Service not found")

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)