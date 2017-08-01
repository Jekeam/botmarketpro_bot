# coding: utf8
import sqlite3
import config as prop


# объявим константы
T_USERS = 'users'
T_GUIDE = 'guide'
T_ORDERS = 'orders'
T_USER_COLUMNS = '(id, username, first_name, last_name, email, phone, language)'
T_GUIDE_COLUMNS = '(user_id, step)'
T_ORDERS_COLUMNS = '(user_id, chat_id, desc, price, dedline, phone, email)'


class SQLighter:

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        # self.cursor = self.connection.cursor()

    def create_db(self):
        # Создаем файл и таблицу юзеров
        conn = self.connection
        try:
            conn.execute('''create table ''' + T_USERS + '''(
                             id         int  primary key not null,
                             username   text not null,
                             first_name text,
                             last_name  text,
                             email      text,
                             phone      text,
                             language   text);
                        ''')
            print("Table " + T_USERS + " created successfully")
        except Exception as exc:
            print("Table created " + T_USERS + " fail: " + str(exc))
        # Создаем таблицу шагов юзера, чтоб знать без ебеней где он находится
        try:
            conn.execute('''create table ''' + T_GUIDE + '''(
                             user_id   int primary key not null,
                             step  int);
                        ''')
            print("Table created " + T_GUIDE + " successfully")
        except Exception as exc:
            print("Table created " + T_GUIDE + " fail: " + str(exc))
        # Создаем таблицу заказов        
        try:# статусы: 1-в процессе оформления / 2-готов / 3-в работе / 4-закрыт /-1 отменен
            conn.execute('''create table ''' + T_ORDERS + '''(
                             id integer primary key autoincrement,
                             status int not null,
                             user_id int not null,
                             chat_id int,
                             desc text,
                             price text,
                             dedline text,
                             phone text,
                             email text);
                        ''')
            print("Table " + T_ORDERS + " created successfully")
        except Exception as exc:
            print("Table created " + T_ORDERS + " fail: " + str(exc))
        conn.close()

    def user_add(self, message):
        # Добавление нового пользователя в БД
        if self.connection:
            user_id = str(message.from_user.id)
            username = str("'" + message.from_user.username + "'")
            first_name = str("'" + message.from_user.first_name + "'")
            last_name = str("'" + message.from_user.last_name + "'")
            language_code = str("'" + message.from_user.language_code + "'")
            if user_id:
                sql_text = "select id from " + T_USERS + " where id = " + user_id
                res = self.connection.execute(sql_text)
                for v_res in res:
                    return v_res[0]
                sql_text = "insert into " + T_USERS + T_USER_COLUMNS + "\
                            values (" + user_id + ", " + username + ", " + first_name + ", " + last_name + ", null, null, " + language_code + ")"
                self.connection.execute(sql_text)
                self.connection.commit()
                sql_text = "insert into " + T_GUIDE + T_GUIDE_COLUMNS + "\
                            values (" + user_id + ", '1')"
                self.connection.execute(sql_text)
                self.connection.commit()
                return user_id


    def set_order(self, user_id):
        sql_text = "insert into " + T_ORDERS + " (status, user_id)\
                    values ( 1, " + str(user_id) + ");"
        self.connection.execute(sql_text)
        self.connection.commit()
        sql_text = "select max(id) from " + T_ORDERS + " where status = 1 and user_id = " + str(user_id)
        order_id = self.connection.execute(sql_text)
        for v_res in order_id:
            return v_res[0]


    # получить заказ, кторый в процессе оформления
    def get_order(self, user_id):
        sql_text = "select max(id) from " + T_ORDERS + " where status = 1 and user_id = " + str(user_id)
        order_id = self.connection.execute(sql_text)
        for v_res in order_id:
            return v_res[0]


    def update_order(self, order_id, **kwargs):
        for key in kwargs:
            if key == 'desc':
                sql_text = "update " + T_ORDERS + " set desc = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            elif key == 'price':
                sql_text = "update " + T_ORDERS + " set price = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            elif key == 'dedline':
                sql_text = "update " + T_ORDERS + " set dedline = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            elif key == 'phone':
                sql_text = "update " + T_ORDERS + " set phone = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            elif key == 'email':
                sql_text = "update " + T_ORDERS + " set email = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            elif key == 'status':
                sql_text = "update " + T_ORDERS + " set status = '" + str(kwargs[key]) + "' \
                            where id = " + str(order_id) + ";"
            else:
                pass
                return
        self.connection.execute(sql_text)
        self.connection.commit()
        #self.connection.execute(sql_text)
        #self.connection.commit()


    def get_step(self, user_id):
        sql_text = "select step from " + T_GUIDE + " where user_id = " + str(user_id)
        res = self.connection.execute(sql_text)
        if res:
            for v_res in res:
                return str(v_res[0])
        sql_text = "insert into " + T_GUIDE + T_GUIDE_COLUMNS + "\
                    values (" + str(user_id) + ", '1')"
        self.connection.execute(sql_text)
        self.connection.commit()
        return(1)


    def step_update(self, user_id, step):
        sql_text = "update " + T_GUIDE + " set step = " + str(step) + "\
                    where user_id = " + str(user_id)
        self.connection.execute(sql_text)
        self.connection.commit()