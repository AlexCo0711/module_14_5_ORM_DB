# Домашнее задание по теме "План написания админ панели"

# импорт библиотеки SQLite
import sqlite3


# объявление функции initiate_db
def initiate_db():
    # создание и соединение с БД " "
    connection = sqlite3.connect("products.db")
    # создание курсора БД (виртуальная мышь)
    cursor = connection.cursor()

    # создание таблицы Products в БД через SQL-запросы с полями id, title, description, price
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products
    (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    price INTEGER NOT NULL
    )
    """)
    # заполнение БД данными
    # for i in range(1, 8):
    #     cursor.execute(
    #         'INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
    #         (f'Продукт {i}', f'Фигура {i}', f'{i * 100}')
    #     )

    # создание таблицы Users в БД через SQL-запросы с полями id, username, email, age, balance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users
        (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
        )
        """)

    # сохраняем изменения БД
    connection.commit()
    # закрываем соединение с БД
    connection.close()


# функция get_all_products возвращающая все записи из таблицы Products
def get_all_products():
    # соединение с БД "products.db"
    connection = sqlite3.connect("products.db")
    # создание курсора БД (виртуальная мышь)
    cursor = connection.cursor()
    # SQL запрос по извлечению всех записей таблицы Products БД products
    cursor.execute('SELECT * FROM Products')
    # возврат функции
    return cursor.fetchall()

# функция add_user() принимает имя пользователя, почту и возраст и добавляет
# в таблицу Users в БД запись с переданными данными
def add_user(username, email, age):
    # соединение с БД "products.db"
    connection = sqlite3.connect("products.db")
    # создание курсора БД (виртуальная мышь)
    cursor = connection.cursor()
    # добавление пользователя в таблицу User БД
    cursor.execute(
         'INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)', (username, email, age, 1000)
        )
    # сохраняем изменения БД
    connection.commit()

# функция is_included() принимает имя пользователя и возвращает True,
# если такой пользователь есть в таблице Users, в противном случае False
def is_included(username):
    # соединение с БД "products.db"
    connection = sqlite3.connect("products.db")
    # создание курсора БД (виртуальная мышь)
    cursor = connection.cursor()
    user_chek = cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    if user_chek.fetchone() is None:
        return False
    else:
        return True
    # сохраняем изменения БД и закрываем
    connection.commit()

# обращение к функции создания БД
initiate_db()