from PyQt6.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("Hello PyQt6 🚀")
label.resize(200, 100)
label.show()
app.exec()