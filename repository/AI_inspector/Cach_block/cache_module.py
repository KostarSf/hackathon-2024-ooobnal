import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

import threading

from elastic_cache import ElasticsearchCache

class Cache:
    def __init__(self, master):
        self.master = master
        self.json_h = self.master.json_h
        self.json_h.get_json_config(self, "elastic_conf")
        self.es_cache = ElasticsearchCache(index_name=self.index_name, es_url=self.es_url, es_user=self.es_user,es_password=self.es_password, es_params={"ca_certs": self.verif_certs_path,"verify_certs":True})

    def main_entrance(self, conf_cache_mode, func_conf, func_handler, unique_flow_determinant):
        self.main_node.set_request_state(unique_flow_determinant, "Сache Processing")
        if conf_cache_mode == "Record":
            return self.record_entrance(func_conf, func_handler)
        elif conf_cache_mode == "Auto_answer":
            return self.get_auto_answer(func_conf, func_handler)
        elif conf_cache_mode == "Auto_answer_without_save":
            return self.get_auto_answer(func_conf, func_handler, saving=False)

    def record_entrance(self, func_conf, func_handler, saving = True):
        conf_name, conf_query, mode = self.unpack_conf(func_conf)
        answer = func_handler(conf_name, conf_query, mode)
        if answer["status"] == "successfully" and saving:
            self.record_data(conf_name, conf_query, answer["data"])
        return answer

    def record_data(self, conf_name, conf_query, new_response):
        thread = threading.Thread(target=self.es_cache.update, args=(conf_name, conf_query, new_response))
        thread.start()

    def get_auto_answer(self, func_conf, func_handler, saving = True):
        conf_name, conf_query, mode = self.unpack_conf(func_conf)
        answer = self.es_cache.lookup(conf_name, conf_query)
        if not answer:
            answer = self.record_entrance(func_conf, func_handler)
        else:
            answer = "".join(answer)
        return answer

    def unpack_conf(self, conf_query):
        conf_name = conf_query["conf_name"]
        conf_data = conf_query["conf_data"]
        if "mode" in conf_query:
            mode = conf_query["mode"]
        else:
            mode = "Normal"
        return conf_name, conf_data, mode

