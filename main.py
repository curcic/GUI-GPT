import sys
import openai
from PyQt5 import QtWidgets, QtGui
from datetime import datetime
import configparser

from test_api import is_api_key_valid


class Constants:
    MAX_TOKENS = 4000
    API_ENGINE = "text-davinci-003"


class ChatTab(QtWidgets.QWidget):
    def __init__(self, api_key):
        super().__init__()

        self.api_key = api_key

        self.chat_log = QtWidgets.QTextEdit(self)
        self.chat_log.setReadOnly(True)

        self.chat_input = QtWidgets.QLineEdit(self)
        self.chat_input.returnPressed.connect(self.send_message)

        send_icon = QtGui.QIcon("resources/send.png")
        self.send_button = QtWidgets.QPushButton(send_icon, "Send", self)
        self.send_button.clicked.connect(self.send_message)

        export_icon = QtGui.QIcon("resources/export.png")
        self.export_button = QtWidgets.QPushButton(export_icon, "Export Chat", self)
        self.export_button.clicked.connect(self.export_chat)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.chat_log)
        self.layout.addWidget(self.chat_input)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.export_button)
        self.layout.addLayout(button_layout)

        self.chat_input.setFocus()

    def send_message(self):
        message = self.chat_input.text()
        if not message:
            return
        self.chat_input.clear()
        self.chat_log.setReadOnly(True)
        self.chat_log.append(f"You: {message}")

        try:
            openai.api_key = self.api_key
            response = openai.Completion.create(
                engine=Constants.API_ENGINE,
                prompt=f"{message}\n",
                max_tokens=Constants.MAX_TOKENS,
                temperature=0,
            )
            response_text = response["choices"][0]["text"]
            self.chat_log.append(f"GPT-3: {response_text}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            QtWidgets.QMessageBox.critical(self, "API Error", error_msg)
            self.chat_log.append(error_msg)

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

        self.setWindowTitle("GUI-GPT-3")
        self.setGeometry(50, 50, 600, 400)
        self.setWindowIcon(QtGui.QIcon("resources/icon.png"))

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabCloseRequested.connect(self.check_tab_count)

        self.new_tab_button = QtWidgets.QPushButton("New Chat Tab", self)
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
