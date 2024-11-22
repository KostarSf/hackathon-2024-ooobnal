import os
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__)))

from dependencies.json_handler import JsonHandler
from database import Database

class Master:
    def __init__(self):
        self.json_h                 = JsonHandler(self)
        self.sqlite_db              = Database(self)



if __name__ == "__main__":
    test = Master()
    test.sqlite_db.start()

    test.sqlite_db.create("Users", [1234, 1234], 1)
    time.sleep(10)

    test.sqlite_db.stop()
