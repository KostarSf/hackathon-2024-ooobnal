import asyncio

import time
import threading

class TelegramAnimation:
    def __init__(self, master):
        print("START TELEGRAM HANDLER -> TELEGRAM ANIMATION")
        self.master     = master

        self.active_animations = dict()

    def _complex_init(self):
        self.telegram = self.master.telegram

    def start(self):
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True, name='tread_1')
        self.is_running = True
        print("START TELEGRAM HANDLER -> TELEGRAM ANIMATION(ANIMATION LOOP)")
        self.worker_thread.start()

    def stop(self):
        self.stop_all()
        print("STOP TELEGRAM HANDLER -> TELEGRAM ANIMATION(ANIMATION LOOP)")
        self.worker_thread.join()

    def set_animation(self, chat_id, base_message="Подождите секунду", animation_dict = ["", ".", "..", "..."], time_change = 1):
        """Запускает анимацию для указанного chat_id с дополнительным сообщением."""
        if chat_id in self.active_animations:
            self.telegram.message_del(self.active_animations[chat_id][0])
        message = self.telegram.send_and_get_message(chat_id, base_message)
        self.active_animations[chat_id] = (message, 0, base_message, animation_dict, time_change)

    def stop_animation(self, chat_id):
        """Останавливает анимацию для указанного chat_id."""
        if chat_id in self.active_animations:
            message, _, _, _, _ = self.active_animations.pop(chat_id)
            self.telegram.message_del(message)

    def _process_queue(self):
        print("PROCESS QUEUE")
        """Основной цикл анимации, выполняемый в единственном потоке."""
        while self.is_running:
            for chat_id, (message, wait_time, base_message, animation_dict, time_change) in list(self.active_animations.items()):
                try:
                    self.active_animations[chat_id] = (message, wait_time + 1, base_message, animation_dict, time_change)
                    full_message = self.get_animation(base_message, wait_time, animation_dict, time_change)
                    self.telegram.edit_message(message, full_message)
                except:
                    pass
            time.sleep(1)

    def get_animation(self, base_message, wait_time, animation_dict, time_change):
        curr_time = wait_time // time_change
        anim_s = animation_dict[(curr_time % len(animation_dict))]
        full_message = f"{base_message}{anim_s}"
        return full_message

    def stop_all(self):
        """Останавливает анимацию для всех пользователей и завершает цикл."""
        self.is_running = False
        for chat_id in list(self.active_animations.keys()):
            self.stop_animation(chat_id)
