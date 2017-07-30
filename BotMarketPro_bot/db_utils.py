# coding: utf8
import sqlite3
import config as prop


# объявим константы
T_USERS = 'users'
T_GUIDE = 'guide'
T_USER_COLUMNS = '(id, username, first_name, last_name, email, phone, language)'


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
                             cur_step  int,
                             next_step int,
                             back_step int);
                        ''')
            print("Table created " + T_GUIDE + " successfully")
        except Exception as exc:
            print("Table created " + T_GUIDE + " fail: " + str(exc))
        conn.close()

    def user_add(self, message):
        # Добавление нового пользователя в БД
        if self.connection:
            user_id = str(message.from_user.id)
            username = str("'"+message.from_user.username+"'")
            first_name = str("'"+message.from_user.first_name+"'")
            last_name = str("'"+message.from_user.last_name+"'")
            language_code = str("'"+message.from_user.language_code+"'")
            if user_id:
                sql_text = "select id from "+T_USERS+" where id = "+user_id
                print(sql_text)
                res = self.connection.execute(sql_text)
                for v_res in res:
                    print('Юзер в базе ' + str(v_res))
                    return
                sql_text = "insert into " + T_USERS + T_USER_COLUMNS +"\
                            values (" + user_id + ", " + username + ", " + first_name + ", " + last_name + ", null, null, " + language_code + ") "
                print(sql_text)
                self.connection.execute(sql_text);
                self.connection.commit()