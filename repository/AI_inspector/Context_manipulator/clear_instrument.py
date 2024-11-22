


class ClearInstrument:
    def __init__(self, master):
        print("START REQUEST HANDLER -> PREPROCESSING MODULE -> CLEAR INSTRUMENT")
        self.master = master


    def _complex_init(self):
        self.weight_cleaning_boundary = self.main_node.weight_cleaning_boundary

    def clear_unimportant(self, messages_history):
        del_indexes = []
        for i, message in enumerate(messages_history):
            if "weight" in message:
                if message["weight"] < self.weight_cleaning_boundary:
                    del_indexes.append(i)
        for i in sorted(del_indexes, reverse=True):
            del messages_history[i]
        return messages_history