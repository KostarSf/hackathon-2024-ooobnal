import sqlite3
import threading
from datetime import datetime
import queue

class Database:
    def __init__(self, master):
        print("INIT DATA BASE")
        self.master = master
        self.path = self.master.data_base_path
        self.name = self.master.data_base_name
        self.json_h = self.master.json_h

        self.command_queue = queue.Queue()
        # self.log_data_in_data_base = self.master.logger.data_base.log_locals_data
        #self.start()
        #self.rtf()
        #self.get_func()
        #print(self.check_trigger_1('Departments'))
        #self.create("Departments", ["eeeee"], 1111111)
        #self.update(1111, "Departments", 6, "parent_id", 2)
        #self.delete("Users", 3)

    def _complex_init(self):
        self.database = self.master.database

    def start(self):
        print('START DATA BASE')
        self.conn = sqlite3.connect(self.path+'\\'+self.name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.json_h.get_json_config(self, "db_config")
        self.create_tables()
        self.update_tables()
        # self.add_none_dep()
        self.create_functions()
        self.change_triggers()

        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True, name='tread_1')
        self.is_running = True
        self.worker_thread.start()

    def stop(self):
        self.is_running = False
        print("END DATA BASE")
        self.worker_thread.join()
        self.conn.close()

    def add_command(self, command, *args):
        result_queue = queue.Queue()
        self.command_queue.put((command, args, result_queue))
        res = result_queue.get()
        del result_queue
        return res

    def _process_queue(self):
        while self.is_running:
            try:
                command, args, result_queue = self.command_queue.get(timeout=2)
                result = command(*args)
                if result_queue:
                    result_queue.put(result)
                self.command_queue.task_done()
            except queue.Empty:
                pass

    def connect(self):
        return sqlite3.connect(self.path + "\\" + self.name)

    # def get_func(self):
    #     self.cursor.execute("SELECT name FROM sqlite_master WHERE type='function'")
    #     functions = self.cursor.fetchall()

    def create_functions(self):
        for table_name, columns in self.table.items():
            func_config = columns['functions']
            for func_name, func_param in func_config.items():
                f = getattr(self, func_param['path_to_func'])
                self.conn.create_function(func_name, func_param['n_of_parameters'], f)

        self.conn.commit()

    def check_trigger(self, table_name):
        query = """
        SELECT name, sql
        FROM sqlite_master
        WHERE tbl_name = ? AND type = 'trigger'
        """
        self.cursor.execute(query, (table_name,))
        table_info = {i[0]: i[1] for i in self.cursor.fetchall()}
        self.conn.commit()
        return table_info

    def get_query_trigger(self, table_name, trigger_name, trigger_condition, trigger_type, type_of_action, sql_statement):
        if trigger_condition:
            condition = f"WHEN {trigger_condition}"
        else:
            condition = 'FOR EACH ROW'
        query = f"""
            CREATE TRIGGER {trigger_name}
            {trigger_type} {type_of_action} ON {table_name}
            {condition}
            BEGIN
                {sql_statement}
            END;
            """
        return query

    def create_trigger(self, query):
        cursor = self.conn.cursor()
        """Создает триггер в SQLite3. !!!!!!!!!! IF NOT EXISTS !!!!!!!!!!!!
        Args:
            conn: Соединение с базой данных SQLite3.
            trigger_name: Имя триггера.
            table_name: Имя таблицы.
            trigger_type: Тип триггера (BEFORE, AFTER, INSTEAD OF).
            type_of_action: Тип операции (select, update, delete, insert)
            sql_statement: SQL-запрос, который будет выполняться триггером.
        """
        cursor.execute(query)
        self.conn.commit()

    def drop_trigger(self, trigger_name):
        """Удаляет триггер из SQLite3.

        Args:
            trigger_name: Имя триггера, который нужно удалить.
        """
        self.cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
        self.conn.commit()

    # def add_none_dep(self):
    #     row = self.deep_get(11111, "Departments", ["id"], "name = 'None'")
    #     if not row:
    #         self.deep_create("Departments", ['None'], 11111)
    #         self.id_none_dep = self.deep_get(11111, "Departments", ["id"], "name = 'None'")
    #     else:
    #         self.id_none_dep = row

    def update_tables(self):
        for i in self.table.items():
            col = list(set(i[1]['config']['no_important'].keys()) - set(self.get_table_column(i[0])))
            self.add_column(i[0], col)

    def add_column(self, name_tab, column):
        for col in column:
            type = self.table[name_tab]['config']['no_important'][col]['type']
            query = f'ALTER TABLE {name_tab} ADD {col} {type};'
            self.cursor.execute(query)
            self.conn.commit()

    def get_table_column(self, name):
        query = f"SELECT * FROM {name}"
        data = self.cursor.execute(query)
        column = [i[0] for i in data.description]
        return column

    def change_triggers(self):
        for table_name, columns in self.table.items():
            tab_inp_config = columns['triggers']
            trigger_in_db = self.check_trigger(table_name)
            for triger_name, triger_param in tab_inp_config.items():
                query = self.get_query_trigger(table_name, triger_name, triger_param['condition'], *triger_param['value'])
                if triger_name not in trigger_in_db.keys():
                    self.create_trigger(query)
                elif query != trigger_in_db[triger_name]:
                    self.drop_trigger(triger_name)
                    self.create_trigger(query)
            trigger_list_in_db = list(trigger_in_db.keys())
            trigger_list_in_js = list(tab_inp_config.keys())
            diff_list = list(set(trigger_list_in_db)-set(trigger_list_in_js))
            for del_trig in diff_list:
                self.drop_trigger(del_trig)

    def create_tables(self):
        create_table_statements = []
        for table_name, columns in self.table.items():
            columns_definition = "id INTEGER PRIMARY KEY"
            tab_inp_config = columns['config']['important']
            for column_name, column_conf in tab_inp_config.items():
                col_type = column_conf["type"]
                columns_definition += f", {column_name} {col_type}"
            create_table_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition});"
            create_table_statements.append(create_table_statement)

        full_script = "\n".join(create_table_statements)

        self.cursor.executescript(full_script)

        self.conn.commit()

    def create(self, tab_name, value, chat_id, repetitions=False):
        return self.add_command(self.deep_create, tab_name, value, chat_id, repetitions)

    def deep_create(self, tab_name, value, chat_id, repetitions=False):
        col_name_list = [col_dict for col_dict in self.table[tab_name]['config']['important']]
        if len(col_name_list) == len(value):
            col_name_str = ', '.join(col_name_list)
            q_str = ', '.join(['?'] * len(value))

            if self.deep_get(chat_id,tab_name,["id"],' AND '.join([f"{col} = {repr(val)}" for col, val in zip(col_name_list, value)])):
                if not repetitions: return

            query = f'INSERT INTO {tab_name} ({col_name_str}) VALUES ({q_str})'

            try:
                cursor = self.conn.cursor()
                cursor.execute(query, tuple(value))
                self.conn.commit()
                return_value = cursor.lastrowid
                # info = f"Запись {value} в таблицу {tab_name} успешно добавлена c id {return_value}"
                # self.log_data_in_data_base()
                return return_value
            except sqlite3.Error as e:
                print(f"Ошибка при добавлении!", e)


    def update(self, chat_id, tab_name, id, field_name, new_value):
        self.add_command(self.deep_update, chat_id, tab_name, id, field_name, new_value)

    def deep_update(self, chat_id, tab_name, id, field_name, new_value):
        valid_fields = self.get_table_column(tab_name)
        if field_name in valid_fields:
            query = f"UPDATE {tab_name} SET {field_name} = ? WHERE id = ?"
            try:
                # Создаем запрос для обновления поля
                cursor = self.conn.cursor()
                cursor.execute(query, (new_value, id))

                self.conn.commit()
                # info = f"Поле {field_name} таблицы {tab_name} успешно обновлено на {new_value}."
                # self.log_data_in_data_base()
            except sqlite3.Error as e:
                print(f"Ошибка при обновлении поля {field_name} таблицы {tab_name}: {e}")
        else:
            print(f"Поля {field_name} нет в {tab_name}")


    def delete(self, tab_name, id):
        self.add_command(self.deep_delete, tab_name, id)

    def deep_delete(self, tab_name, id):
        cursor = self.conn.cursor()
        cursor.execute(f'DELETE FROM {tab_name} WHERE id = ?', (id,))
        self.conn.commit()

    def get(self, chat_id, tab_name, column='*', predicate=''):
        return self.add_command(self.deep_get, chat_id, tab_name, column, predicate)

    def deep_get(self, chat_id, tab_name, column='*', predicate=''):
        col = ', '.join(column)
        query = f'SELECT {col} FROM {tab_name}'
        if predicate:
           query += f' WHERE {predicate}'
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            raw = cursor.fetchall()

            if len(raw) == 1 and len(raw[0]) == 1:
                return_value = raw[0][0]
            else:
                return_value = raw
            # self.log_data_in_data_base()
            return return_value
        except sqlite3.Error as e:
            print(f"Ошибка при получении!", e)
            return []

    def get_id(self,chat_id,table_name, predicate_value):
        return self.add_command(self.deep_get_id, chat_id,table_name, predicate_value)

    def deep_get_id(self,chat_id, table_name, predicate_value):
        if table_name == "Tasks":
            predicate = f"creator_user_id = {predicate_value}"
        elif table_name == "Departments":
            predicate = f"name = {predicate_value}"
        else:
            predicate = f"user_id = {predicate_value}"
        return self.deep_get(chat_id, table_name, ["id"], predicate)

    def get_table(self, table_names, user_id):
        return self.add_command(self.deep_get_table, table_names, user_id)

    def deep_get_table(self, table_names, user_id):
        # Список для хранения частей запроса
        columns = {}
        join = []
        user_column_name = 'user_id'

        # Получаем имена столбцов для каждой таблицы

        for tab_name in table_names:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({tab_name})")
            table_info = cursor.fetchall()
            columns[tab_name] = [f"{tab_name}.{col[1]}" for col in table_info]

        # Формируем список столбцов для SELECT
        select_columns = [col for cols in columns.values() for col in cols]
        if select_columns == []:
            return None, None
        # Генерируем JOIN часть запроса, начиная со второй таблицы
        for i in range(1, len(table_names)):
            tab_name = table_names[i]
            previous_tab_name = table_names[i - 1]
            if tab_name == 'Tasks':
                join_condition = f"{previous_tab_name}.{user_column_name} = {tab_name}.create_user_id"
            else:
                join_condition = f"{previous_tab_name}.{user_column_name} = {tab_name}.{user_column_name}"
            join.append(f'JOIN {tab_name} ON {join_condition}')

        # Формируем основной SQL-запрос
        query = 'SELECT ' + ', '.join(select_columns) + ' FROM ' + table_names[0] + ' '
        if join:
            query += ' '.join(join)

        # Добавляем условие WHERE для фильтрации по user_id
        if table_names[0] == 'Tasks':
            query += f' WHERE {table_names[0]}.creator_user_id = {user_id}'
        else:
            query += f' WHERE {table_names[0]}.user_id = {user_id}'

        #print(request)

        # Выполняем запрос к базе данных
        cursor = self.conn.cursor()
        cursor.execute(query)
        body = cursor.fetchall()
        # self.log_data_in_data_base()

        # Возвращаем результат и реальные имена столбцов
        return body, select_columns

    def execute_sql(self, chat_id, query):
        return self.add_command(self.deep_execute_sql, chat_id, query)

    def deep_execute_sql(self, chat_id, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()

            # self.log_data_in_data_base()

            try:
                result = cursor.fetchall()
                return result
            except:
                pass
        except Exception as e:
            print(f"Ошибка выполнения запроса", e)
            return 'error'

    # def print_t(self):
    #     print(11111111111111111111111111)

    def display_table(self, table_name):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Выводим заголовки столбцов
        column_names = [description[0] for description in cursor.description]
        print(" | ".join(column_names))
        print("-" * (len(column_names) * 15))

        # Выводим данные
        for row in rows:
            print(" | ".join(map(str, row)))



if __name__ == '__main__':
    pass