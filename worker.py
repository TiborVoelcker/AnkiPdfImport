from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt, QSize
from PyQt5.QtGui import QPixmap
from pdf2image import convert_from_path
import tempfile
from datetime import datetime
from GenAnki import writeCards
import os


def sort_pictures(questions, answers):
    cards = []
    for i, row in enumerate(questions):
        answers[i].reverse()
        for j, q in enumerate(row):
            cards.append((q, answers[i][j]))
    return cards


def crop(image, sections):
    images = []
    for section_row in sections:
        row = []
        for section in section_row:
            coords = section.getCoords()
            coords = (coords[0]*image.width, coords[1]*image.height, coords[2]*image.width, coords[3]*image.height)
            row.append(image.crop(coords))
        images.append(row)
    return images


class Worker(QObject):
    converted = pyqtSignal(list)
    saved = pyqtSignal()

    @pyqtSlot()
    def convertPdf(self, filename, path, scale=QSize(870, 1100)):
        paths = convert_from_path(filename, dpi=100, output_folder=path, fmt="jpeg", paths_only=True)
        pixmaps = []
        for p in paths:
            pix = QPixmap(p)
            pixmaps.append(pix.scaled(scale, Qt.IgnoreAspectRatio, Qt.FastTransformation))
        self.converted.emit(pixmaps)

    @pyqtSlot()
    def saveCards(self, path, data, deck):
        ((q_page, q_sec), (a_page, a_sec)) = data
        q_img = convert_from_path(path, dpi=200, fmt="jpeg", first_page=q_page+1, last_page=q_page+1)[0]
        a_img = convert_from_path(path, dpi=200, fmt="jpeg", first_page=a_page+1, last_page=a_page+1)[0]
        cards = sort_pictures(crop(q_img, q_sec), crop(a_img, a_sec))

        filename = os.path.splitext(os.path.basename(path))[0]
        with tempfile.TemporaryDirectory() as tempdir:
            for i, card in enumerate(cards):
                fp_front = os.path.join(tempdir, f"{filename}_{q_page}_{i}.jpg")
                fp_back = os.path.join(tempdir, f"{filename}_{a_page}_{i}.jpg")
                card[0].save(fp_front, format="JPEG")
                card[1].save(fp_back, format="JPEG")
                cards[i] = (fp_front, fp_back)
            writeCards(cards, deck)

        self.saved.emit()
