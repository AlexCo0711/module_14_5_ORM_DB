# Домашнее задание по теме "Написание примитивной ORM"

# импорт необходимых библиотек и методов
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
# блок из aiogram для работы с клавиатурой и объект кнопки
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import config
# импорт данных из crud_functions
from crud_functions import *

bot = Bot(token=config.TOKEN)
# переменная dp объекта «Dispatcher», у него наш бот в
# качестве аргументов. В качестве «Storage» будет «MemoryStorage»
dp = Dispatcher(bot, storage=MemoryStorage())

# Клавиатуры:

# Онлайн "главная" клавиатура:
kb_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Расчитать'),
            KeyboardButton(text='Информация')
        ],
        [KeyboardButton(text='Купить')],
        [KeyboardButton(text='Регистрация')]
    ], resize_keyboard=True, one_time_keyboard=True
)

# Инлайн клавиатуры:
# клавиатура выбора расчёта
kb_info = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
        ]
    ]
)

# клавиатура по количеству id в БД
buttons_list=[]
# цикл по количеству продуктов в БД
for item in get_all_products():
    # добавление в список кнопок с наименованием продукта из БД
    buttons_list.append(
        [InlineKeyboardButton(text=f'{item[1]}', callback_data='product_buying')]
    )
# вывод кнопок клавиатуры выбора продукта
kb_product = InlineKeyboardMarkup(inline_keyboard=buttons_list)

# объявление класса состояния UserState наследованный от StatesGroup
class UserState(StatesGroup):
    # объявление объектов класса age, growth, weight, man (возраст, рост, вес, пол)
    age = State()
    growth = State()
    weight = State()

# класс состояний RegistrationState со следующими объектами класса
# State: username, email, age, balance(по умолчанию 1000)
class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

# обработчик начала общения с ботом (команды /start)
@dp.message_handler(commands=['start'])
# функция старта
async def start(message):
    # дополнение методом reply_markup для отображения клавиатуры kb
    await message.answer('Привет! Я бот помогающий вашему здоровью.\n'
                         'Нажмите одну из кнопок для продолжения', reply_markup=kb_main)


# обработчик ожидания нажатия кнопки «Расчитать»
@dp.message_handler(text=['Расчитать'], state=None)
# функция получения возраста пользователя
async def main_menu(message: types.Message, state: FSMContext):
    # ожидание нажатия кнопок выбора
    await message.answer('Выберите опцию:', reply_markup=kb_info)


# обработчик ожидания нажатия кнопки «Формулы расчёта»
@dp.callback_query_handler(text=['formulas'])
# функция вывода расчётной формулы
async def get_formula(call: types.CallbackQuery):
    await call.message.answer('Формула расчёта Миффлина-Сан Жеора:\n'
                              '(10*вес + 6.25*рост + 5*возраст + 5) - для мужчин\n'
                              '(10*вес + 6.25*рост + 5*возраст - 161) - для женщин', reply_markup=kb_main)


# обработчик ожидания нажатия кнопки «Расчитать»
@dp.callback_query_handler(text=['calories'])
# функция получения возраста пользователя
async def set_age(call: types.CallbackQuery):
    # ожидание сообщения Calories и вывод текста
    await call.message.answer('Ваш возраст (полных лет):')
    # ожидание останова данной функци
    await call.answer()
    # ожидание ввода возраста
    await UserState.age.set()


