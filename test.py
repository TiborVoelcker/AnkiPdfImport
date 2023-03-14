import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pathlib import Path
from ImportWindow import ImportWindow


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        layout = QVBoxLayout()

        self.btn = QPushButton("Import Cards from PDF")
        self.btn.clicked.connect(self.getfile)
        layout.addWidget(self.btn)

        self.setLayout(layout)
        self.setWindowTitle("Test")

    def getfile(self):
        downloads = str(Path.home() / "Downloads")
        filename, _ = QFileDialog.getOpenFileName(self, "Import PDF", downloads, "PDF (*.pdf)")
        if filename:
            self.setCursor(Qt.WaitCursor)
            ImportWindow(self, filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
