import openai
import sys
from PyQt5 import QtWidgets, QtGui

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

        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.chat_log = QtWidgets.QTextEdit(self)
        self.chat_log.setReadOnly(True)
        self.chat_input = QtWidgets.QLineEdit(self)

        send_icon = QtGui.QIcon('send.png')
        self.send_button = QtWidgets.QPushButton(send_icon, "Send", self)
        self.send_button.clicked.connect(self.send_message)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.chat_log)
        self.layout.addWidget(self.chat_input)
        self.layout.addWidget(self.send_button)

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


app = QtWidgets.QApplication([])
window = ChatWindow()

app_icon = QtGui.QIcon('icon.png')
app.setWindowIcon(app_icon)

window.show()
app.exec_()
