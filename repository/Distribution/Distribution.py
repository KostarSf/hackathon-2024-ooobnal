from io import BytesIO
import time
import random


class Distribution:

    def __init__(self, master):
        self.master = master

    def _complex_init(self):
        self.message_handler = self.master.message_handler
        self.request_handler = self.master.request_handler
        self.database = self.master.database

    def message(self, chat_id, user_id, message_text):
        messages = self.get_chat_messages(chat_id)
        if not messages:
            self.message_handler.send_message_user(chat_id, "Перед выполнением запроса, пожалуйста, отправьте файл")
            return

        messages.append({"role": "user", "content": message_text})

        answer = self.request_handler.main_entrance("main", messages, "VB", str(chat_id))

        if answer["status"] == "successfully":
            self.add_chat_message(chat_id, user_id, "user", message_text)
            self.add_chat_message(chat_id, user_id, "assistant", answer["data"])
            self.message_handler.send_message_user(chat_id, answer["data"])
        else:
            print("Ошибка обработки", answer)
            self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")

    def get_chat_messages(self, chat_id):
        raw_history = self.database.get(chat_id, "chat_history", "*", f"chat_id = {chat_id}")
        context = []
        for row in raw_history:
            role = row[3]
            content = row[4]
            if role != "file":
                context.append({"role": role, "content": content})
            else:
                context.append({"role": role, "content": f"Содержание файла: file::{content}::file\n", "indexing": True, "weight": 0.5})

        return context

    def clear_chat_context(self, chat_id, user_id):
        self.database.execute_sql(chat_id, f"DELETE FROM chat_history WHERE chat_id = {chat_id}")
        self.add_chat_message(chat_id, user_id, "system", self.get_ai_rules())

    def add_chat_message(self, chat_id, user_id, role, txt_mes):
        last_id = self.database.create("chat_history", [chat_id, user_id], chat_id, True)
        self.database.update(chat_id, "chat_history", last_id, "txt_mes", txt_mes)
        self.database.update(chat_id, "chat_history", last_id, "role", role)

    def file_handler(self, chat_id, user_id, file_base_name, file_type, downloaded_file):
        try:
            unique_file_name = self.create_unique_file_name(file_base_name)
            file_init_label = self.request_handler.main_entrance(
                "file",
                {
                    "index_name": unique_file_name,
                    "file_type": file_type,
                    "file": BytesIO(downloaded_file)
                },
                "Init_file",
                str(chat_id))

            self.loop_waiting(file_init_label)
            print("Файл инициализирован")

            self.clear_chat_context(chat_id, user_id)
            self.add_chat_message(chat_id, user_id, "file", unique_file_name)

            messages = self.get_chat_messages(chat_id)

            answer = self.request_handler.main_entrance("main", messages, "VB", str(chat_id))

            if answer["status"] == "successfully":
                self.add_chat_message(chat_id, user_id, "assistant", answer["data"])
                self.message_handler.send_message_user(chat_id, answer["data"])
            else:
                print("Ошибка обработки", answer)
                self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")
        except:
            self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")

    def create_unique_file_name(self, file_base_name):
        return ''.join(random.choices('0123456789abcdef', k=16))

    def loop_waiting(self, file_init_label):
        while True:
            try:
                label = file_init_label.get_nowait()
                if label == 'successfully':
                    return False
            except:
                time.sleep(1)

    def get_ai_rules(self):
        return "Тебе предоставлен файл. Предоставь краткую сводку об информации, находящейся в нем, если содержание файла удовлетворяет следующим правилам. "\
                "Если не удается получить информацию из этого файла, не предоставляй краткую сводку, откажись выполнять последующие запросы и сообщи пользователю о недоступности данных. "\
                "Если файл не касается темы клинических заболеваний, диагнозов или медицины, откажись обрабатывать запрос и сообщи об этом пользователю. "\
                "Если пользователь задал вопрос, отвечай только в том случае, если этот вопрос напрямую касается "\
                "содержимого данного файла, а также относитя к тематике медицины. В противном случае сообщи о невозможности ответа пользователю. "\
                "При ответе пользователю следуй следующим правилам: "\
                "Если пользователь хочет выполнить какую-либо обработку данных из файла (например, попросит создать таблицу с диагнозами), "\
                "выполни этот запрос и удостоверься, что при этом используются только данные из предоставленного файла."\
                "если файл не текстовый, либо не в формате PDF, игнорируй его и сообщи об этом пользователю. "\
                "Если файл очень короткий, либо из него не удается выделить основную тему, игнорируй его и сообщи об этом пользователю. "\
                "Отвечай только на вопросы, связанные конкретно с данным файлом, либо на запросы, связанные с обработкой данных из этого файла. "\
                "Если запрос нерелевантен, игнорируй его и сообщи об этом пользователю."

    def file_text_handler(self, chat_id, user_id, text, file_base_name, file_type, downloaded_file):
        unique_file_name = self.create_unique_file_name(file_base_name)
        file_init_label = self.request_handler.main_entrance(
            "file",
            {
                "index_name": unique_file_name,
                "file_type": file_type,
                "file": BytesIO(downloaded_file)
            },
            "Init_file",
            str(chat_id))

        self.loop_waiting(file_init_label)

        self.clear_chat_context(chat_id, user_id)
        self.add_chat_message(chat_id, user_id, "file", unique_file_name)
        self.add_chat_message(chat_id, user_id, "user", text)

        chat_context = self.get_chat_messages(chat_id)

        answer = self.request_handler.main_entrance("main", chat_context, "VB", str(chat_id))

        if answer["status"] == "successfully":
            self.add_chat_message(chat_id, user_id, "assistant", answer["data"])
            self.message_handler.send_message_user(chat_id, answer["data"])
        else:
            print("Ошибка обработки", answer)
            self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")
