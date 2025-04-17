from typing import Any, List, Dict

class BookmarkQuerier:
    def __init__(self, filter_by_folders: bool = False) -> None:
        """
        Initializes the BookmarkQuerier class.
        Parameters:
            filter_by_folders (bool): Whether to filter by folders
        """
        self.filter_by_folders = filter_by_folders
        self.matches_len = 0
        self.max_matches_len = 10

    def search(
            self, bookmark_entry: Dict[str, Any], query: str, matches: List[Dict[str, Any]], 
            parent_name: str = ""
            ) -> None:
        """
        Recursively edits the matches variable with bookmark entries that match the query.
        Matches if query terms are found in either name, URL, or parent folder name.

        Parameters:
            bookmark_entry (Dict[str, Any]): The bookmark entry to search
            query (str): The query
            matches (List[Dict[str, Any]]): The list to append matches to
            parent_name (str, optional): The name of the parent folder
        """
        if self.matches_len >= self.max_matches_len:
            return

        if bookmark_entry["type"] == "folder":
            for child_bookmark_entry in bookmark_entry["children"]:
                self.search(child_bookmark_entry, query, matches, bookmark_entry["name"])
        else:
            sub_queries = query.split(" ")
            bookmark_title = bookmark_entry["name"]
            bookmark_url = bookmark_entry.get("url", "")
            
            # Create search text that includes parent folder name, bookmark name and URL
            search_text = f"{bookmark_title} {bookmark_url}"
            if parent_name and self.filter_by_folders:
                search_text = f"{parent_name} {search_text}"

            if not self.contains_all_substrings(search_text, sub_queries):
                return

            matches.append(bookmark_entry)
            self.matches_len += 1

    def contains_all_substrings(self, text: str, substrings: List[str]) -> bool:
        """
        Check if all substrings are in the text

        Parameters:
            text (str): The text to match against
            substrings (List[str]): The substrings to check

        Returns:
            bool: True if all substrings are in the text, False otherwise
        """
        for substring in substrings:
            if substring.lower() not in text.lower():
                return False
        return True
