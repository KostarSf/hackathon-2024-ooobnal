import time
from pprint import pprint

from Request_handler import RequestHandler

from block_upgrade.json_handler import JsonHandler
from Telegram.Telegram_block import Telegram_Handler

from testing.test_text import text_book
class Master:
    def __init__(self):
        self.json_h             = JsonHandler(self)
        self.ai_inspector       = RequestHandler(self)
        self.telegram_handler   = Telegram_Handler(self)
        self._complex_init()

    def _complex_init(self):
        self.ai_inspector._complex_init()


if __name__ == "__main__":
    test = Master()
    # s_t = time.time()
    # pprint(test.ai_inspector.main_entrance("main", [{"role": "file", "content": "Текст произведения Война и Мир:\n", "indexing": True, "weight": 0.5},
    #           {"role": "user", "content": "о чем произведение"}], "Normal")
   # )

    # print("мусор", мусор)
    # print("total", total)
    # print("ошибок", total - res - мусор)
    # Modes:
    # Normal
    # ("main", [{"role": "system", "content": "Текст произведения Война и Мир:\n", "indexing": True, "weight": 0.5},
    #           {"role": "user", "content": "о чем произведение"}], "Normal")
    # VB
    # ("main", [{"role": "file", "content": "Текст произведения Война и Мир: file::voina_i_mir::file\n", "indexing": True, "weight": 0.5},
    #               {"role": "user", "content": "о чем произведение"}], "VB")
    # Cache
    # ("Auto_answer", {"conf_name": "main",
    #                  "conf_data": [{"role": "file", "content": "Текст произведения Война и Мир:\n", "indexing": True,
    #                                 "weight": 0.5},
    #                                {"role": "user", "content": "о чем произведение"}], "mode": "Normal"}, "Cache"))
    # Vectorization
    # Generate
    # Init_file
    # pprint(test.ai_inspector.main_entrance("data", {"file_text": text_book, "index_name": "voina_i_mir"}, "Init_file"))
    # time.sleep(10000)

























    # time.sleep(1000)
    # ("file_path", {"file_type": "docx",
    #                "file_path": r"C:\Users\denis\PycharmProjects\Test_telegram\New_module\AI_inspector\voina-i-mir.docx",
    #                "index_name": "voina_i_mir"}, "Init_file")

    # [{"role": "system", "content": text_book},
    #  {"role": "user", "content": "о чем произведение"}]


    # for i in range(2, 10):
    #     from block_upgrade.json_handler import JsonHandler
    #     class Master:
    #         def __init__(self, metadata):
    #             self.metadata = metadata
    #             self.json_h             = JsonHandler(self)
    #             self.AI_QP              = RequestHandler(self)
    #
    #     test = Master({
    #         "hnsw:M": i*10,
    #         "hnsw:construction_ef": i * 100,
    #     })
    #     s_t = time.time()
    #     print(i)
    #     test.AI_QP.main_entrance("UTF11",[{"role": "system", "content": text_book},
    #                                              {"role": "user", "content": "о чем произведение"}
    #                                              ] ,"")
    #     print(time.time() - s_t)



# Conf for Init File
# conf_name - тип онфигурационных данных data - данные передаются в виде текста, file_path - данные в конфиге файле подразумевают распаковку из пути, file - данные в конфиге содержит прямую ссылку на файл
# conf_data = {
#   file_type = "txt", #распаковка типов происходит в ConvertModule
#   file_path = ".."
#   index_name = "" Уникальное имя индекса
#   embedding - (Optional) ссылка на embedding если будет использваться какой-то специфический
# }

# Conf for VB
# message_history = [
# {"role": "file", "content": "Текст произведения Война и Мир:\nfile::text_book::file", "special_request": "text", "indexing": True, "weight": 0.5},
# {"role": "system", "content": "text"},
# {"role": "user", "content": "о чем произведение"}
# ]