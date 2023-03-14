from aqt import mw
from datetime import datetime


def writeCards(cards, deck):
    today = datetime.today().strftime("%Y_%M_%d")

    basic = mw.col.models.byName("Basic")

    for i, card in enumerate(cards):
        (question, answer) = card
        # note = mw.col.new_note(basic)

        # legacy
        mw.col.models.setCurrent(basic)
        note = mw.col.newNote(False)

        new_filename = mw.col.media.add_file(question)
        note["Front"] = f'<img src="{new_filename}">'

        new_filename = mw.col.media.add_file(answer)
        note["Back"] = f'<img src="{new_filename}">'

        mw.col.add_note(note, deck.id)
