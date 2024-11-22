import time

import json
from pprint import pprint

class ReturnHandler:
        def __init__(self, master):
            print("START REQUEST HANDLER -> CONFIG HANDLER -> RETURN HANDLER")
            self.master = master

        def func_return_manager(self, return_func_name, data):
            if return_func_name != "None":
                func_return = getattr(self, return_func_name, None)
                if not func_return is None:
                    return func_return(data)
                else:
                    raise Exception(f"Функция возврата не найдена {return_func_name}")
            else:
                return self.successfully_return(data)

        def binary_return(self, data):
            if data == "True":
                return self.successfully_return(True)
            elif data == "False":
                return self.successfully_return(False)
            else:
                return self.error_return("API ANSWER ERROR", "Ошибка ответа API OPEN AI неверный формат ответа")

        def data_with_none_return(self, data):
            if data == "None":
                return self.successfully_return(None)
            else:
                return self.successfully_return(data)

        def int_return(self, data):
            if data.isdigit():
                return self.successfully_return(int(data))
            elif data == "None":
                return self.successfully_return(None)
            else:
                return self.error_return("API ANSWER ERROR", "Ошибка ответа API OPEN AI неверный формат ответа")

        def ternary_return(self, data):
            if data == "None":
                return self.successfully_return(None)
            else:
                return self.binary_return(data)

        def successfully_return(self, data):
            return {"status":"successfully","data": data}

        def error_return(self, type_exception, text_exception):
            return {"status": "Error", "data": None, "type": type_exception, "text_exception": text_exception}


