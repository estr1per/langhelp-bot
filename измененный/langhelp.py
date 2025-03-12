import telebot
from telebot import types
from googletrans import Translator
import random
import asyncio

TOKEN = '7941596774:AAHOEKXQOEE2iabX7m6u2llcvCm6izk7bnU'
bot = telebot.TeleBot(TOKEN)
user_langs = {}
practice_questions = {
    'en': [
        ('What is the capital of France?', 'Paris'),
        ('Какая третья форма глагола "see"?', 'seen'),
        ('Какой синоним слова "happy"?', 'cheerful'),
        ('Какая вторая форма глагола "try"?', 'tried'),
        ('Какая вторая форма "arrive"?', 'arrived')
    ],
    'fr': [
        ('Quelle est la capitale de la France?', 'Paris'),
        ('Comment s’appelle un chaton en français?', 'Chaton'),
        ('Quel est le plus grand océan sur Terre?', 'Océan Pacifique'),
        ('Combien de continents y a-t-il?', 'Sept')
    ],
    'es': [
        ('¿Cuál es la capital de Francia?', 'París'),
        ('¿Cómo se llama un gato pequeño en español?', 'Gatito'),
        ('¿Cuál es el océano más grande de la Tierra?', 'Océano Pacífico'),
        ('¿Cuántos continentes hay?', 'Siete')
    ],
}


@bot.message_handler(commands=['start'])
def start_message(message):
    langs = types.ReplyKeyboardMarkup(resize_keyboard=True)
    eng = types.KeyboardButton('English')
    frc = types.KeyboardButton('French')
    esp = types.KeyboardButton('Spanish')
    langs.add(eng, frc, esp)
    bot.send_message(message.chat.id, 'Привет, выбери язык', reply_markup=langs)


@bot.message_handler(func=lambda message: message.text in ['English', 'French', 'Spanish'])
def set_language(message):
    user_langs[message.chat.id] = {
        'English': 'en',
        'French': 'fr',
        'Spanish': 'es'
    }[message.text]
    bot.send_message(message.chat.id, f'Вы выбрали {message.text}! Что вы хотите делать?',
                     reply_markup=create_main_menu())


def create_main_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    translator_button = types.KeyboardButton('Использовать переводчик')
    practice_button = types.KeyboardButton('Получить тренировку языка')
    menu.add(translator_button, practice_button)
    return menu


def create_translate_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    repeat = types.KeyboardButton('Перевести еще раз')
    back = types.KeyboardButton('Вернуться в главное меню')
    menu.add(repeat, back)
    return menu


def create_continue_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    continue_button = types.KeyboardButton('Продолжить тренировку')
    stop_button = types.KeyboardButton('Закончить тренировку')
    menu.add(continue_button, stop_button)
    return menu


@bot.message_handler(func=lambda message: message.text == 'Использовать переводчик')
def use_translator(message):
    bot.send_message(message.chat.id, 'Пожалуйста, введите текст для перевода.')
    bot.register_next_step_handler(message, translate_text)


def translate_text(message):
    translator = Translator()
    user_lang = user_langs.get(message.chat.id, 'en')
    try:
        # В новых версиях googletrans.translate может быть корутиной, поэтому проверяем и вызываем asyncio.run, если нужно
        result = translator.translate(message.text, dest=user_lang)
        if asyncio.iscoroutine(result):
            result = asyncio.run(result)
        translated_text = result.text
        bot.send_message(message.chat.id, f'Переведенный текст: {translated_text}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при переводе.{str(e)} Пожалуйста, попробуйте еще раз.')

    bot.send_message(message.chat.id, 'Хотите перевести что-то еще или вернуться в главное меню?',
                     reply_markup=create_translate_menu())


@bot.message_handler(func=lambda message: message.text == 'Перевести еще раз')
def repeat_translation(message):
    bot.send_message(message.chat.id, 'Пожалуйста, введите текст для перевода.')
    bot.register_next_step_handler(message, translate_text)


@bot.message_handler(func=lambda message: message.text == 'Вернуться в главное меню')
def back_to_main_menu(message):
    bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: message.text == 'Получить тренировку языка')
def start_practice(message):
    if message.chat.id in user_langs:
        lang = user_langs[message.chat.id]
        question, answer = random.choice(practice_questions[lang])
        bot.send_message(message.chat.id, question)
        bot.register_next_step_handler(message, check_answer, answer)
    else:
        bot.send_message(message.chat.id, 'Сначала выберите язык с помощью команды /start.')

def check_answer(message, correct_answer):
    user_answer = message.text.strip().lower()
    expected_answer = correct_answer.strip().lower()
    if user_answer == expected_answer:
        bot.send_message(message.chat.id, 'Правильно!')
    else:
        bot.send_message(message.chat.id, f'Неправильно. Правильный ответ: {correct_answer}')
    bot.send_message(message.chat.id, 'Хотите продолжить тренировку или закончить?',
                     reply_markup=create_continue_menu())

@bot.message_handler(func=lambda message: message.text == 'Продолжить тренировку')
def continue_practice(message):
    if message.chat.id in user_langs:
        lang = user_langs[message.chat.id]
        question, answer = random.choice(practice_questions[lang])
        bot.send_message(message.chat.id, question)
        bot.register_next_step_handler(message, check_answer, answer)
    else:
        bot.send_message(message.chat.id, 'Сначала выберите язык с помощью команды /start.')

@bot.message_handler(func=lambda message: message.text == 'Закончить тренировку')
def stop_practice(message):
    bot.send_message(message.chat.id, 'Вы вернулись в главное меню.', reply_markup=create_main_menu())

if __name__ == '__main__':
    bot.polling(none_stop=True)
