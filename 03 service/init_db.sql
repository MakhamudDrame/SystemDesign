-- Создание базы данных
CREATE DATABASE archdb;

-- Подключение к базе данных
\c archdb;

-- Создание таблицы пользователей с полями для хранения хешированного пароля
CREATE TABLE  users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    age INTEGER
);

-- Индекс для быстрого поиска по имени пользователя
CREATE INDEX IF NOT EXISTS idx_username ON users(username);

-- Создание таблицы  услуг
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(500) NOT NULL,
    price FLOAT NOT NULL
);

CREATE INDEX IF NOT EXISTS id_services ON users(username);


-- Создание таблицы заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    price FLOAT NOT NULL,
    date_to_client DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS id_user_id ON orders(user_id);


-- Тестовые данные

INSERT INTO users (id,username, email, hashed_password, age) VALUES
( 1,'ella', 'ella@example.com', '$2b$12$KIX/1Q0B1gYH3C8.x0ZQ1Oe1fS0f8s7H9r9a5e6q2gG1H5Xv4e5kO', 30 ),
(2, 'mike', 'mike@example.com', '$2b$12$D9U1Zc4F3lW4uD9gF3lW6uOe7f5s8s7H9r9a5e6q2gG1H5Xv4e5kO', 21),
(3, 'donald', 'donalde@example.com', '$2b$12$A3L2F0Q0B1gYH3C8.x0ZQ1Oe1fS0f8s7H9r9a5e6q2gG1H5Xv4e5kO', 50),
( 4, 'anna', 'anna@example.com', '$2b$12$E5U2Zc4F3lW4uD9gF3lW6uOe7f5s8s7H9r9a5e6q2gG1H5Xv4e5kO', 28);


INSERT INTO services (id, name, description, price) VALUES
(1, 'engish_lesson','online lessons',3000),
(2, 'shoe repair','repair all shoes',2500),
(3,'laundry','laundry of all',1000);

INSERT INTO orders (id, email, name, price, date_to_client) VALUES
(2,'mike@example.com','engish_lesson', 3000, '11.11.2024'),
(1,'ella@example.com','engish_lesson', 3000,'07.11.2024' ),
(3,'donalde@example.com','laundry of all',1000, '01.11.2024'),
(4,'anna@example.com','shoe repair', 2000, '03.11.2024');
