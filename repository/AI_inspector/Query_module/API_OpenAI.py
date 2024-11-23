


from openai import OpenAI

class API:
    def __init__(self, master):
        self.master     = master
        print("START REQUEST HANDLER -> CONFIG HANDLER -> API GPT")

    def _complex_init(self):
        self.api_key = self.main_node.open_AI["api_key"]
        self.client = OpenAI(api_key=self.api_key)

    def query_handler(self, model_name, messages_history):
        completion = self.client.chat.completions.create(
            model=model_name,
            messages=messages_history,
            temperature=0.2)
        data = completion.choices[0].message.content
        return data