# обработчик ожидания окончания статуса UserState.age
@dp.message_handler(state=UserState.age)
# функция получения роста пользователя
async def set_growth(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения возраста от пользователя в базе данных состояния
    await state.update_data(age_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой рост (см):')
    # ожидание ввода роста
    await UserState.growth.set()


# обработчик ожидания окончания статуса UserState.growth
@dp.message_handler(state=UserState.growth)
# функция получения веса пользователя
async def set_weight(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения роста от пользователя в базе данных состояния
    await state.update_data(growth_=message.text)
    # ожидание вывода текста
    await message.answer('Введите свой вес (кг):')
    # ожидание ввода веса
    await UserState.weight.set()


# обработчик ожидания окончания статуса UserState.weight и выбора пола пользователя
@dp.message_handler(state=UserState.weight)
# функция получения пола пользователя
async def set_weight(message: types.Message, state: FSMContext):
    # ожидание сохранение сообщения веса от пользователя в базе данных состояния
    await state.update_data(weight_=message.text)
    # сохранение полученных данных в переменной data
    data = await state.get_data()
    # подсчет согласно формуле Миффлина-Сан Жеора
    calories_m = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 + 5
    calories_w = int(data['weight_']) * 10 + int(data['growth_']) * 6.25 - int(data['age_']) * 5 - 161
    # ожидание вывода текста результатов расчета
    await message.answer(f'Ваша норма калорий в день для:\n'
                         f'мужчин - {calories_m}\n'
                         f'женщин -  {calories_w}', reply_markup=kb_main)
    await state.finish()


# обработчик кнопок Информация
@dp.message_handler(text=['Информация'])
# функция кнопок
async def inform(message):
    await message.answer("Бот поможет расчитать суточный рацион в калориях\n"
                         "для вашего возраста, роста, веса и пола", reply_markup=kb_main)


# обработчик ожидания нажатия кнопки «Купить»
@dp.message_handler(text=['Купить'])
# функция кнопок
async def get_buying_list(message):
    # цикл перебора вариантов продуктов
    for k in get_all_products():
        # открытие файла изображения продукта
        with open(f'{k[0]}.jpg', 'rb') as img:
            # ожидание отображения продукта
            await message.answer_photo(img, f"Название: {k[1]} | Описание: {k[2]} | Цена: {k[3]}")
    await message.answer(text='Выберите продукт для покупки:', reply_markup=kb_product)


# обработчик ожидания нажатия кнопки выбранного продукта
@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):
    # обращение к картинке
    with open("0.jpg", 'rb') as img0:
        # ожидание выбора
        await call.message.answer_photo(img0, 'Вы успешно приобрели продукт!')
    # закрытие ожидания
    await call.answer()

# цепочки изменений состояний RegistrationState:
# обработчик ожидания нажатия кнопки «Регистрация»
@dp.message_handler(text=['Регистрация'])
async def sihg_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит): ')
    # ожидание ввода имени в атрибут RegistrationState.username
    await RegistrationState.username.set()

# обработчик реагирует на состояние RegistrationState.username
@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    # условие проверки существования пользователя в таблице User БД
    if is_included(message.text):
        await message.answer("Пользователь существует, введите другое имя")
        # запрашиваем новое состояние для RegistrationState.username
        await RegistrationState.username.set()
    else:
        # обновление данных в состоянии RegistrationState.username на message.text
        await state.update_data(username=message.text)
        # ожидание процедуры ввода email
        await message.answer("Введите свой email:")
        # ожидание ввода email в атрибут RegistrationState.email
        await RegistrationState.email.set()

# обработчик реагирует на состояние RegistrationState.email
@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    # обновление данных в состоянии RegistrationState.email на message.text
    await state.update_data(email=message.text)
    # ожидание процедуры ввода возраста
    await message.answer("Введите свой возраст:")
    # ожидание ввода возраста в атрибут RegistrationState.age
    await RegistrationState.age.set()

# обработчик реагирует на состояние RegistrationState.age
@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    # обновление данных в состоянии RegistrationState.age на message.text
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    # запись в таблицу User БД собранные данные при помощи crud-функции add_user
    add_user(user_data['username'], user_data['email'], user_data['age'])
    await message.answer(f"{user_data['username']} зарегистрирован")
    # завершение приёма состояния при помощи метода finish()
    await state.finish()

# обработчик перехвата любых сообщений
@dp.message_handler()
# функция перехвата сообщений
async def all_messages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    # запуск бота (dp - аргумент через что стартовать)
    executor.start_polling(dp, skip_updates=True)
