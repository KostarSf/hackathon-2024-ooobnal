import time

# from llama_cpp import Llama

import queue
import threading

class API:
    def __init__(self, master):
        print("START REQUEST HANDLER -> CONFIG HANDLER -> LOCAL LLM")
        self.master = master
        self.json_h = self.master.json_h
        self.json_h.get_json_config(self, "AI_API_config")


        self.processing_queue = queue.Queue()

    def _complex_init(self):
        params_model = self.main_node.local_LLM_llama_cpp["params_model"]
        self.llm = Llama(**params_model)
        self.role_tokens = self.llm.tokenize("bot\n".encode("utf-8"), special=True)

    def start(self):
        print("START REQUEST HANDLER -> CONFIG HANDLER -> LOCAL LLM(_process_queue_loop)")
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True, name='tread_1')
        self.is_running = True
        self.worker_thread.start()

    def stop(self):
        self.is_running = False
        print("STOP REQUEST HANDLER -> CONFIG HANDLER -> LOCAL LLM(_process_queue_loop)")
        self.worker_thread.join()

    def query_handler(self, model_name, messages_history):
        return self.add_query_in_queue(model_name, messages_history)

    def add_query_in_queue(self, model_name, messages_history):
        result_queue = queue.Queue()
        self.processing_queue.put((model_name, messages_history, result_queue))
        res = result_queue.get()
        del result_queue
        return res

    def _process_queue(self):
        while self.is_running:
            try:
                model_name, messages_history, result_queue = self.processing_queue.get(timeout=2)
                st_t = time.time()
                result = self._internal_query_handler(model_name, messages_history)
                print(f"Локальная модель обработала запрос за {time.time() - st_t} {model_name}, {messages_history}")
                if result_queue:
                    result_queue.put(result)
                self.processing_queue.task_done()
            except queue.Empty:
                pass

    def _internal_query_handler(self, model_name, messages_history):
        tokens = self.get_message_tokens(messages_history)
        generator = self.llm.generate(tokens, **self.main_node.local_LLM_llama_cpp["params_query"][model_name])
        data = ""
        for token in generator:
            if token == self.llm.token_eos():
                break
            data += self.llm.detokenize([token]).decode("utf-8", errors="ignore")
        # output = self.llm.create_chat_completion(messages_history)
        # data = output["choices"][0]["message"]["content"]
        return data

    def get_message_tokens(self, message_history):
        query = self.main_node.local_LLM_llama_cpp["params_query"]["system_prompt"].format(instruction=message_history[0]["content"], message_history=self.format_messages(message_history[1:]))
        content = query.encode("utf-8")
        tokens = self.llm.tokenize(content, special=True)
        all_tokens = tokens + self.role_tokens
        return all_tokens

    def format_messages(self, messages_history):
        formatted = ""
        for message in messages_history:
            role = message['role']
            content = message['content']
            formatted += f"{role}: {content}\n"
        return formatted
