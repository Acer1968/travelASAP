from PySide6 import QtWidgets, QtUiTools, QtCore

# from travelasap import Trip

app = QtWidgets.QApplication()

# main = QtWidgets.QMainWindow()
# main.setWindowTitle("travelASAP FB poster")

ui_file = QtCore.QFile("publishingForm.ui")
loader = QtUiTools.QUiLoader()
main = loader.load(ui_file)
ui_file.close()


publishButton = main.findChild(QtWidgets.QPushButton, "pushButtonPublishNow")
postFBGenText = main.findChild(QtWidgets.QLabel, "postFBGenText")
termsInput = main.findChild(QtWidgets.QPlainTextEdit, "termsInput")
postFBGenText.setText("")


def publikuj():
    x = "".join((termsInput.toPlainText(), "na nic"))
    postFBGenText.setText("".join(("----Stisknuto ", str(x))))


publishButton.onClick = publikuj()

main.show()
app.exec()
