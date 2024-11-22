import os

import emoji



class MessageHandler:
    def __init__(self, master):
        self.master = master


    def _complex_init(self):
        self.telegram = self.master.telegram
        self.distribution = self.master.distribution

    def handle_text_message(self, message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        message_text = self.get_message_text(message.text)

        print(message.text)
        print(message_text)
        print(chat_id)
        print(user_id)
        self.distribution.massage(chat_id,user_id, message_text)

    def handle_file_message(self, message, bot_instance):
        chat_id = message.chat.id
        user_id = message.from_user.id
        document = message.document
        file_name = message.document.file_name
        file_base_name, file_type = os.path.splitext(file_name)
        file_type = file_type[1:]
        # mime_type = document.mime_type
        # file_size = document.file_size

        if file_type in ['txt', 'pdf', 'docx', 'csv']:
            file_info = bot_instance.get_file(document.file_id)
            downloaded_file = bot_instance.download_file(file_info.file_path)

            file_folder = "../docs/" + str(chat_id) + "/"
            self.create_directory(file_folder)
            file_path = file_folder + file_name

            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            if message.caption:
                text = message.caption
                self.distribution.file_text_handler(chat_id,text,file_base_name,file_type,downloaded_file)
            else:
                self.distribution.file_handler(chat_id,file_base_name,file_type,downloaded_file)


    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Место хранения init_telegram '{path}' успешно создана.")

    def get_message_text(self, message_text):
        if any(char in emoji.EMOJI_DATA for char in message_text):
            message_text = emoji.demojize(message_text, language='alias')
            print(message_text)
        return message_text

    def send_message_user(self, chat_id, message_text):
        self.telegram.send_message_users([chat_id], message_text)
