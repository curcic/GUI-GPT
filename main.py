import sys
import openai
from PyQt5 import QtWidgets, QtGui
from datetime import datetime
import configparser

from test_api import is_api_key_valid

class ChatTab(QtWidgets.QWidget):
    def __init__(self, api_key):
        super().__init__()

        self.selected_api = "gpt-4"
        self.api_key = api_key

        self.chat_log = QtWidgets.QTextEdit(self)
        self.chat_log.setReadOnly(True)

        self.chat_input = QtWidgets.QLineEdit(self)
        self.chat_input.returnPressed.connect(self.send_message)

        self.api_group_box = QtWidgets.QGroupBox("API")
        self.api_group_box_layout = QtWidgets.QVBoxLayout(self.api_group_box)

        self.api_gpt4_radio_button = QtWidgets.QRadioButton("GPT-4")
        self.api_gpt4_radio_button.setChecked(True)
        self.api_gpt4_radio_button.toggled.connect(self.api_radio_button_toggled)
        self.api_group_box_layout.addWidget(self.api_gpt4_radio_button)

        self.api_gpt35turbo_radio_button = QtWidgets.QRadioButton("GPT-3.5 Turbo")
        self.api_gpt35turbo_radio_button.toggled.connect(self.api_radio_button_toggled)
        self.api_group_box_layout.addWidget(self.api_gpt35turbo_radio_button)

        self.temperature_label = QtWidgets.QLabel("Temperature:")
        self.temperature_input = QtWidgets.QLineEdit("0.5", self)

        self.max_tokens_label = QtWidgets.QLabel("Max Tokens:")
        self.max_tokens_input = QtWidgets.QLineEdit("8192", self)

        send_icon = QtGui.QIcon("resources/send.png")
        self.send_button = QtWidgets.QPushButton(send_icon, "Send", self)
        self.send_button.clicked.connect(self.send_message)

        export_icon = QtGui.QIcon("resources/export.png")
        self.export_button = QtWidgets.QPushButton(export_icon, "Export Chat", self)
        self.export_button.clicked.connect(self.export_chat)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.chat_log)
        self.layout.addWidget(self.chat_input)
        self.layout.addWidget(self.api_group_box)
        self.layout.addWidget(self.temperature_label)
        self.layout.addWidget(self.temperature_input)
        self.layout.addWidget(self.max_tokens_label)
        self.layout.addWidget(self.max_tokens_input)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.export_button)
        self.layout.addLayout(button_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.chat_input.setFocus()

    def api_radio_button_toggled(self):
        if self.api_gpt4_radio_button.isChecked():
            self.selected_api = "gpt-4"
        elif self.api_gpt35turbo_radio_button.isChecked():
            self.selected_api = "gpt-3.5-turbo"

    def send_message(self):
        message = self.chat_input.text()
        if not message:
            return
        self.chat_input.clear()
        self.chat_log.setReadOnly(True)

        user_cursor = self.chat_log.textCursor()
        user_cursor.insertHtml("<span style='color: blue'>You: </span>")
        user_cursor.insertText(f"\n{message}\n\n")

        max_tokens_text = self.max_tokens_input.text()
        if self.api_gpt4_radio_button.isChecked():
            if (
                not max_tokens_text.isdigit()
                or int(max_tokens_text) < 0
                or int(max_tokens_text) > 8192
            ):
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Max Tokens",
                    "Please enter a valid max tokens value between 0 and 8192.",
                )
                return
        else:
            if (
                not max_tokens_text.isdigit()
                or int(max_tokens_text) < 0
                or int(max_tokens_text) > 4097
            ):
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Max Tokens",
                    "Please enter a valid max tokens value between 0 and 4097.",
                )
                return

        temperature_text = self.temperature_input.text()
        if float(temperature_text) < 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Invalid Temperature",
                "Please enter a valid temperature value greater than 0.",
            )
            return

        try:
            openai.api_key = self.api_key
            response = openai.Completion.create(
                engine=self.selected_api,
                prompt=f"{message}\n",
                max_tokens=int(max_tokens_text),
                temperature=float(temperature_text),
            )
            response_text = response["choices"][0]["text"]

            response_cursor = self.chat_log.textCursor()
            response_cursor.insertHtml("<span style='color: red'>GPT: </span>")
            response_cursor.insertText(f"{response_text}\n\n")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "API Error", error_msg)
            self.chat_log.append(f"{error_msg}\n\n")

        self.chat_log.setReadOnly(True)

    def export_chat(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"chat_{timestamp}.txt"

        try:
            with open(file_name, "w") as f:
                f.write(self.chat_log.toPlainText())
            QtWidgets.QMessageBox.information(
                self, "Export Successful", f"The chat has been exported to {file_name}."
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting the chat: {str(e)}",
            )


class ChatWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI-GPT")
        self.setGeometry(50, 50, 800, 600)
        self.setWindowIcon(QtGui.QIcon("resources/icon.png"))

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabCloseRequested.connect(self.check_tab_count)

        tab_icon = QtGui.QIcon("resources/tab.png")
        self.new_tab_button = QtWidgets.QPushButton(tab_icon, "New Chat Tab", self)
        self.new_tab_button.clicked.connect(self.add_new_tab)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        layout.addWidget(self.new_tab_button)

        self.tab_count = 0
        self.add_new_tab()

    def add_new_tab(self):
        self.tab_count += 1
        api_key = self.get_api_key()
        if api_key:
            chat_tab = ChatTab(api_key)
            index = self.tab_widget.addTab(chat_tab, f"Chat {self.tab_count}")
            self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        widget.deleteLater()
        self.tab_widget.removeTab(index)

    def check_tab_count(self):
        if self.tab_widget.count() == 0:
            QtWidgets.QApplication.quit()

    def get_api_key(self):
        config = configparser.ConfigParser()
        config.read("config.ini")
        api_key = config.get("API", "key", fallback="")
        while not api_key or not is_api_key_valid(api_key):
            api_key, ok = QtWidgets.QInputDialog.getText(
                self,
                "OpenAI API Key",
                "Enter your OpenAI API key:",
                QtWidgets.QLineEdit.Normal,
                "",
            )
            if not ok:
                sys.exit()
            if is_api_key_valid(api_key):
                config["API"] = {"key": api_key}
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid API Key",
                    "The API key you entered is invalid. Please try again.",
                )
        return api_key


app = QtWidgets.QApplication([])
window = ChatWindow()

app_icon = QtGui.QIcon("resources/icon.png")
app.setWindowIcon(app_icon)

window.show()
app.exec_()
