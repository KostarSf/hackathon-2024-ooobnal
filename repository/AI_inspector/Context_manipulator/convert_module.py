
import os
import PyPDF2
import docx
import csv


class ConvertFileModule:
    def __init__(self, master):
        print("START REQUEST HANDLER -> PREPROCESSING MODULE -> CONVERT FILE MODULE")
        self.master = master

    def convert_file_text(self, conf_file, file_transfer):
        if file_transfer:
            file_type = conf_file["file_type"]
            file_data = conf_file["file"]
        else:
            file_type = conf_file["file_type"]
            file_data = conf_file["file_path"]

        if file_type == 'txt':
            return self._convert_txt(file_data, file_transfer)
        elif file_type == 'pdf':
            return self._convert_pdf(file_data, file_transfer)
        elif file_type == 'docx':
            return self._convert_docx(file_data)
        elif file_type == 'csv':
            return self._convert_csv(file_data, file_transfer)
        else:
            print(f"Тип файла '{file_type}' не поддерживается.")
            return None

    def _convert_txt(self, file_data, file_transfer):
        if file_transfer:
            return file_data.read()
        else:
            with open(file_data, 'r', encoding='utf-8') as file:
                return file.read()

    def _convert_pdf(self, file_data, file_transfer):
        if file_transfer:
            return self._convert_pdf_base(file_data)
        else:
            with open(file_data, 'rb') as file:
                return self._convert_pdf_base(file)

    def _convert_pdf_base(self, file_data):
        text = ""
        pdf_reader = PyPDF2.PdfReader(file_data)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    def _convert_docx(self, file_data):
        doc = docx.Document(file_data)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    def _convert_csv(self, file_data, file_transfer):
        if file_transfer:
            return self._convert_csv_base(file_data)
        else:
            with open(file_data, 'r', encoding='utf-8') as file:
                return self._convert_csv_base(file)
    def _convert_csv_base(self, file_data):
        text = ""
        reader = csv.reader(file_data)
        for row in reader:
            text += ", ".join(row) + "\n"
        return text
