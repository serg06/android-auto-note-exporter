from __future__ import annotations

from datetime import datetime as dt


class NoteListItemData:
    def __init__(self, title='', date=dt.now()):
        self.title: str = title
        self.date: dt = date


class NotePageData:
    def __init__(self, title='', text=''):
        self.title: str = title
        self.text: str = text


class NoteData:
    def __init__(self, title='', text='', date=dt.now()):
        self.title = title
        self.text = text
        self.date = date

    def __eq__(self, other: NoteData):
        return self.title == other.title and self.text == other.text and self.date == other.date

    def __hash__(self):
        return hash((self.title, self.text, self.date))

    def __str__(self):
        return f'({self.date}) {self.title}'

    def __repr__(self):
        return str(self)

    def toJson(self):
        return {
            'title': self.title,
            'text': self.text,
            'date': self.date.isoformat()
        }
