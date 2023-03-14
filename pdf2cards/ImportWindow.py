from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from .GraphicsRectItem import GraphicsRectItem
from .worker import Worker
from aqt import mw


class ImportWindow(QDialog):
    def __init__(self, parent=None, filename=None):
        self.filename = filename
        self.tempdir = QTemporaryDir()
        assert self.tempdir.isValid(), "Temporary Directory is invalid!"
        self.rows = 4
        self.columns = 2
        self.current_page = 0
        self.questions = ()
        self.decks = mw.col.decks.all_names_and_ids()
        super(ImportWindow, self).__init__(parent)

        self.pixmaps = []
        self.size = QSize(870, 1100)
        self.work = Worker()
        self.thread = QThread()
        self.work.moveToThread(self.thread)
        self.work.converted.connect(self.pdfConverted)
        self.thread.started.connect(lambda: self.work.convertPdf(filename, self.tempdir.path(), self.size))
        self.setCursor(Qt.WaitCursor)
        self.thread.start()

        self.initGUI()

        self.show()

    def initGUI(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(QPointF(0, 0), QSizeF(self.size)))
        self.pixmap = self.scene.addPixmap(QPixmap(self.size))

        self.rect = GraphicsRectItem(87, 110, 696, 880, handleSize=50, rows=self.rows, columns=self.columns)
        self.scene.addItem(self.rect)

        self.view = QGraphicsView(self.scene)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

        self.spinbox_row = QSpinBox()
        self.spinbox_row.setValue(self.rows)
        self.spinbox_column = QSpinBox()
        self.spinbox_column.setValue(self.columns)
        self.spinbox_row.valueChanged.connect(self.valuechange)
        self.spinbox_column.valueChanged.connect(self.valuechange)
        self.spinbox_row.setRange(1, 10)
        self.spinbox_column.setRange(1, 10)

        self.button_next = QPushButton()
        self.button_next.clicked.connect(lambda: self.pagechange(self.current_page + 1))
        self.button_next.setText(">>")
        self.button_prev = QPushButton()
        self.button_prev.clicked.connect(lambda: self.pagechange(self.current_page - 1))
        self.button_prev.setText("<<")
        self.spinbox_page = QSpinBox()
        self.spinbox_page.setValue(self.current_page + 1)
        self.spinbox_page.valueChanged.connect(lambda: self.pagechange(self.spinbox_page.value() - 1))

        self.combobox = QComboBox()
        self.combobox.addItems([str(deck.name) for deck in self.decks])

        self.button_save = QPushButton()
        self.button_save.clicked.connect(self.save)
        self.button_save.setText("Save")
        self.button_save.setEnabled(False)

        self.button_undo = QPushButton()
        self.button_undo.clicked.connect(self.undo)
        self.button_undo.setText("Undo")

        self.button_close = QPushButton()
        self.button_close.clicked.connect(self.close)
        self.button_close.setText("Close")

        self.info = QLabel("Choose Questions")
        self.info.setAlignment(Qt.AlignHCenter)

        layout_main = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_bottom = QGridLayout()
        layout_main.addWidget(self.info)
        layout_main.addLayout(layout_top)
        layout_top.addStretch()
        layout_top.addWidget(self.button_prev)
        layout_top.addWidget(self.spinbox_page)
        layout_top.addWidget(self.button_next)
        layout_top.addStretch()
        layout_main.addWidget(self.view)
        layout_main.addLayout(layout_bottom)
        layout_bottom.addWidget(QLabel("Rows"), 1, 0)
        layout_bottom.addWidget((QLabel("Columns")), 2, 0)
        layout_bottom.addWidget(self.spinbox_row, 1, 1)
        layout_bottom.addWidget(self.spinbox_column, 2, 1)
        layout_bottom.setColumnStretch(2, 1)
        label = QLabel("Add to Deck:")
        label.setAlignment(Qt.AlignRight)
        layout_bottom.addWidget(label, 0, 1, 1, 2)
        layout_bottom.addWidget(self.combobox, 0, 3, 1, 2)
        layout_bottom.addWidget(self.button_save, 1, 3)
        layout_bottom.addWidget(self.button_undo, 1, 4)
        layout_bottom.addWidget(self.button_close, 2, 4)

        self.setLayout(layout_main)
        self.setWindowTitle("Import Cards from PDF")

    def resizeEvent(self, event):
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def valuechange(self):
        self.rect.setRows(self.spinbox_row.value())
        self.rect.setColumns(self.spinbox_column.value())

    def pagechange(self, i):
        if i < 0:
            i = len(self.pixmaps)-1
        elif i >= len(self.pixmaps):
            i = 0
        self.current_page = i
        self.spinbox_page.setValue(i+1)
        try:
            self.pixmap.setPixmap(self.pixmaps[i])
        except IndexError:
            pass

    def save(self):
        data = (self.current_page, self.rect.getSections())
        self.pagechange(self.current_page + 1)
        try:
            deck = next(filter(lambda i: i.name == self.combobox.currentText(), self.decks))
        except StopIteration:
            deck = False
        if not self.questions:
            self.questions = data
            self.info.setText("Choose Answers for selected Questions")
            self.spinbox_row.setEnabled(False)
            self.spinbox_column.setEnabled(False)
            self.combobox.setEnabled(False)
            self.button_undo.setEnabled(True)
        else:
            self.button_save.setEnabled(False)
            self.button_save.setCursor(Qt.WaitCursor)

            self.work.saved.connect(self.saved)
            data = (self.questions, data)
            self.thread.started.connect(lambda: self.work.saveCards(self.filename, data, deck))
            self.thread.start()

            self.questions = ()
            self.info.setText("Choose Questions")
            self.spinbox_row.setEnabled(True)
            self.spinbox_column.setEnabled(True)
            self.combobox.setEnabled(True)
            self.button_undo.setEnabled(False)

    def undo(self):
        self.questions = ()
        self.info.setText("Choose Questions")
        self.spinbox_row.setEnabled(True)
        self.spinbox_column.setEnabled(True)
        self.combobox.setEnabled(True)
        self.button_undo.setEnabled(False)

    def pdfConverted(self, data):
        self.pixmaps = data
        self.thread.quit()
        self.thread.wait()
        self.thread.started.disconnect()
        self.pixmap.setPixmap(self.pixmaps[self.current_page])
        self.button_save.setEnabled(True)
        self.setCursor(Qt.ArrowCursor)

    def saved(self):
        self.thread.quit()
        self.thread.wait()
        try:
            self.thread.started.disconnect()
        except TypeError:
            pass
        self.button_save.setEnabled(True)
        self.button_save.setCursor(Qt.ArrowCursor)
