
#!/usr/bin/env python
# license removed for brevity
import threading
import time
import sys
import os
import json
import inspect
from collections import namedtuple

sys.path.append(os.path.join(os.path.dirname(__file__)))


class JsonHandler:

    def __init__(self, master = True):
        self.master = master
        self.get_json_config(self.master, "main_config")
        # self.get_pathes()
        # self.get_show_config_list = []
        # self.get_transition_configuration_list = []

    ############ UPDATING FUNCTIONS #############

    def load_in_json(self,data, file_name):
        with open(os.path.dirname(__file__) + '/' + file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_in_json_folder(self,data, file_name,folder_path):
        with open(folder_path + file_name, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_from_json(self,file_name,not_found_return = 0):
        path = os.path.dirname(__file__) + '/' + file_name
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                    return json.load(file)
        else:
            return not_found_return

    def load_from_json_folder(self, file_name, folder_path, not_found_return=0):
        if os.path.exists(folder_path + file_name):
            with open(folder_path + file_name, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            return not_found_return

    ############ GETTING FUNCTIONS ##############

    def get_json_config(self, _object, file_name):
        self.get_global_parameters(_object, False, file_name)

    ############ PATHES ########################

    # def get_pathes(self):
    #     current_path = os.path.join(os.path.dirname(__file__))
    #     self.master.json_path      = current_path
    #     self.master.data_base_path = current_path.replace("Json_block", "Data_base_block")
       

    ############ THREAD ########################

    def start(self):
        print("START JSON THREAD")
        self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=False, name = "json")
        self.main_loop_thread.start()


    def stop(self):
        self.is_main_loop = False
        self.main_loop_thread.join()
        print("END JSON THREAD")


    def main_loop(self):
        self.is_main_loop = True
        while self.is_main_loop:
            time.sleep(2)
            # self.get_json_config(self.master, "main_config")
            # self.get_json_config(self.master.question_handler, "forms")
            # for item in self.get_show_config_list:
            #     self.get_json_config(item, "show_config")
            # for item in self.get_transition_configuration_list:
            #     self.get_json_config(item, "transition_configuration")
            # self.load_in_json(self.master.question_answer_handler.users_status_answering,"user_status_answering.json")



    ############ SYSTEM FUNCTIONS ##############

    def get_global_data(self, file_name):      
        file = os.path.dirname(__file__) + "/%s.json" % file_name
        with open(file, encoding="UTF-8") as json_file:
            dictionaries_list = json.loads(json_file.read())["parameters"]    
            return( dictionaries_list )

    def get_local_data(self, file_name, dir_name):         
        file_path = os.path.join(os.path.dirname(__file__), '..', '..', dir_name, file_name + '.json')
        with open(file_path) as json_file:   
            dictionaries_list = json.loads(json_file.read())["parameters"]  
            return( dictionaries_list )
            
    def get_global_parameters(self, _object, object_name, file_name):             
        dictionaries_list = self.get_global_data(file_name)
        _block = self.get_block(dictionaries_list, object_name)
        self.set_parameters(_object, _block)            

    def get_local_parameters(self, _object, object_name, file_name, dir_name):             
        dictionaries_list = self.get_local_data(file_name, dir_name)
        _block = self.get_block(dictionaries_list, object_name)
        self.set_parameters(_object, _block) 

        
            
    def get_block(self, dictionaries_list, name = False):
        if name:
            for block in dictionaries_list:
                if block["name"] == name:
                    _block = {}
                    _block.update(block)
                    _block.pop("name");  
        else:
            for block in dictionaries_list:
                _block = {}
                _block.update(block)
        return(_block)


    def set_parameters(self, _object, _block): 
        for element in _block: 
            value = _block[element]
            if type(value) is str:    string = "'%s'" % value
            else:                     string = str(value)
            #self.object = _object
            text = "_object.%s = " + string
            exec(text % element)      

    def write_parameter(self, file_name, parameter_name, parameter_value):
        dictionaries_list = self.get_local_data(file_name, "calibration")
        _block = self.get_block(dictionaries_list)
        data = {}    
        data['parameters'] = []
        _block[parameter_name] = parameter_value
        data['parameters'].append(_block)

        with open(os.path.dirname(__file__) + "/../../configuration/calibration/%s.json" % file_name , 'w') as outfile:
            json.dump(data, outfile)

    def get_logger_parameters(self):
        with open(os.path.dirname(__file__) + "/logger_config.json", 'r') as openfile:
            json_object = json.load(openfile)
            return json_object


if __name__ == "__main__":
    pass













