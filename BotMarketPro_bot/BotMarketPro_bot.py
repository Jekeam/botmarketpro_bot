# coding: utf8
import telebot
import re
import config as prop
import time
import botan
from telebot import types
import db_utils as db


bot = telebot.TeleBot(prop.token)


# Определяем общие кнопки
btn_order_cancel = types.KeyboardButton(prop.btn_order_cancel) # Копка "отменить заказ"


# Команда CREATE_DB
@bot.message_handler(commands=['create_db'])
def create_db(message):
    db_worker = db.SQLighter(prop.db)
    db_worker.create_db()


# Команда START
@bot.message_handler(commands=['start'])
def cmd_start(message):
    db_worker = db.SQLighter(prop.db)
    db_worker.user_add(message)
    first_name = message.chat.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_order = types.KeyboardButton(prop.btn_make_order) # Копка оформить заказ
    btn_ask = types.KeyboardButton(prop.btn_ask_question) # Копка задать вопрос
    markup.add(btn_order)
    markup.add(btn_ask)
    bot.send_message(message.chat.id, prop.msg_hi.format(first_name), reply_markup=markup)
    botan.track(prop.botan_key, message.chat.id, message)


# Команда HELP
@bot.message_handler(commands=['help'])
def cmd_help(message):
    botan.track(prop.botan_key, message.chat.id, message, '/help')


#Команда SETTINGS
@bot.message_handler(commands=['settings'])
def cmd_settings(message):
    botan.track(prop.botan_key, message.chat.id, message, '/settings')


# Получаем от клиента описание заказа (вызвано из order_guide)
def get_order_desc(order_desc):
    print('Описание заказа: ' + order_desc)

def get_budget(message):
    botan.track(prop.botan_key, message.chat.id, message, prop.btn_skip)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
    btn_4k = types.KeyboardButton(prop.btn_4k)
    btn_10k = types.KeyboardButton(prop.btn_10k)
    btn_20k = types.KeyboardButton(prop.btn_20k)
    btn_30k = types.KeyboardButton(prop.btn_30k)
    keyboard.add(btn_4k, btn_10k)
    keyboard.add(btn_20k, btn_30k)
    keyboard.add(btn_order_cancel)
    bot.send_message(message.chat.id, prop.msg_budget, reply_markup = keyboard)


# Если сообщение не удалось обработать
def no_data_found(message):
    bot.reply_to(message, prop.msg_not_found)
    botan.track(prop.botan_key, message.chat.id, message, 'no_data_found')

# Если ненашли ничего!
@bot.message_handler(func=lambda message: True, content_types = ['text'])
def check_answer(message):
    msg_text = message.text
    chat_id = message.chat.id
    # нажал "оформить заказ"
    if msg_text == prop.btn_make_order:
        # Пожалуйста, введите краткое описание заказа
        markup = types.ForceReply()
        bot.send_message(chat_id, prop.msg_order_desc, reply_markup = markup)
        botan.track(prop.botan_key, chat_id, message, prop.btn_make_order)
    # нажал "отменить заказ"
    elif msg_text == prop.btn_order_cancel:
        bot.send_message(chat_id, prop.msg_order_cancel)
        botan.track(prop.botan_key, message.chat.id, message, prop.msg_order_cancel)
        cmd_start(message)        
    # ответ на ранее заданный вопрос, по описанию заказа
    elif message.reply_to_message and message.reply_to_message.text == prop.msg_order_desc:
        # Запишем описание заказа
        get_order_desc(message.text)
        # Добавим возможность выйти из режима оформления заказа
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        btn_order_telephone = types.KeyboardButton(prop.btn_phone, request_contact = True) # Копка "Предоставить телефон"
        btn_skip = types.KeyboardButton(prop.btn_skip) # Копка "Пропустить"
        keyboard.add(btn_order_telephone)
        keyboard.add(btn_skip)
        keyboard.add(btn_order_cancel)
        bot.send_message(chat_id, prop.msg_your_contact, reply_markup = keyboard)
    # нажали "Пропустить"
    elif msg_text == prop.btn_skip:
        get_budget(message)
    elif msg_text == prop.btn_phone:
        botan.track(prop.botan_key, message.chat.id, message, prop.btn_phone)
        print(str(message))
    else:
        print('no_data_found:' + msg_text)
        no_data_found(message)


# Получаем контакт клиента
@bot.message_handler(content_types = ['contact'])
def get_phone(message):
    # проверим что жалкий людишка не обманул нас, и не отправил левый телефон?
    if message.from_user.id == message.contact.user_id:
        print(str(message))
        get_budget(message)
    else:
        keyboard_confirm = types.ReplyKeyboardMarkup(resize_keyboard = True)
        btn_yes = types.KeyboardButton(prop.btn_yes) # Копка "Да"
        btn_no = types.KeyboardButton(prop.btn_no) # Копка "Нет"
        keyboard_confirm.add(btn_yes, btn_no)
        bot.send_message(message.chat.id,
                         prop.msg_confirm_phone.format(str(message.contact.phone_number)),
                         reply_markup = keyboard_confirm)
        print(str(message))
        get_budget(message)


# Запуск скрипта
if __name__ == '__main__':
    print('start')
    bot.polling(none_stop = True)