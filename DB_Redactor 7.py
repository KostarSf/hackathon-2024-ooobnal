# pip install PyQt5




import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QComboBox, QTabWidget, QScrollArea, QGroupBox,
                             QLabel, QLineEdit, QMessageBox, QInputDialog)


class YourApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_edit_mode_enabled = False

        self.edit_mode_button = QPushButton("Редактировать", self)
        self.edit_mode_button.clicked.connect(self.toggle_edit_mode)

        self.update_button_visibility()

    def toggle_edit_mode(self):
        self.is_edit_mode_enabled = not self.is_edit_mode_enabled
        self.update_button_visibility()

    def update_button_visibility(self):
        if self.is_edit_mode_enabled:
            self.edit_mode_button.setVisible(True)
        else:
            self.edit_mode_button.setVisible(False)

    def some_condition_change(self, condition):
        self.is_edit_mode_enabled = condition
        self.update_button_visibility()


class DBEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DB Editor")
        self.setGeometry(100, 100, 1000, 600)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout()

        self.left_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.left_layout.addWidget(self.tab_widget)

        self.right_layout = QVBoxLayout()

        display_group = QGroupBox("Отображение")
        display_layout = QVBoxLayout()

        self.access_level_combo = QComboBox()
        self.access_level_combo.addItems(["Просмотр", "Редактирование данных", "Редактирование БД"])
        self.access_level_combo.setCurrentIndex(0)
        self.access_level_combo.currentIndexChanged.connect(self.change_access_level)
        display_layout.addWidget(QLabel("Режим"))
        display_layout.addWidget(self.access_level_combo)

        display_group.setLayout(display_layout)
        self.right_layout.addWidget(display_group)

        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout()

        self.filter_column_combo = QComboBox()
        self.filter_column_combo.addItem("Выберите столбец")
        filter_layout.addWidget(self.filter_column_combo)

        self.filter_condition_combo = QComboBox()
        self.filter_condition_combo.addItems(["содержит", "равно", "начинается с", "заканчивается на"])
        filter_layout.addWidget(self.filter_condition_combo)

        self.filter_line_edit = QLineEdit()
        self.filter_line_edit.setPlaceholderText("Введите текст для фильтрации")
        filter_layout.addWidget(self.filter_line_edit)

        self.filter_apply_button = QPushButton("Применить фильтр")
        self.filter_apply_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_apply_button)

        self.filter_reset_button = QPushButton("Сбросить фильтр")
        self.filter_reset_button.clicked.connect(self.reset_filter)
        filter_layout.addWidget(self.filter_reset_button)

        filter_group.setLayout(filter_layout)
        self.right_layout.addWidget(filter_group)

        edit_group = QGroupBox("Редактирование БД")
        edit_layout = QVBoxLayout()

        self.load_button = QPushButton('Открыть базу данных')
        self.load_button.clicked.connect(self.open_db)
        edit_layout.addWidget(self.load_button)

        self.save_button = QPushButton('Сохранить изменения')
        self.save_button.clicked.connect(self.save_changes)
        edit_layout.addWidget(self.save_button)

        self.add_row_button = QPushButton('Добавить строку')
        self.add_row_button.clicked.connect(self.add_row)
        edit_layout.addWidget(self.add_row_button)

        self.delete_row_button = QPushButton('Удалить строку')
        self.delete_row_button.clicked.connect(self.delete_row)
        edit_layout.addWidget(self.delete_row_button)

        self.new_column_name_edit = QLineEdit()
        self.new_column_name_edit.setPlaceholderText("Введите имя нового столбца")
        edit_layout.addWidget(self.new_column_name_edit)

        self.add_column_button = QPushButton('Добавить столбец')
        self.add_column_button.clicked.connect(self.add_column)
        edit_layout.addWidget(self.add_column_button)

        self.delete_column_button = QPushButton('Удалить столбец')
        self.delete_column_button.clicked.connect(self.delete_column)
        edit_layout.addWidget(self.delete_column_button)

        edit_group.setLayout(edit_layout)
        self.right_layout.addWidget(edit_group)

        self.right_layout.addStretch()

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)
        self.right_widget.setFixedWidth(250)

        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addWidget(self.right_widget)

        self.main_widget.setLayout(self.main_layout)

        self.db_connection = None
        self.current_table = None
        self.access_level = 'view'
        self.visual_mode = False

        #Тута можно исключение поменять можно
        self.excluded_tables = []
        #Для проверки можно закоментировать данный путь, он будет открывать возможность к ручному выбору БД.
        #self.database_path = r"C:\Users\dante\PycharmProjects\22\Data_base_block\organization.db"

        self.open_db()

        self.change_access_level()

    def change_access_level(self):
        self.access_level = self.access_level_combo.currentText()
        self.update_buttons()

    def update_buttons(self):
        if self.access_level == 'Просмотр':
            self.add_row_button.setEnabled(False)
            self.delete_row_button.setEnabled(False)
            self.add_column_button.setEnabled(False)
            self.delete_column_button.setEnabled(False)
            self.save_button.setEnabled(False)
        elif self.access_level == 'Редактирование данных':
            self.add_row_button.setEnabled(False)
            self.delete_row_button.setEnabled(False)
            self.add_column_button.setEnabled(False)
            self.delete_column_button.setEnabled(False)
            self.save_button.setEnabled(True)
        elif self.access_level == 'Редактирование БД':
            self.add_row_button.setEnabled(True)
            self.delete_row_button.setEnabled(True)
            self.add_column_button.setEnabled(True)
            self.delete_column_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def open_db(self):
        if self.db_connection:
            return

        if hasattr(self, 'database_path') and self.database_path:
            try:
                self.db_connection = sqlite3.connect(self.database_path)
                print(f"Connected to database: {self.database_path}")
                self.load_data()
            except Exception as e:
                print(f"Error connecting to database: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {e}")
        else:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getOpenFileName(self, "Открыть базу данных", "",
                                                       "SQLite Files (*.db);;All Files (*)", options=options)
            if file_name:
                self.database_path = file_name
                try:
                    self.db_connection = sqlite3.connect(self.database_path)
                    print(f"Connected to database: {self.database_path}")
                    self.load_data()
                except Exception as e:
                    print(f"Error connecting to database: {e}")
                    QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {e}")

    def load_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("Available tables:")
        for table in tables:
            print(table[0])

        self.tab_widget.clear()
        for table in tables:
            table_name = table[0]
            if table_name in self.excluded_tables:
                print(f"Пропуск таблицы '{table_name}', так как она в списке исключённых.")
                continue

            scroll_area = QScrollArea()
            table_widget = QTableWidget()
            scroll_area.setWidget(table_widget)
            scroll_area.setWidgetResizable(True)
            self.tab_widget.addTab(scroll_area, table_name)
            self.load_table_data(table_widget, table_name)

    def load_table_data(self, table_widget, table_name):
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        headers = [description[0] for description in cursor.description]
        self.filter_column_combo.clear()
        self.filter_column_combo.addItem("Выберите столбец")
        self.filter_column_combo.addItems(headers)

        table_widget.setColumnCount(len(headers))
        table_widget.setRowCount(len(data))
        table_widget.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                table_widget.setItem(row_idx, col_idx, item)

    def apply_filter(self):
        filter_column = self.filter_column_combo.currentText()
        condition = self.filter_condition_combo.currentText()
        filter_values = self.filter_line_edit.text().strip()

        if filter_column == "Выберите столбец" or not filter_values:
            QMessageBox.warning(self, "Предупреждение", "Выберите столбец и введите значения для фильтрации.")
            return

        filter_values_list = [value.strip() for value in filter_values.split(',') if value.strip()]

        if not filter_values_list:
            QMessageBox.warning(self, "Предупреждение", "Введите хотя бы одно значение для фильтрации.")
            return

        cursor = self.db_connection.cursor()

        for i in range(self.tab_widget.count()):
            current_table = self.tab_widget.tabText(i)
            query = f"SELECT * FROM {current_table} WHERE "
            conditions = []

            for value in filter_values_list:
                if condition == "содержит":
                    conditions.append(f"{filter_column} LIKE ?")
                    value = f"%{value}%"
                elif condition == "равно":
                    conditions.append(f"{filter_column} = ?")
                elif condition == "начинается с":
                    conditions.append(f"{filter_column} LIKE ?")
                    value = f"{value}%"
                elif condition == "заканчивается на":
                    conditions.append(f"{filter_column} LIKE ?")
                    value = f"%{value}"

            full_query = query + " OR ".join(conditions)

            try:
                cursor.execute(full_query, filter_values_list * len(conditions))
                filtered_data = cursor.fetchall()

                scroll_area = self.tab_widget.widget(i)
                table_widget = scroll_area.widget()
                headers = [description[0] for description in cursor.description]
                table_widget.setColumnCount(len(headers))
                table_widget.setRowCount(len(filtered_data))
                table_widget.setHorizontalHeaderLabels(headers)

                for row_idx, row_data in enumerate(filtered_data):
                    for col_idx, value in enumerate(row_data):
                        item = QTableWidgetItem(str(value))
                        table_widget.setItem(row_idx, col_idx, item)

            except sqlite3.Error as e:
                print(f"Error filtering table '{current_table}': {e}")

    def reset_filter(self):
        self.filter_column_combo.setCurrentIndex(0)
        self.filter_line_edit.clear()

        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index < 0:
            return

        current_table = self.tab_widget.tabText(current_tab_index)
        table_widget = self.tab_widget.widget(current_tab_index).widget()
        self.load_table_data(table_widget, current_table)

        QMessageBox.information(self, "Фильтр", f"Фильтры сброшены для таблицы '{current_table}'.")

    def add_row(self):
        self.current_table = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите таблицу.")
            return

        cursor = self.db_connection.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns_info = cursor.fetchall()

        row_data = []

        for column in columns_info:
            column_name = column[1]
            not_null = column[3]

            default_value = "Default Value"
            if not_null:
                row_data.append(default_value)
            else:
                row_data.append(None)

        placeholders = ', '.join(['?'] * len(row_data))

        try:
            cursor.execute(f"INSERT INTO {self.current_table} VALUES ({placeholders})", row_data)
            self.db_connection.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", "Строка успешно добавлена.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось добавить строку: {e}")

    def delete_row(self):
        self.current_table = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите таблицу.")
            return

        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return
        table_widget = current_tab.widget()

        selected_rows = table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите строки для удаления.")
            return

        cursor = self.db_connection.cursor()

        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns_info = cursor.fetchall()

        primary_key_column = None
        for column in columns_info:
            if column[5]:
                primary_key_column = column[1]
                break

        if not primary_key_column:
            QMessageBox.critical(self, "Ошибка", f"Таблица '{self.current_table}' не имеет первичного ключа.")
            return

        for row in selected_rows:
            row_index = row.row()

            primary_key_value = table_widget.item(row_index, columns_info.index(
                [col for col in columns_info if col[1] == primary_key_column][0])).text()

            try:
                cursor.execute(f"DELETE FROM {self.current_table} WHERE {primary_key_column} = ?", (primary_key_value,))
                self.db_connection.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось удалить строку: {e}")
                return

        self.load_data()
        QMessageBox.information(self, "Успех", "Строка успешно удалена.")

    def add_column(self):
        new_column_name = self.new_column_name_edit.text().strip()
        if not new_column_name:
            QMessageBox.warning(self, "Предупреждение", "Введите имя нового столбца.")
            return

        try:
            cursor = self.db_connection.cursor()
            self.current_table = self.tab_widget.tabText(self.tab_widget.currentIndex())
            cursor.execute(f"ALTER TABLE {self.current_table} ADD COLUMN {new_column_name} TEXT")
            self.load_data()
            self.new_column_name_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить столбец: {e}")

    def delete_column(self):
        self.current_table = self.tab_widget.tabText(self.tab_widget.currentIndex())
        if not self.current_table:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите таблицу.")
            return

        column_to_delete = self.new_column_name_edit.text().strip()
        if not column_to_delete:
            QMessageBox.warning(self, "Предупреждение", "Введите имя столбца для удаления.")
            return

        cursor = self.db_connection.cursor()

        try:
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns_info = cursor.fetchall()
            columns = [column[1] for column in columns_info]

            if column_to_delete not in columns:
                QMessageBox.warning(self, "Предупреждение", f"Столбец '{column_to_delete}' не существует в таблице.")
                return

            cursor.execute(f"ALTER TABLE {self.current_table} DROP COLUMN {column_to_delete}")

            self.db_connection.commit()

            self.load_data()
            self.new_column_name_edit.clear()

            QMessageBox.information(self, "Успех", f"Столбец '{column_to_delete}' успешно удалён.")
        except sqlite3.Error as e:
            self.db_connection.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить столбец: {e}")
        finally:
            cursor.close()

    def save_changes(self):
        if not self.db_connection:
            return

        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index < 0:
            return

        current_table_name = self.tab_widget.tabText(current_tab_index)
        current_table_widget = self.tab_widget.widget(current_tab_index).widget()

        cursor = self.db_connection.cursor()
        headers = [current_table_widget.horizontalHeaderItem(col_idx).text() for col_idx in
                   range(current_table_widget.columnCount())]

        try:
            cursor.execute(f"DELETE FROM {current_table_name}")

            for row in range(current_table_widget.rowCount()):
                values = []
                for col in range(current_table_widget.columnCount()):
                    item = current_table_widget.item(row, col)
                    values.append(item.text() if item else None)

                if 'user_id' in headers:
                    user_id_index = headers.index('user_id')
                    if values[user_id_index] is None:
                        values[user_id_index] = self.get_next_id(cursor, 'user_id', current_table_name)

                if 'chat_id' in headers:
                    chat_id_index = headers.index('chat_id')
                    if values[chat_id_index] is None:
                        values[chat_id_index] = self.get_next_id(cursor, 'chat_id', current_table_name)

                if any(value is not None for value in values):
                    placeholders = ", ".join(["?"] * len(values))
                    cursor.execute(
                        f"INSERT INTO {current_table_name} ({', '.join(headers)}) VALUES ({placeholders})", values)

            self.db_connection.commit()
            QMessageBox.information(self, "Успех", "Изменения сохранены в базе данных.")
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            QMessageBox.warning(self, "Ошибка",
                                f"Не удалось сохранить строку из-за нарушения уникальности.\nОшибка: {e}")
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении данных: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

    def get_next_id(self, cursor, column_name, table_name):
        cursor.execute(f"SELECT MAX({column_name}) FROM {table_name}")
        max_id = cursor.fetchone()[0]
        return (max_id + 1) if max_id is not None else 1

    def validate_data(self, data, column_type):
        if column_type.upper() == 'INTEGER':
            try:
                return int(data), True
            except ValueError:
                return None, False
        elif column_type.upper() == 'REAL':
            try:
                return float(data), True
            except ValueError:
                return None, False
        elif column_type.upper() == 'TEXT':
            return data, True
        else:
            return data, True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = DBEditor()
    editor.show()
    sys.exit(app.exec_())
