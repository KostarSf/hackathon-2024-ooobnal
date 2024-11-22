from io import BytesIO
import time
class Distribution:

    def __init__(self, master):
        self.master = master

    def _complex_init(self):
        self.message_handler = self.master.message_handler
        self.request_handler = self.master.request_handler
        self.database = self.master.database

    def message(self, chat_id, user_id, message_text):
        answer = self.request_handler.main_entrance("main",
                                                    [{"role": "user", "content": message_text}],
                                                    "Normal",
                                                    str(chat_id))
        last_id = self.database.create("chat_history", [chat_id, user_id], chat_id, True)
        self.database.update(chat_id,"chat_history", last_id, "txt_mes", message_text)
        self.database.update(chat_id,"chat_history", last_id, "role", "user")

        last_id = self.database.create("chat_history", [chat_id, user_id], chat_id, True)
        self.database.update(chat_id, "chat_history", last_id, "txt_mes", answer["data"])
        self.database.update(chat_id, "chat_history", last_id, "role", "system")

        if answer["status"] == "successfully":
            self.message_handler.send_message_user(chat_id, answer["data"])
        else:
            print("Ошбика обработки", answer)
            self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")


    def file_handler(self, chat_id,file_base_name,file_type,downloaded_file):

        file_init_label = self.request_handler.main_entrance("file",
                                                          {"index_name": file_base_name, "file_type": file_type,
                                                           "file": BytesIO(downloaded_file)}, "Init_file", str(chat_id))
        print("Файл инициализирован")

    def loop_waiting(self, file_init_label):
        while True:
            try:
                label = file_init_label.get_nowait()
                if label == 'successfully':
                    return False
            except:
                time.sleep(1)
    def file_text_handler(self, chat_id,text,file_base_name,file_type,downloaded_file):

        file_init_label = self.request_handler.main_entrance("file",
                                                             {"index_name": file_base_name, "file_type": file_type,
                                                              "file": BytesIO(downloaded_file)}, "Init_file",
                                                             str(chat_id))

        self.loop_waiting(file_init_label)

        answer = self.request_handler.main_entrance("main", [{"role": "file", "content": f"Содержание файла: file::{file_base_name}::file\n", "indexing": True, "weight": 0.5}, {"role": "user", "content": text}], "VB", str(chat_id))

        if answer["status"] == "successfully":
            self.message_handler.send_message_user(chat_id, answer["data"])
        else:
            print("Ошибка обработки", answer)
            self.message_handler.send_message_user(chat_id, "Я почему-то сломался(\nПопробуйте написать позже.")


