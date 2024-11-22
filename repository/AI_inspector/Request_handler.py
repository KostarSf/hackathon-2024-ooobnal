import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__)))

from Context_manipulator.preprocessing_module import PreprocessingModule
from repository.AI_inspector.Query_module.config_module import ConfigModule
from repository.AI_inspector.Cach_block.cache_module import Cache
from repository.AI_inspector.Error_handler.AI_error_handler import AI_error_handler

# mode_list = ["Normal", "VB", "Cache", "Generate", "Vectorization", "Init_file"]

import threading

class RequestHandler:
    def __init__(self, master):
        print("START REQUEST HANDLER")
        self.master         = master
        self.main_node      = self
        self.json_h         = self.master.json_h
        self.json_h.get_json_config(self, "main_ai_inspector_config")
        self.json_h.get_json_config(self, "AI_API_config")

        self.dict_system_states = {}

        self.config_m       = ConfigModule(self.master)
        self.preproc_m      = PreprocessingModule(self.master)
        self.local_error_h  = AI_error_handler(self.master)
        if self.cache_activate:
            self.cache = Cache(self.master)


    def _complex_init(self):
        self.config_m.main_node = self.main_node
        self.preproc_m.main_node = self.main_node
        self.local_error_h.main_node = self.main_node
        self.config_m._complex_init()
        self.preproc_m._complex_init()

    def start(self):
        self.preproc_m.start()
        self.config_m.start()

    def stop(self):
        self.preproc_m.stop()
        self.config_m.stop()

    def set_request_state(self, unique_flow_determinant, state):
        self.dict_system_states[unique_flow_determinant] = state

    def get_request_state(self, unique_flow_determinant):
        return self.dict_system_states[unique_flow_determinant]

    def main_entrance(self, conf_name, conf_data, mode, unique_flow_determinant = None):
        if not unique_flow_determinant:
            unique_flow_determinant = f"Thread_{self.get_id_thread()}"
        self.set_request_state(unique_flow_determinant, "Received")
        if mode == "Normal":
            return self.normal_entrance(conf_name, conf_data, unique_flow_determinant)
        elif mode == "VB":
            return self.vectorbase_entrance(conf_name, conf_data, unique_flow_determinant)
        elif mode == "Cache":
            return self.cache_entrance(conf_name, conf_data, unique_flow_determinant)
        elif mode == "Vectorization":
            return self.preproc_m.vectorize_entrance(conf_name, conf_data, unique_flow_determinant)
        elif mode == "Generate":
            pass
        elif mode == "Init_file":
            return self.preproc_m.initialize_file(conf_name, conf_data, unique_flow_determinant)
        # return self.preproc_m.vb.get_indexed_message_history(conf_data, self.preproc_m.count_tokens)

    def normal_entrance(self, conf_name, conf_data, unique_flow_determinant):
        if [message for message in conf_data if message["role"] == "file"]:
            print("Неверно указан режим сообщения. Запрос содержит объявление ")
            return self.vectorbase_entrance(conf_name, conf_data, unique_flow_determinant)
        conf_data = self.preproc_m.normal_entrance(conf_data, unique_flow_determinant)
        return self.get_answer(conf_name, conf_data, unique_flow_determinant)

    def vectorbase_entrance(self, conf_name, conf_data, unique_flow_determinant):
        if not [message for message in conf_data if message["role"] == "file"]:
            print("Обьявление файла в conf_data отсутствует. В запросе ожидалось объявление файла! Предупреждение входа VB!")
        conf_data = self.preproc_m.vectorbase_entrance(conf_data, unique_flow_determinant)
        return self.get_answer(conf_name, conf_data, unique_flow_determinant)

    def get_answer(self, conf_name, conf_data, unique_flow_determinant):
        answer = self.config_m.ai_handle(conf_name, conf_data, unique_flow_determinant)
        return answer

    def cache_entrance(self, conf_cache_mode, conf_data, unique_flow_determinant):
        if self.cache:
            answer = self.cache.main_entrance(conf_cache_mode, conf_data, self.main_entrance, unique_flow_determinant)
            return answer
        else:
            print("База Кеширования Запросов отклчена")
            return None


    def get_id_thread(self):
        thread_id = threading.current_thread().ident
        return thread_id
