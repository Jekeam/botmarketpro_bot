# coding: utf8
import telebot
import re
from telebot import types
import config as app
import time


bot = telebot.TeleBot(app.token)


#Команда START
@bot.message_handler(commands=['start','reset'])
def cmd_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_order = types.KeyboardButton(app.btn_make_order) # Копка оформить заказ
    btn_ask = types.KeyboardButton(app.btn_ask_question) # Копка задать вопрос
    markup.add(btn_order, btn_ask)
    bot.send_message(message.chat.id, app.msg_hi, reply_markup=markup)


# Если ненашли ничего!
@bot.message_handler(func=lambda message: True)
def cmd_start(message):
    bot.reply_to(message, app.msg_not_found)
    

# Запуск скрипта
if __name__ == '__main__':
    print('start')
    bot.polling(none_stop=True)