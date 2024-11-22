import os
import sys
import threading
import re

import zlib

import queue

sys.path.append(os.path.join(os.path.dirname(__file__)))

import time


# Vector_base
from langchain_chroma import Chroma
# from langchain_community.vectorstores import Chroma
# from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

# text handler
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

# embeddings
from langchain_community.embeddings import OpenAIEmbeddings               # OpenAI embeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings  # Instructor — это открытая модель, которая генерирует эмбеддинги, учитывая контекст вашего запроса.
# from langchain_community.embeddings import HuggingFaceEmbeddings        # HuggingFace embeddings

from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

# langchain llms
# from langchain.llms import OpenAI


# langchain chains звенья обработки
# from langchain.chains import RetrievalQA #Обработчик QA

class VectorBase:
    def __init__(self, master):
        print("START REQUEST HANDLER -> PREPROCESSING MODULE -> VECTOR BASE")
        self.master = master
        self.json_h = self.master.json_h

        self.queue_init_file = queue.Queue()


    def _complex_init(self):
        self.__init_conf_var()

        self.storage_path_folder     = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.main_node.storage_path_folder)
        self.vectorstore_folder      = self.main_node.vectorstore_folder
        self.vectorstore_temp_folder = self.main_node.vectorstore_temp_folder

        self.create_directory(self.storage_path_folder)
        self.create_directory(self.storage_path_folder + self.vectorstore_folder)
        self.create_directory(self.storage_path_folder + self.vectorstore_folder + self.vectorstore_temp_folder)

        # self.client = Chroma()
        self.set_embeddings_HuggingFaceEmbeddings(self.embeddings_model)
        # self.main_vectorstore   = self.get_vectorstore(self.embeddings, self.type_vectorstore, self.name_main_collection)
        self.text_splitter      = self.get_text_splitter(self.chunk_size_splitter, self.chunk_overlap_splitter)

    def __init_conf_var(self):
        self.embeddings_model       = self.main_node.embeddings_model
        self.type_vectorstore       = self.main_node.type_vectorstore
        self.chunk_size_splitter    = self.main_node.chunk_size_splitter
        self.chunk_overlap_splitter = self.main_node.chunk_overlap_splitter
        # self.name_main_collection   = "temp_collection"

    ####### WORK WITH EMBEDDING ##########
    def set_embeddings_HuggingFaceEmbeddings(self, model_name):
        path_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../storage/embedding_model")
        if not os.path.exists(path_model):
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
            self.save_embeddings(path_model)
        else:
            self.embeddings = self.load_embeddings_from_local_files(path_model)

    def save_embeddings(self, directory):
        self.create_directory(directory)

        model = SentenceTransformer(self.embeddings.model_name)
        model.save(directory)
        print(f"Модель эмбеддингов сохранена в {directory}.")

    def load_embeddings_from_local_files(self, directory):
        if not os.path.exists(directory):
            raise ValueError(f"Директория {directory} не существует.")

        # print(f"Модель эмбеддингов загружена из {directory}.")
        return HuggingFaceEmbeddings(model_name=directory)

    ###### FUNC FOR MODE VECTORIZE ##########
    def get_embeddings_HuggingFaceEmbeddings(self):
        return self.embeddings

    def vectorize(self, query):
        return self.embeddings.embed_query(query)

    ##### FUNC FOR MODE INIT_FILE ########
    def init_file(self, conf_file, unique_flow_determinant):
        file_text = conf_file["file_text"]
        index_name = conf_file["index_name"]
        if "embedding" in conf_file:
            embeddings = conf_file["embeddings"]
        else:
            embeddings = self.embeddings

        vectorstore = self.get_vectorstore(embeddings, self.type_vectorstore, index_name)

        return self.add_file_init_queue(vectorstore, file_text, unique_flow_determinant)


    ##### FILE INIT QUEUE HANDLE #######
    def add_file_init_queue(self, vectorstore, file_text, unique_flow_determinant):
        result_queue = queue.Queue()
        self.queue_init_file.put((vectorstore, file_text, unique_flow_determinant, result_queue))
        print(f"Файл добавлен в очередь инициализации")
        return result_queue

    def start(self):
        print("START REQUEST HANDLER -> PREPROCESSING MODULE (FILE INIT QUEUE)")
        self.worker_thread = threading.Thread(target=self._process_file_init_queue, daemon=True, name='file_init')
        self.is_running = True
        self.worker_thread.start()

    def _process_file_init_queue(self):
        while self.is_running:
            try:
                vectorstore, file_text, unique_flow_determinant, result_queue = self.queue_init_file.get(timeout=2)
                self.main_node.set_request_state(unique_flow_determinant, "Init File")
                status = self.add_vectorestore_file(vectorstore, file_text)
                self.main_node.set_request_state(unique_flow_determinant, "End Init File")
                if result_queue:
                    result_queue.put(status)
                self.queue_init_file.task_done()
            except queue.Empty:
                pass

    def add_vectorestore_file(self, vectorstore, file_text):
        try:
            s_t = time.time()
            docs = self.split_text_docs(file_text)

            num_vector = self.get_num_vector(vectorstore)
            if num_vector > 0:
                if self.document_comparison(vectorstore, docs):
                    return "successfully"
                else:
                    self.reset_collection(vectorstore)

            vectorstore.add_documents(docs)
            print(f"Файл инициализирован {vectorstore._collection_name} заняло времени:", time.time() - s_t)
            return "successfully"
        except Exception as ex:
            print(f"Ошибка инициализации файла {ex}")
            return "Error"

    def document_comparison(self, vectorstore, docs):
        vectorstore_docs = {str(doc) for doc in vectorstore.get()["documents"]}

        docs_set = {str(doc.page_content) for doc in docs}

        return docs_set.issubset(vectorstore_docs)

    def stop(self):
        self.is_running = False
        print("STOP REQUEST HANDLER -> PREPROCESSING MODULE (FILE INIT QUEUE)")
        self.worker_thread.join()

    ##### FUNC FOR INDEXING | MODE NORMAL, CACHE, VB ########
    def get_indexed_message_history(self, messages_history, unique_flow_determinant):
        self.main_node.set_request_state(unique_flow_determinant, "Сontext Сompression")
        query = self.get_query_in_message_history(messages_history)
        self.get_vectorstores_message_history(messages_history, query, unique_flow_determinant)
        self.get_ranked_query_segments(messages_history, query, unique_flow_determinant)
        free_context_window = self.get_calculate_free_context_window(messages_history)
        if free_context_window <= 0:
            self.critical_context_overflow(messages_history, unique_flow_determinant)
        else:
            self.fill_free_context(messages_history, free_context_window)

        return messages_history

    ##### STAGES OF INDEX PROCCESING ######
    def get_query_in_message_history(self, messages_history):
        query = []
        for message in messages_history:
            if "indexing" not in message:
                if message["role"] == "file":
                    message["indexing"] = True
                else:
                    message["indexing"] = False
            if message["role"] == "user":
                query.append(message["content"])
        query = "\n".join(query)
        return query

    def get_vectorstores_message_history(self, messages_history, query, unique_flow_determinant):
        for i, message in enumerate(messages_history):
            if message["role"] == "system":
                if not message["indexing"]:
                    continue

                index_name = f"main_{i}_vectorstore"
                persist_directory = self.get_vectorstore_temp_folder(unique_flow_determinant)
                vectorstore = self.get_vectorstore(self.embeddings, self.type_vectorstore, index_name, persist_directory)

                docs         = self.split_text_docs(message["content"], dop_index=i)
                sorted_index = self.get_sorted_index(vectorstore, query, docs)

                if len(sorted_index) < 2:
                    message["indexing"] = False
                else:
                    message["vectorstore"] = sorted_index

            elif message["role"] == "file":
                file_name    = self.get_index_file(message["content"])
                vectorstore  = self.get_vectorstore(self.embeddings, self.type_vectorstore, file_name)

                if "special_request" in message:
                    sorted_index       = self.sort_index(vectorstore, message["special_request"])
                else:
                    sorted_index       = self.sort_index(vectorstore, query)

                message["vectorstore"] = sorted_index

                docs                   = self.sort_docs_by_index(sorted_index)
                texts                  = self.convert_docs_texts(docs)
                file_text              = "/n".join(texts)

                message["file_text"]   = file_text

                if not message["indexing"]:
                    message["content"] = self.replace_file_pattern(message["content"], file_text)

        return messages_history


    def get_ranked_query_segments(self, messages_history, query, unique_flow_determinant):
        all_docs          = self.sorting_messages_with_convert_text_docs(messages_history)

        index_name        = "ranked_messages"
        persist_directory = self.get_vectorstore_temp_folder(unique_flow_determinant)

        vectorstore       = self.get_vectorstore(self.embeddings, self.type_vectorstore, index_name, persist_directory)
        sorted_index      = self.get_sorted_index(vectorstore, query, all_docs)
        importance_range  = [doc.metadata["dop_index"] for doc in sorted_index]

        for value, index in enumerate(importance_range):
            messages_history[index]["importance_rank"] = value

        weight_dict      = {index: value["weight"] for index, value in enumerate(messages_history) if "weight" in value}
        ranked_conf_dict = self.calculate_fullness(importance_range, weight_dict)

        for index, value in ranked_conf_dict.items():
            messages_history[index]["relative_importance"] = value

        return messages_history


    def fill_free_context(self, messages_history, free_context_window):
        generator_config = [
            {
                "index": index,
                "gen": (text for text in message["vectorstore"]),
                "context_window": free_context_window * message["relative_importance"]
            }
            for index, message in enumerate(messages_history) if message["indexing"]
        ]

        for message_gen_config in generator_config:
            index = message_gen_config["index"]

            sorted_docs = self.get_sorted_inserted_docs(message_gen_config["gen"],  message_gen_config["context_window"])

            result = "".join(self.get_combining_index(sorted_docs))

            if messages_history[index]["role"] == "file":
                messages_history[index]["content"] = self.replace_file_pattern(messages_history[index]["content"], result)
            else:
                messages_history[index]["content"] = result
        return messages_history

    def critical_context_overflow(self, messages_history, unique_flow_determinant):
        for message in messages_history:
            if message["role"] == "file":
                message["indexing"] = True
            elif message["role"] == "system":
                message["indexing"] = True
        return self.get_indexed_message_history(messages_history, unique_flow_determinant)

    #### MAINTENANCE FUNC FOR INDEXING STAGES ######
    def sorting_messages_with_convert_text_docs(self, messages_history):
        all_docs = []
        for i, message in enumerate(messages_history):
            if message["indexing"]:
                if message["role"] == "system":
                    docs = self.convert_texts_docs([message["content"]], dop_index=i)
                    all_docs.extend(docs)
                elif message["role"] == "file":
                    docs = self.convert_texts_docs([message["file_text"]], dop_index=i)
                    all_docs.extend(docs)
        return all_docs

    def get_sorted_inserted_docs(self, generator, context_window):
        inserted_docs = []
        current_context = 0
        for doc in generator:
            current_context += self.count_tokens(doc.page_content)
            if current_context < context_window:
                inserted_docs.append(doc)
            else:
                break

        sorted_docs = self.sort_docs_by_index(inserted_docs)
        return sorted_docs

    def get_combining_index(self, sorted_docs):
        result = []
        previous_key = None
        for doc in sorted_docs:
            if previous_key is not None and doc.metadata["index"] - previous_key > 1:
                if len(result) >= 1 and result[-1] != "\n Пропущенный сегмент\n":
                    result.append("\n Пропущенный сегмент\n")
            else:
                result.append(doc.page_content)
            previous_key = doc.metadata["index"]


        return result

    #### SIMPLE PROCCESING FUNC ######
    def calculate_fullness(self, importance_range, weight_dict):
        # Распределение гибкого процента важности
        weighted_values = {}
        total_positions = len(importance_range)

        for i, index in enumerate(importance_range):
            position_weight = (total_positions - i) / total_positions  # коэффициент позиции (4-1)/4

            weighted_value = weight_dict.get(index, 0.5) * position_weight
            weighted_values[index] = weighted_value

        total_weight = sum(weighted_values.values())
        if total_weight == 0:
            return [0] * len(importance_range)

        normalized_percentages = {key: value / total_weight for key, value in weighted_values.items()}
        return normalized_percentages

    def get_calculate_free_context_window(self, messages_history):
        busy_context_window = 0
        for index, message in enumerate(messages_history):
            if not message["indexing"]:
                busy_context_window += self.count_tokens(message["content"])
        return self.limit_token - busy_context_window

    def sort_docs_by_index(self, docs):
        return sorted(docs, key=lambda doc: doc.metadata["index"])

    def get_index_file(self, text):
        match = re.search(r'file::(.*?)::file', text)
        if match:
            return match.group(1)
        else:
            raise FileExistsError("Отсутсвие имени файла в запросе")

    def replace_file_pattern(self, orig_text, file_text):
        result = re.sub(r'file::(.*?)::file', file_text, orig_text)
        return result

    # def get_indexed_message_history(self, messages_history, count_tokens_func):
    #     clear_messages_history, query = self.get_clear_message_history_and_query(messages_history)
    #     docs_for_index                = self.get_doc_index(messages_history)
    #     sort_index                    = self.get_sorted_index(self.main_vectorstore, query, docs_for_index)
    #     clear_message_history         = self.get_relevant_message_history(clear_messages_history, sort_index, count_tokens_func)
    #     return clear_message_history


    # def get_clear_message_history_and_query(self, messages_history):
    #     clear_message_history = []
    #     query = []
    #     for message in messages_history:
    #         if message["role"] == "user":
    #             query.append(message["content"])
    #             clear_message_history.append(message)
    #         elif message["role"] == "system":
    #             temp = message.copy()
    #             temp["content"] = {}
    #             clear_message_history.append(temp)
    #     query = "\n".join(query)
    #     return clear_message_history, query

    # def get_doc_index(self, message_history):
    #     docs = []
    #     for i, message in enumerate(message_history):
    #         if message["role"] != "user":
    #             docs = self.split_text_docs(message["content"], dop_index=i)
    #             docs.extend(docs)
    #     return docs

    def get_num_vector(self, vectorstore):
        return vectorstore._collection.count()

    def sort_index(self, vectorstore, query):
        count_vectors = self.get_num_vector(vectorstore)
        search_results = vectorstore.similarity_search(query, k=count_vectors)
        return search_results

    def get_sorted_index(self, vectorstore, query, docs_for_index):
        self.reset_collection(vectorstore)  # if Chroma
        vectorstore.add_documents(documents=docs_for_index)
        search_results = self.sort_index(vectorstore, query)

        # OLD
        # self.vectorstore = self.get_vectorstore_old_ChromaDB(documents, self.embeddings)
        # self.vectorstore = self.get_vectorstore_old_FAISS(documents, self.embeddings)

        # query_embedding = self.vectorize(query)
        # search_results = self.vectorstore.similarity_search_by_vector(query_embedding, k=len(documents))
        return search_results

    def reset_collection(self, vectorstore):
        vectorstore.reset_collection()

    ###### MAINTENANCE FUNCTION FOR INDEX ######
    def split_text_by_words(self, documents):
        doc_out = self.text_splitter.split_documents(documents)
        return doc_out

    def get_doc(self, text, metadata = {}):
        return Document(page_content=text, metadata=metadata)

    def convert_texts_docs(self, text_array, dop_index = None):
        if dop_index is None:
            return [self.get_doc(text, {"index": i}) for i, text in enumerate(text_array)]
        else:
            return [self.get_doc(text, {"index": i, "dop_index":dop_index}) for i, text in enumerate(text_array)]

    def convert_docs_texts(self, documents, meta_index=None):
        if meta_index == None:
            return [doc.page_content for doc in documents]
        else:
            return [doc.page_content for doc in documents if doc.metadata["index"] == meta_index]

    def split_text(self, text):
        doc_message = [self.get_doc(text)]
        split_message = self.split_text_by_words(doc_message)
        if len(split_message) > 3:
            texts = self.convert_docs_texts(split_message)
        else:
            texts = self.convert_docs_texts(doc_message)
        return texts

    def split_text_docs(self, text, dop_index = None):
        texts = self.split_text(text)
        docs = self.convert_texts_docs(texts, dop_index=dop_index)
        return docs

    ######## INIT FUNCTIONS ######
    def get_text_splitter(self, chunk_size, chunk_overlap):
        # text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "  "],
            length_function=self.count_tokens,
            keep_separator=True
        )
        return text_splitter

    ###### INIT VECTORSTORE FUNCTION ######
    def get_vectorstore(self, embeddings, type_vb = "Chroma", *args):
        func = getattr(self, f"get_vectorstore_{type_vb}")
        return func(embeddings, *args)

    def get_vectorstore_Chroma(self, embeddings, index_name="example_collection", persist_directory = "files"):
        persist_directory = self.vectorstore_folder + persist_directory
        # persist_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), persist_directory)
        self.create_directory(persist_directory)
        vector_store = Chroma(
            collection_name=index_name,
            embedding_function=embeddings,
            collection_metadata=self.main_node.vectorstore_metadata,
            persist_directory=persist_directory
        )
        return vector_store


    # def get_vectorstore_FAISS(self, embeddings):
    #     index = faiss.IndexFlatL2(len(embeddings.embed_query("Этот запрос требуется для определения размерности эмбединга")))
    #
    #     vectorstore = FAISS(
    #         embedding_function=embeddings,
    #         index=index,
    #         docstore=InMemoryDocstore(),
    #         index_to_docstore_id={},
    #     )
    #     return vectorstore
    #
    # def save_FAISS_vectorstore(self, vectorstore, path):
    #     vectorstore.save_local(path)
    #
    # def load_FAISS_vectorstore(self, path):
    #     vectorstore = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
    #     return vectorstore

    # def get_vectorstore_old_with_doc(self, documents, embeddings, type_vb = "Chroma"):
    #     func = getattr(self, f"get_vectorstore_old_{type_vb}")
    #     return func(documents, embeddings)

    # def get_vectorstore_old_Chroma(self, documents, embeddings, index_name="example_collection"):
    #     vector_store = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=index_name)
    #     return vector_store

    # def get_vectorstore_old_FAISS(self, embeddings, documents):
    #     vectorstore = FAISS.from_documents(documents, embedding=embeddings)
    #     vectorstore.save_local(index_name)
        # return vectorstore

    ###### SYSTEM-WIDE FUNCTON ######
    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Место хранения Vectorstore '{path}' успешно создана.")

    def count_tokens(self, text):
        num_tokens = len(self.count_token_encoding.encode(text))
        return num_tokens

    def get_vectorstore_temp_folder(self, unique_flow_determinant):
        path = self.vectorstore_temp_folder + unique_flow_determinant + "/"
        return path


if __name__ == "__main__":
    test = VectorBase(True)
