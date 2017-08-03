# coding: utf8
import telebot
import re
import config as prop
import time
# import botan
from telebot import types
import db_utils as db
import re
import datetime
from telegramcalendar import create_calendar

bot = telebot.TeleBot(prop.token)
current_shown_dates = {}


# Определяем общие кнопки
btn_order_cancel = types.KeyboardButton(prop.btn_order_cancel) # Копка "отменить заказ"


# Команда CREATE_DB
@bot.message_handler(commands=['create_db'])
def create_db(message):
    db_worker = db.SQLighter(prop.db)
    db_worker.create_db()


def first_btn(message):
    first_name = message.chat.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_order = types.KeyboardButton(prop.btn_make_order) # Копка оформить заказ
    btn_ask = types.KeyboardButton(prop.btn_ask_question) # Копка задать вопрос
    btn_about = types.KeyboardButton(prop.btn_about) # Копка задать вопрос
    markup.add(btn_order)
    markup.add(btn_ask)
    markup.add(btn_about)
    bot.send_message(message.chat.id, prop.msg_hi.format(first_name), reply_markup=markup)


# Команда START
@bot.message_handler(commands=['start'])
def cmd_start(message):
    db_worker = db.SQLighter(prop.db)
    user_id = db_worker.user_add(message)
    first_btn(message)
    # db_worker.step_update(user_id, 2)
    # botan.track(prop.# botan_key, message.chat.id, message)


# Команда HELP
@bot.message_handler(commands=['help'])
def cmd_help(message):
    # botan.track(prop.# botan_key, message.chat.id, message, '/help')
    pass


#Команда SETTINGS
@bot.message_handler(commands=['settings'])
def cmd_settings(message):
    # botan.track(prop.# botan_key, message.chat.id, message, '/settings')
    pass

def send_order(order_id):
    db_worker = db.SQLighter(prop.db)
    if order_id:
        text = db_worker.get_fill_order(order_id)
        return text

