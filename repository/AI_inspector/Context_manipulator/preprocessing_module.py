import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

import tiktoken

from vector_base import VectorBase
from clear_instrument import ClearInstrument
from convert_module import ConvertFileModule

class PreprocessingModule:
    def __init__(self, master):
        print("START REQUEST HANDLER -> PREPROCESSING MODULE")
        self.master = master
        self.vb               = VectorBase(self.master)
        self.clear_instrument = ClearInstrument(self.master)
        self.convert          = ConvertFileModule(self.master)


    def _complex_init(self):
        self.vb.main_node                   = self.main_node
        self.clear_instrument.main_node     = self.main_node
        self.convert.main_node              = self.main_node

        self.limit_token                = self.main_node.limit_token
        self.tiktoken_encoding_model    = self.main_node.tiktoken_encoding_model
        self.count_token_encoding       = tiktoken.encoding_for_model(self.tiktoken_encoding_model)
        self.vb.limit_token             = self.limit_token
        self.vb.count_token_encoding    = self.count_token_encoding

        self.vb._complex_init()
        self.clear_instrument._complex_init()

    def start(self):
        self.vb.start()

    def stop(self):
        self.vb.stop()

    def normal_entrance(self, config_history, unique_flow_determinant):
        if not self.check_token_window([message["content"] for message in config_history if "content" in message]):
            return config_history

        self.clear_instrument.clear_unimportant(config_history)
        if not self.check_token_window([message["content"] for message in config_history if "content" in message]):
            return config_history

        return self.vb.get_indexed_message_history(config_history, unique_flow_determinant)

    def vectorbase_entrance(self, config_history, unique_flow_determinant):
        return self.vb.get_indexed_message_history(config_history, unique_flow_determinant)

    def initialize_file(self, conf_name, conf_data, unique_flow_determinant):
        self.main_node.set_request_state(unique_flow_determinant, "Unpacking file")
        if conf_name == "data":
            file_text = conf_data["file_text"]
        elif conf_name == "file_path":
            file_text = self.convert.convert_file_text(conf_data, file_transfer=False)
        elif conf_name == "file":
            file_text = self.convert.convert_file_text(conf_data, file_transfer=True)
        conf_data["file_text"] = file_text
        return self.vb.init_file(conf_data, unique_flow_determinant)

    def vectorize_entrance(self, conf_name, conf_data, unique_flow_determinant):
        self.main_node.set_request_state(unique_flow_determinant, "Vectorize")
        if conf_name == "vectorize":
            return self.vb.vectorize(conf_data)
        elif conf_data == "get_embedding":
            return self.vb.get_embeddings_HuggingFaceEmbeddings()


    def check_token_window(self, text_arr):
        sum_token = sum([self.count_tokens(i) for i in text_arr])
        return sum_token > self.limit_token

    def count_tokens(self, text):
        num_tokens = len(self.count_token_encoding.encode(text))
        return num_tokens
