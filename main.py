import openai
import sys
from PyQt5 import QtWidgets, QtGui
from datetime import datetime

from test_api import is_api_key_valid


class ChatWindow(QtWidgets.QWidget):
    def get_api_key_from_text_box(self):
        api_key, ok = QtWidgets.QInputDialog.getText(self, "OpenAI API Key",
                                                     "Enter your OpenAI API key:", QtWidgets.QLineEdit.Normal, "")
        if ok:
            return api_key
        else:
            return None

    def __init__(self):
        super().__init__()

        self.api_key = self.get_api_key_from_text_box()

        if not is_api_key_valid(self.api_key):
            QtWidgets.QMessageBox.critical(self, "Invalid API Key", "The API key entered is invalid.")
            sys.exit()

        self.setWindowTitle("GUI-GPT-3")
        self.setGeometry(50, 50, 600, 400)

        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))

        self.chat_log = QtWidgets.QTextEdit(self)
        self.chat_log.setReadOnly(True)
        self.chat_input = QtWidgets.QLineEdit(self)

        send_icon = QtGui.QIcon('resources/send.png')
        self.send_button = QtWidgets.QPushButton(send_icon, "Send", self)
        self.send_button.clicked.connect(self.send_message)

        export_icon = QtGui.QIcon('resources/export.png')
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

        self.chat_input.clear()

        self.chat_log.setReadOnly(True)

        self.chat_log.append("You: " + message)

        openai.api_key = self.api_key
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"{message}\n",
                max_tokens=4000,
                temperature=0,
            )
            response_text = response["choices"][0]["text"]
            self.chat_log.append("GPT-3: " + response_text)
        except Exception as e:
            self.chat_log.append("Error: " + str(e))

        self.chat_log.setReadOnly(True)

    def export_chat(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        file_name = f"chat_{timestamp}.txt"

        try:
            with open(file_name, "w") as f:
                f.write(self.chat_log.toPlainText())
            QtWidgets.QMessageBox.information(self, "Export Successful", f"The chat has been exported to {file_name}.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Error",
                                           f"An error occurred while exporting the chat: {str(e)}")


app = QtWidgets.QApplication([])
window = ChatWindow()

app_icon = QtGui.QIcon('resources/icon.png')
app.setWindowIcon(app_icon)

window.show()
app.exec_()