@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month > 12:
            month = 1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year,month)
        bot.edit_message_text("Пожалйста, выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month-=1
        if month < 1:
            month = 12
            year-=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year,month)
        bot.edit_message_text("Пожалйста, выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    db_worker = db.SQLighter(prop.db)
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day = call.data[13:]
        date = datetime.datetime(int(saved_date[0]),int(saved_date[1]),int(day),0,0,0)
        bot.send_message(chat_id, 'Крайник срок:' + str(date.strftime('%d.%m.%Y')))
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Дата выбрана")
        db_worker = db.SQLighter(prop.db)
        order_id = db_worker.get_order(user_id)
        if order_id:
            text = db_worker.get_fill_order(order_id)
            db_worker.update_order(order_id, dedline = str(date.strftime('%d.%m.%Y')))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_order = types.KeyboardButton(prop.btn_make_order) # Копка оформить заказ
            btn_ask = types.KeyboardButton(prop.btn_ask_question) # Копка задать вопрос
            btn_about = types.KeyboardButton(prop.btn_about) # Копка задать вопрос
            markup.add(btn_order)
            markup.add(btn_ask)
            markup.add(btn_about)
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        #Do something to inform of the error
        pass


@bot.message_handler(commands=['calendar'])
def get_calendar(message):
    now = datetime.datetime.now() #Текущая дата
    chat_id = message.chat.id
    date = (now.year,now.month)
    current_shown_dates[chat_id] = date #Сохраним текущую дату в словарь
    markup = create_calendar(now.year,now.month)
    bot.send_message(message.chat.id, "Пожалйста, выберите дату", reply_markup=markup)


# Получаем от клиента описание заказа (вызвано из order_guide)
def get_order_desc(order_id, order_desc):
    db_worker = db.SQLighter(prop.db)
    if order_id:
        db_worker.update_order(order_id, desc = order_desc)

def get_budget(message):
    db_worker = db.SQLighter(prop.db)
    # botan.track(prop.# botan_key, message.chat.id, message, prop.btn_skip)
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
    # botan.track(prop.# botan_key, message.chat.id, message, 'no_data_found')


# Добавим укажите ваш Email
def set_your_deadline(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
    btn_deadline = types.KeyboardButton(prop.btn_deadline) # Копка "Предоставить телефон"
    btn_deadline_not = types.KeyboardButton(prop.btn_deadline_not) # Копка "Пропустить"
    keyboard.add(btn_deadline)
    keyboard.add(btn_deadline_not)
    keyboard.add(btn_order_cancel)
    bot.send_message(chat_id, prop.msg_deadline, reply_markup = keyboard)

# Если ненашли ничего!
@bot.message_handler(func=lambda message: True, content_types = ['text'])
def check_answer(message):
    db_worker = db.SQLighter(prop.db)
    msg_text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id
    order_id = db_worker.get_order(user_id)
    msg_text_rep = ''
    if message.reply_to_message:
        msg_text_rep = message.reply_to_message.text
    # step = db_worker.get_step(user_id)
    # нажал "оформить заказ"
    if msg_text == prop.btn_make_order:
        # Пожалуйста, введите краткое описание заказа
        order_id = db_worker.set_order(user_id)
        markup = types.ForceReply()
        bot.send_message(chat_id, prop.msg_order_desc, reply_markup = markup)
        # botan.track(prop.# botan_key, chat_id, message, prop.btn_make_order)
    # нажал "отменить заказ"
    elif msg_text == prop.btn_order_cancel:
        bot.send_message(chat_id, prop.msg_order_cancel)
        if order_id:
            db_worker.update_order(order_id, status = -1)
        cmd_start(message)
        # botan.track(prop.# botan_key, message.chat.id, message,
        # prop.msg_order_cancel)
    # ответ на ранее заданный вопрос, по описанию заказа
    elif message.reply_to_message and message.reply_to_message.text == prop.msg_order_desc:
        # Запишем описание заказа
        if order_id:
            get_order_desc(order_id, message.text)
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
    # нажали да и подтвердили номер
    elif msg_text == prop.btn_yes:
        get_budget(message)
    # нажали нет и запросить номер повторно
    elif msg_text == prop.btn_yes:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        btn_order_telephone = types.KeyboardButton(prop.btn_phone, request_contact = True) # Копка "Предоставить телефон"
        btn_skip = types.KeyboardButton(prop.btn_skip) # Копка "Пропустить"
        keyboard.add(btn_order_telephone)
        keyboard.add(btn_skip)
        keyboard.add(btn_order_cancel)
        bot.send_message(chat_id, prop.msg_your_contact, reply_markup = keyboard)
    # запись бюджта / запрос eмeйла
    elif msg_text.isdigit() or msg_text in [prop.btn_4k, prop.btn_10k, prop.btn_20k, prop.btn_30k]:
        if order_id:
            db_worker.update_order(order_id, price = ''.join(re.findall(r'\d+', msg_text)))
            # Добавим укажите ваш Email
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            btn_email = types.KeyboardButton(prop.btn_email) # Копка "Предоставить телефон"
            btn_skip_email = types.KeyboardButton(prop.btn_skip_email) # Копка "Пропустить"
            keyboard.add(btn_email)
            keyboard.add(btn_skip_email)
            keyboard.add(btn_order_cancel)
            bot.send_message(chat_id, prop.msg_order_email, reply_markup = keyboard)
    # выбрали указать еМайл
    elif msg_text == prop.btn_email:
        # Пожалуйста, введите ваш email
        markup = types.ForceReply()
        bot.send_message(chat_id, prop.msg_order_email, reply_markup = markup)
    # ответ на ранее заданный вопрос, по емейлу
    elif message.reply_to_message and \
        (msg_text_rep == prop.msg_order_email or msg_text_rep == prop.msg_order_email_rep):
        if re.match('[^@]+@[^@]+\.[^@]+', msg_text):
            db_worker.update_order(order_id, email = msg_text)
            # добавим укажите ваш дедлайн
            set_your_deadline(chat_id)
        else:
            # Пожалуйста, введите ваш email ЕЩЕ РАЗОЧЕК ДРУЖЕ
            markup = types.ForceReply()
            bot.send_message(chat_id, prop.msg_order_email_rep, reply_markup = markup)
    elif msg_text == prop.btn_skip_email:
        # добавим укажите ваш дедлайн
        set_your_deadline(chat_id)
    # Нажали указать крайний срок
    elif msg_text == prop.btn_deadline:
        get_calendar(message)
    # Нажали нет срочности
    elif msg_text == prop.btn_deadline_not:
        order_id = db_worker.get_order(user_id)
        if order_id:
            text = db_worker.get_fill_order(order_id)
            markup = types.ReplyKeyboardRemove()
            first_name = message.chat.first_name
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_order = types.KeyboardButton(prop.btn_make_order) # Копка оформить заказ
            btn_ask = types.KeyboardButton(prop.btn_ask_question) # Копка задать вопрос
            btn_about = types.KeyboardButton(prop.btn_about) # Копка задать вопрос
            markup.add(btn_order)
            markup.add(btn_ask)
            markup.add(btn_about)
            bot.send_message(message.chat.id, text, reply_markup=markup)
    elif msg_text == prop.btn_about:
        markup = types.InlineKeyboardMarkup()
        btn_my_site = types.InlineKeyboardButton(text='Наш сайт', url='https://BotMarket.Pro') # Копка "наш сайт"
        markup.add(btn_my_site)
        bot.send_message(chat_id, "Нажми на кнопку и перейди на наш сайт.", reply_markup=markup)
    elif msg_text == prop.btn_ask_question:
        markup = types.ForceReply()
        bot.send_message(chat_id, prop.btn_ask_question_text, reply_markup = markup)
    else:
        print('no_data_found:' + msg_text)
        no_data_found(message)


# Получаем контакт клиента
@bot.message_handler(content_types = ['contact'])
def get_phone(message):
    # проверим что жалкий людишка не обманул нас, и не отправил левый телефон?
    db_worker = db.SQLighter(prop.db)
    user_id = message.from_user.id
    order_id = db_worker.get_order(user_id)
    if user_id == message.contact.user_id:
        if order_id:
            db_worker.update_order(order_id, phone = message.contact.phone_number)
        get_budget(message)
    else:
        if order_id:
            db_worker.update_order(order_id, phone = message.contact.phone_number)
        keyboard_confirm = types.ReplyKeyboardMarkup(resize_keyboard = True)
        btn_yes = types.KeyboardButton(prop.btn_yes) # Кнопка "Да"
        btn_no = types.KeyboardButton(prop.btn_no) # Кнопка "Нет"
        keyboard_confirm.add(btn_yes, btn_no)
        bot.send_message(message.chat.id,
                         prop.msg_confirm_phone.format(str(message.contact.phone_number)),
                         reply_markup = keyboard_confirm)


# Запуск скрипта
if __name__ == '__main__':
    print('start')
    bot.polling(none_stop = True)