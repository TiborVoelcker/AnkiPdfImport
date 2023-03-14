import os, sys

folder = os.path.dirname(__file__)
libfolder = os.path.join(folder, "_vendor")
sys.path.insert(0, libfolder)

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from pathlib import Path
from .ImportWindow import ImportWindow

def getfile():
    downloads = str(Path.home() / "Downloads")
    filename, _ = QFileDialog.getOpenFileName(mw, "Import PDF", downloads, "PDF (*.pdf)")
    if filename:
        importWindow = ImportWindow(mw, filename)

# create a new menu item, "test"
import_pdf = QAction("Import PDF Cards", mw)
# set it to call testFunction when it's clicked
qconnect(import_pdf.triggered, getfile)
# and add it to the tools menu
mw.form.menuTools.addAction(import_pdf)