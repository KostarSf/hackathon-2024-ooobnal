import os
import sys

from repository.Telegram_block.waiting_display import TelegramAnimation

sys.path.append(os.path.join(os.path.dirname(__file__)))

from repository.Telegram_block.telegram import TelegramBot
from repository.Json_block.json_handler import JsonHandler
from repository.Message_block.message_handler import MessageHandler
from repository.Distribution.Distribution import Distribution
from repository.AI_inspector.Request_handler import RequestHandler
from repository.database_sqlite.database import Database

class Master:
    def __init__(self, mode):
        print("START MASTER")
        self.mode = mode
        print(self.mode)
        self.init_modules()
        self.init_modules_complex()
        self.start_modules()
        self.main_loop()
        self.stop_modules()
        print("STOP MASTER")

    def init_modules(self):
        self.json_h = JsonHandler(self)
        self.telegram = TelegramBot(self)
        self.message_handler = MessageHandler(self)
        self.distribution = Distribution(self)
        self.request_handler = RequestHandler(self)
        self.database = Database(self)
        self.telegram_anim = TelegramAnimation(self)

    def init_modules_complex(self):
        self.telegram._complex_init()
        self.message_handler._complex_init()
        self.distribution._complex_init()
        self.request_handler._complex_init()
        self.database._complex_init()
        self.telegram_anim._complex_init()


    def start_modules(self):
        self.telegram.start()
        self.json_h.start()
        self.request_handler.start()
        self.database.start()
        self.telegram_anim.start()

    def main_loop(self):
        self.is_work = True
        while self.is_work:
            command = input()
            if command == "stop":
                self.is_work = False

    def stop_modules(self):
        self.telegram.stop()
        self.json_h.stop()
        self.request_handler.stop()
        self.database.stop()
        self.telegram_anim.stop()