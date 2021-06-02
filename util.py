from __future__ import annotations

import copy
from typing import Dict, Callable, List, Optional, Set

from com.dtmilano.android.viewclient import ViewClient, View, UiScrollable


def traverseListViewChildren(vc: ViewClient, listViewFinder: Callable[[ViewClient], View],
                             transform: Callable[[View], None], listItemHasher: Callable[[View], int],
                             listItemVisibilityChecker: Callable[[View], bool]):
    """
    Iterate all children of a ListView. May not work correctly if list items are too big.

    :param vc:
        The ViewClient.
    :param listViewFinder:
        A function which takes the ViewClient and returns the ListView.
    :param transform:
        The function to apply to every child element.
    :param listItemHasher:
        A functon which takes a child element and returns a unique hash. It's used to check equality between two
            child elements. This fixes two issues:
                - Prevents from accidentally calling trasform on the same item twice (if scrolling too slow).
                - Prevents from skipping an item (if scrolling too fast.)
    :param listItemVisibilityChecker:
        A function which takes a child element and returns true/false if it's fully on-screen or not. It's used to make
            sure we don't look at a child that has already been partially hidden (and partially disabled), or one which
            hasn't fully come into view yet.
    :return:
    """

    # Scroll to start
    listView = listViewFinder(vc)
    fastScroller: UiScrollable = copy.copy(listView.uiScrollable)
    fastScroller.duration = 80
    fastScroller.swipeDeadZonePercentage = 0
    fastScroller.flingToBeginning(maxSwipes=10)

    # Reload UI
    vc.dump()

    # Iterate children
    last_child: Optional[View] = None
    reached_end = False
    visited_hashes: Set[int] = set()

    while not reached_end:
        # Get list view
        listView = listViewFinder(vc)

        # NOTE: If scrolls at wrong speed, adjust this.
        slowScroller: UiScrollable = copy.copy(listView.uiScrollable)
        slowScroller.duration = 800
        slowScroller.swipeDeadZonePercentage = 0.15

        # Grab children on screen
        children: List[View] = listView.getChildren()

        # Remove ones that aren't fully visible
        children = [c for c in children if listItemVisibilityChecker(c)]

        # Remove ones we've already done
        if last_child is not None:
            children_hashes = [listItemHasher(c) for c in children]
            last_child_hash = listItemHasher(last_child)
            if last_child_hash not in children_hashes:
                raise Exception(
                    "You're scrolling too fast and missing children, please increase scroller's duration or swipe dead zone percentage.")

            idx = children_hashes.index(last_child_hash)
            children = children[idx + 1:]

        # If list empty, we've finished (or we scroll too slowly lol.
        if len(children) == 0:
            reached_end = True
            break

        # Iterate
        for child in children:
            assert isinstance(child, View)
            child_hash = listItemHasher(child)
            if child_hash in visited_hashes:
                raise Exception('Encountered same hash from multiple children. Is your hash function truly unique?')

            transform(child)
            last_child = child
            visited_hashes.add(child_hash)

        # Give it a sec to finish animation before flinging it forwards again
        vc.dump()

        # Scroll
        slowScroller.flingForward()

        # Reload UI
        vc.dump()


def findViewWithPredicate(vc: ViewClient, pred: Callable[[View], bool]) -> Optional[View]:
    view_ids: Dict[str, View] = vc.getViewIds()

    for k, v in view_ids.items():
        if pred(v):
            return v

    return None


def findViewWithPredicateOrRaise(vc: ViewClient, pred: Callable[[View], bool], msg: str = None) -> View:
    result = findViewWithPredicate(vc, pred)
    if result is None:
        if msg is None:
            msg = 'Cannot find view with predicate.'
        raise Exception(msg)
    else:
        return result
