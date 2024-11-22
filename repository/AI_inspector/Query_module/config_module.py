
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

import importlib

from return_handler             import ReturnHandler

from API_OpenAI                 import API
from API_Local_LLM_llama_cpp    import API

class ConfigModule:
    def __init__(self, master):
        print("START REQUEST HANDLER -> CONFIG HANDLER")
        self.master = master
        self.return_handler = ReturnHandler(self.master)

        self.json_h = self.master.json_h
        self.json_h.get_json_config(self, "AI_settings_config")
        self.json_h.get_json_config(self, "AI_instruction_config")


    def _complex_init(self):
        self.module_name               = self.main_node.init_module_API
        class_name                     = self.main_node.init_class_API
        module                         = importlib.import_module(self.module_name)
        api_class                      = getattr(module, class_name)
        self.API                       = api_class(self.master)

        self.return_handler.main_node = self.main_node
        self.API.main_node            = self.main_node
        self.API._complex_init()

    def start(self):
        if self.module_name == "API_Local_LLM_llama_cpp":
            self.API.start()

    def stop(self):
        if self.module_name == "API_Local_LLM_llama_cpp":
            self.API.stop()

    def ai_handle(self, conf_name, messages_history, unique_flow_determinant):
        instr_config = self.instruction_config.get(conf_name)
        if not instr_config:
            raise Exception(f"Имя конфигурации: {conf_name} не обнаружено")

        prompt_config = self.settings_model_config.get(instr_config["inspector_name"])
        if not prompt_config:
            inst_cfg = instr_config["inspector_name"]
            raise Exception(f"Неправильно сформирован конфиг: {inst_cfg} не найдено")

        model_name = prompt_config["model_name"]
        instruction = instr_config["instruction"]
        return_func = prompt_config["return_func"]

        full_messages_history = self.get_messages_history(instruction, messages_history)
        self.main_node.set_request_state(unique_flow_determinant, "Gen Response")
        result = self.API.query_handler(model_name, full_messages_history)
        self.main_node.set_request_state(unique_flow_determinant, "End Processing")
        return self.return_handler.func_return_manager(return_func, result)

    def get_messages_history(self, instruction, messages_history):
        full_messages_history = [{"role": "system", "content": instruction}]
        for message in messages_history:
            if message["role"] == "file":
                full_messages_history.append({"role": "system", "content": message["content"]})
            else:
                full_messages_history.append({"role": message["role"], "content": message["content"]})
        return full_messages_history

