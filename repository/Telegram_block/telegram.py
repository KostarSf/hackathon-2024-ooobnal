import random

import telebot
import shutil
import io
import threading
import time
import requests
import sys
import os
import json


class TelegramBot:
    def __init__(self, master):
        print("START TELEGRAM HANDLER -> TELEGRAM")
        self.master = master
        self.init_variables()
        self.init_all_receivers()

    def init_variables(self):
        self.token                          = self.master.token
        self.stop_polling                   = threading.Event()

        self.bot = telebot.TeleBot(self.token, parse_mode='HTML')


    def _complex_init(self):
        self.message_handler = self.master.message_handler
        # self.commands_handler = self.master.commands_handler

    def print_d(self, *args):
        if self.master.debugging_mode:
            print(*args)

    def check_csv(self, chat_id, text):
        start_marker_phrase = "CSV START"
        end_marker_phrase = "CSV END"

        start_index = text.find(start_marker_phrase)
        end_index = text.find(end_marker_phrase)

        # base_folder = "./tmp"
        # sub_folder = os.path.join(base_folder, str(chat_id))
        # file_path = os.path.join(sub_folder, "table.csv")
        # os.makedirs(sub_folder, exist_ok=True)

        if start_index != -1 and end_index != -1 and start_index < end_index:
            start_line_start = text.rfind('\n', 0, start_index)
            end_line_end = text.find('\n', end_index)

            if start_line_start == -1:
                start_line_start = 0
            if end_line_end == -1:
                end_line_end = len(text)
            else:
                end_line_end += 1

            csv_content = text[start_index + len(start_marker_phrase):end_index].strip()

            csv_lines = [line for line in csv_content.splitlines() if line.strip() != "==="]
            csv_content_cleaned = "\n".join(csv_lines)

            file_like = io.BytesIO()
            file_like.write(csv_content_cleaned.encode('utf-8'))  # Кодируем текст в байты
            file_like.seek(0)  # Перемещаем указатель в начало файла

            # Отправляем файл пользователю
            self.bot.send_document(
                chat_id=chat_id,
                document=file_like,
                visible_file_name="talbe.csv",  # Указываем имя файла
                caption="Таблица с данными из файла"
            )

            cleaned_text = text[:start_line_start] + text[end_line_end:]
            cleaned_text = cleaned_text.strip()

            return cleaned_text

            # with open(file_path, "w", newline="", encoding="utf-8") as file:
            #     file.write(csv_content_cleaned + '\n')
            #
            # print(f"CSV-файл успешно создан по пути: {file_path}")
        else:
            print("Маркеры 'CSV START' и/или 'CSV END' не найдены.")
        #
        # lines = text.splitlines()
        # cleaned_text = "\n".join(line for line in lines if line.strip())
        #
        # if not cleaned_text:
        #     cleaned_text = "Я сформировал таблицу с данными"
        #     with open(file_path, 'rb') as file:
        #         self.bot.send_document(chat_id, file)
        #
        # if os.path.exists(sub_folder):
        #     shutil.rmtree(sub_folder)
        #     print(f"Папка {sub_folder} была удалена.")
        # else:
        #     print(f"Папка {sub_folder} не существует")

        return text

    ############ MESSAGE SEND ##############
    def send_message_users(self, chat_id_list, message_out):
        for chat_id in chat_id_list:
            self.master.telegram_anim.stop_animation(chat_id)
            if not self.master.test_mode:
                cleaned_text = self.check_csv(chat_id, message_out)
                splitted_message = [cleaned_text[i:i + 1000] for i in range(0, len(cleaned_text), 1000)]
                for chunk in splitted_message:
                    self.bot.send_message(chat_id, chunk, parse_mode=None)
            else:
                self.master.testing.send_message(chat_id, message_out, parse_mode=None)

    def send_and_get_message(self, chat_id, message_out):
        return self.bot.send_message(chat_id, message_out, parse_mode=None)

    def edit_message(self, message, message_out):
        self.bot.edit_message_text(message_out, message.chat.id, message.message_id)

    def message_del(self, message):
        self.bot.delete_message(message.chat.id, message.message_id)


    ########## MESSAGE RECEPTION ############

    def register_next_step_handler_by_chat_id(self, chat_id, register_func, *args):
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.register_next_step_handler_by_chat_id(chat_id, register_func, *args)

    def init_all_receivers(self):
        if not self.master.test_mode:
            # self.init_telegram_command_handler('users', self.show_users)
            # self.init_telegram_command_handler("user_tasks", self.show_user_tasks)
            # self.init_telegram_command_handler('tasks', self.show_tasks)
            self.init_telegram_handlers("text", self.handle_text_message)
            self.init_telegram_handlers("document", self.handle_file_message)

    def init_telegram_command_handler(self, commands_name, register_func):
        self.bot.message_handler(commands=[commands_name])(register_func)

    def init_telegram_handlers(self,content_types, register_func):
        self.bot.message_handler(content_types=[content_types])(register_func)

    def init_telegram_all_type_handler(self, register_func):
        self.bot.message_handler(func=lambda message: True)(register_func)


    ########## MESSAGE HANDLERS ############

    # def show_users(self, message):
    #     self.commands_handler.show_users(message)

    # def show_user_tasks(self, message):
    #     self.commands_handler.show_user_tasks(message)

    # def show_tasks(self, message):
    #     self.commands_handler.show_tasks(message)

    def handle_text_message(self, message):
        self.message_handler.handle_text_message(message)

    def handle_file_message(self, message):
        self.message_handler.handle_file_message(message, self.bot)

    ########## SYSTEM FUNCTIONS ############

    def check_if_already_running(self):
        pid_file = 'bot_pid.pid'
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        if os.path.isfile(pid_file):
            print("Bot is already running.")

    def cleanup(self):
        try:
            os.remove('bot_pid.pid')
        except OSError:
            pass

    def safe_polling(self):
        self.check_if_already_running()
        self.skip_old_messages()
        print("Bot running")
        while not self.stop_polling.is_set():
            try:
                self.bot.polling(non_stop=True)
            except requests.exceptions.ConnectionError:
                print("Connection error. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(5)
            finally:
                self.cleanup()

    def skip_old_messages(self):
        updates = self.bot.get_updates(offset= None, limit= 5, timeout=5, long_polling_timeout=2)
        if updates:
            last_update_id = updates[-1].update_id
            self.bot.get_updates(offset = last_update_id + 1,long_polling_timeout=2)
            print("Старые сообщения пропущены.")

    def start(self):
        print("START TELEGRAM HANDLER -> TELEGRAM (MAIN LOOP)")
        polling_thread = threading.Thread(target=self.safe_polling)
        polling_thread.daemon = True
        polling_thread.start()
        return polling_thread

    def stop(self):
        self.stop_polling.set()
        self.bot.stop_polling()
        print("STOP TELEGRAM HANDLER -> TELEGRAM (MAIN LOOP)")


