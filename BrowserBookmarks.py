import json
import logging
import os
from typing import List, Tuple, Dict, Union
from querier import BookmarkQuerier

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

# Swap the two logging configs to enable/disable logging to file debug.log in this directory
# logging.basicConfig(
#     filename=os.path.join(os.path.dirname(os.path.realpath(__file__)), "debug.log"),
#     level=logging.DEBUG,
# )
logging.basicConfig()
logger = logging.getLogger(__name__)

support_browsers = [
    "google-chrome",
    "chromium",
    "Brave-Browser",
    "BraveSoftware",
    "vivaldi",
]

browser_imgs = {
    "google-chrome": "images/chrome.png",
    "chromium": "images/chromium.png",
    "Brave-Browser": "images/brave.png",
    "BraveSoftware": "images/brave.png",
    "vivaldi": "images/vivaldi.png",
    "custom_path": "images/chromium.png",
}


class PreferencesEventListener(EventListener):
    def on_event(
        self,
        event: Union[PreferencesEvent, PreferencesUpdateEvent],
        extension: "BrowserBookmarks",
    ) -> None:
        """
        Listens for preference events and updates the extension preferences. Then updates the bookmarks paths.

        Parameters:
            event (Union[PreferencesEvent, PreferencesUpdateEvent]): The event to listen for
            extension (BrowserBookmarks): The extension to update
        """
        if isinstance(event, PreferencesUpdateEvent):
            if event.id == "keyword":
                return
            extension.preferences[event.id] = event.new_value
        elif isinstance(event, PreferencesEvent):
            assert isinstance(event.preferences, dict)
            extension.preferences = event.preferences
        # Could be optimized so it only refreshes the custom paths
        extension.bookmarks_paths = extension.find_bookmarks_paths()


class KeywordQueryEventListener(EventListener):
    def on_event(  # type: ignore
        self, event: KeywordQueryEvent, extension: "BrowserBookmarks"
    ) -> RenderResultListAction:
        items = extension.get_items(event.get_argument())
        return RenderResultListAction(items)


class BrowserBookmarks(Extension):
    max_matches_len = 10
    bookmarks_paths: List[Tuple[str, str]]

    def __init__(self):
        super(BrowserBookmarks, self).__init__()

        # Subscribe to preference events
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesEventListener())

        # Subscribe to keyword query events
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def find_bookmarks_paths(self) -> List[Tuple[str, str]]:
        """
        Searches for bookmarks by supported browsers and custom paths

        Returns:
            List[Tuple[str, str]]: A list of tuples containing the path to the bookmarks and the browser name
        """
        found_bookmarks: List[Tuple[str, str]] = []
        additional_browser_paths = self.preferences["additional_browser_paths"]

        for browser in support_browsers:
            potential_bookmark_paths = [
                "$HOME/.config/%s" % browser,
                "$HOME/snap/%s/current/.config/%s" % (browser, browser),
            ]

            found_bookmarks.extend(
                BrowserBookmarks.collect_bookmarks_paths(
                    potential_bookmark_paths, browser
                )
            )

        if additional_browser_paths:
            custom_paths: List[str] = list(additional_browser_paths.split(":"))
            logger.info(
                "Custom browser paths found, searching through: %s" % custom_paths
            )
            found_bookmarks.extend(
                BrowserBookmarks.collect_bookmarks_paths(custom_paths, "custom_path")
            )

        if len(found_bookmarks) == 0:
            logger.exception("No Bookmarks were found")

        return found_bookmarks

    @staticmethod
    def collect_bookmarks_paths(dirs: List[str], browser: str) -> List[Tuple[str, str]]:
        """
        Collects the paths to the bookmarks of the browser

        Parameters:
            dirs (List[str]): The directories to search in
            browser (str): The browser name (used to match the icon)

        Returns:
            List[Tuple[str, str]]: A list of tuples containing the path to the bookmarks and the browser name
        """
        grep_results: List[str] = []

        for command in dirs:
            f = os.popen("find %s | grep Bookmarks" % (command))
            grep_results.extend(f.read().split("\n"))
            f.close()

        if len(grep_results) == 0:
            logger.info("Path to the %s Bookmarks was not found" % browser)
            return []

        bookmarks_paths: List[Tuple[str, str]] = []
        for one_path in grep_results:
            if one_path.endswith("Bookmarks"):
                bookmarks_paths.append((one_path, browser))

        return bookmarks_paths

    def get_items(self, query: Union[str, None]) -> List[ExtensionResultItem]:
        """
        Returns a list of ExtensionResultItems for the query, which is rendered by Ulauncher

        Parameters:
            query (Union[str, None]): The query being searched

        Returns:
            List[ExtensionResultItem]: A list of ExtensionResultItems to be rendered
        """
        items: List[ExtensionResultItem] = []

        if query is None:
            query = ""

        logger.debug("Finding bookmark entries for query %s" % query)

        querier = BookmarkQuerier(
            filter_by_folders=self.preferences["filter_by_folders"],
        )

        for bookmarks_path, browser in self.bookmarks_paths:
            matches: List[Dict[str, str | Dict[str, str]]] = []

            with open(bookmarks_path) as data_file:
                data = json.load(data_file)
                querier.search(data["roots"]["bookmark_bar"], query, matches)
                querier.search(data["roots"]["synced"], query, matches)
                querier.search(data["roots"]["other"], query, matches)

            for bookmark in matches:
                bookmark_name: bytes = str(bookmark["name"]).encode("utf-8")
                bookmark_url: bytes = str(bookmark["url"]).encode("utf-8")
                item = ExtensionResultItem(
                    icon=browser_imgs.get(browser),
                    name=str(bookmark_name.decode("utf-8")),
                    description=str(bookmark_url.decode("utf-8")),
                    on_enter=OpenUrlAction(bookmark_url.decode("utf-8")),
                )
                items.append(item)

        return items
