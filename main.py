from __future__ import annotations

import json
import os
import sys
from typing import List

import dateutil.parser
from com.dtmilano.android.viewclient import ViewClient, View

import util
from data import *

try:
    sys.path.insert(0, os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

"""
NOTE: To interact with the app, you must grant permissions with ADB.
- First, go to developer settings
- Make sure the following toggle is enabled:
    USB debugging (Security settings): Allow granting permissions and simulating input via USB debugging
"""

"""
If you're having issues, try uncommeting some of these debug statements.

from com.dtmilano.android.adb import adbclient
adbclient.DEBUG = True
adbclient.DEBUG_SHELL = True
adbclient.DEBUG_TOUCH = True
adbclient.DEBUG_LOG = True
adbclient.DEBUG_WINDOWS = True
adbclient.DEBUG_COORDS = True
adbclient.DEBUG_IMAGE_ROTATION = True
"""

"""
Element finders.
"""


def isNotesListView(view: View) -> bool:
    return view.getId().endswith('notesListView')


def getNotesListView(vc: ViewClient) -> View:
    result = util.findViewWithPredicateOrRaise(vc, isNotesListView,
                                               'Cannot find notes list view. Are you on home screen of notes app? (com.onto.notepad)')
    return result



def isNoteTitleFieldOnNotePage(view: View) -> bool:
    return view.getId().endswith('titleEdit')


def getNoteTitleFieldFromNotePage(vc: ViewClient) -> View:
    return util.findViewWithPredicateOrRaise(vc, isNoteTitleFieldOnNotePage, 'Cannot find notes title field.')


def isNoteContentFieldOnNotePage(view: View) -> bool:
    return view.getId().endswith('contentEdit')


def getNoteContentFieldFromNotePage(vc: ViewClient) -> View:
    return util.findViewWithPredicateOrRaise(vc, isNoteContentFieldOnNotePage, 'Cannot find notes content field.')


def isNoteListItemFullyVisible(noteListItem: View):
    return len(noteListItem.getChildren()) == 2


def parseNoteListItem(noteListItem: View) -> NoteListItemData:
    assert isNoteListItemFullyVisible(noteListItem)
    children = noteListItem.getChildren()
    title = children[0].getText()
    date_str = children[1].getText()
    date = dateutil.parser.parse(date_str)

    return NoteListItemData(title=title, date=date)


def parseNotePage(vc: ViewClient) -> NotePageData:
    title_field = getNoteTitleFieldFromNotePage(vc)
    content_field = getNoteContentFieldFromNotePage(vc)

    title = title_field.getText()
    content = content_field.getText()

    return NotePageData(title=title, text=content)


def hashNoteListItem(noteListItem: View) -> int:
    item = parseNoteListItem(noteListItem)
    return hash((item.title, item.date))


def getNoteDataForListItem(vc: ViewClient, notesListItem: View) -> NoteData:
    # Grab the date
    item = parseNoteListItem(notesListItem)

    # Open the note
    notesListItem.touch()
    vc.dump()

    # Grab the title and the text
    page = parseNotePage(vc)

    # Leave
    vc.device.shell('input keyevent KEYCODE_BACK')

    # Done! Reset UI one more time for the next user
    # Or don't, since it's slow AF.
    # vc.dump()
    result = NoteData(
        title=page.title,
        text=page.text,
        date=item.date
    )

    return result


def extractAllNoteData(vc: ViewClient) -> List[NoteData]:
    # Collect notes
    notes: List[NoteData] = []

    def extractNoteFn(notesListItem: View):
        note = getNoteDataForListItem(vc, notesListItem)
        notes.append(note)
        print(f'Extracted note: {note}')

        # Backup
        saveNoteData(notes, 'backup.json')

    notesListViewFinderFn = getNotesListView

    util.traverseListViewChildren(vc, notesListViewFinderFn, extractNoteFn, hashNoteListItem, isNoteListItemFullyVisible)

    return notes


def saveNoteData(notes: List[NoteData], destination_path):
    print(f'Saving {len(notes)} notes to {destination_path}...')

    with open(destination_path, 'w') as f:
        json.dump([n.toJson() for n in notes], f, indent=2)


def main():
    vc = ViewClient(*ViewClient.connectToDeviceOrExit())
    notes = extractAllNoteData(vc)
    saveNoteData(notes, 'result_success.json')


if __name__ == '__main__':
    main()
