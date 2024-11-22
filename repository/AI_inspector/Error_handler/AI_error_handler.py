



class AI_error_handler:
    def __init__(self, master, retries=3):
        print("START REQUEST HANDLER -> AI ERROR HANDLER")
        self.master = master
        self.retries = retries


    def handle_error(self, error, retry_callback_dict = None):
        pass

    def retry_operation(self, callback, *args):
        for attempt in range(1, self.retries + 1):
            try:
                print(f"Попытка {attempt} из {self.retries}")
                return callback(*args)
            except Exception as e:
                print(f"Ошибка при попытке {attempt}: {e}")
                if attempt == self.retries:
                    print("Превышено количество попыток. Обработка завершена.")
        return None