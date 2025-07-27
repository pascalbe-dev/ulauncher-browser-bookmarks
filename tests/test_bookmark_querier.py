import unittest
from querier import BookmarkQuerier

bookmarks = {
    "type": "folder",
    "name": "root",
    "children": [
        {
            "type": "bookmark",
            "name": "git tutorial",
            "url": "https://git.org"
        },
        {
            "type": "folder",
            "name": "Python",
            "children": [
                {
                    "type": "bookmark",
                    "name": "Documentation",
                    "url": "https://docs.python.org"
                },
                {
                    "type": "bookmark",
                    "name": "Python Tutorial",
                    "url": "https://learn.python.org"
                },
                {
                    "type": "folder",
                    "name": "Advanced",
                    "children": [
                        {
                            "type": "bookmark",
                            "name": "Documentation and Tutorial - python",
                            "url": "https://documentation.python.org"
                        },
                        {
                            "type": "bookmark",
                            "name": "Python Tricks Tutorial",
                            "url": "https://realpython.com"
                        },
                        {
                            "type": "bookmark",
                            "name": "Zen of Python",
                            "url": "https://peps.python.org/pep-0020/"
                        }
                    ]
                }
            ]
        },
        {
            "type": "folder",
            "name": "Typescript",
            "children": [
                {
                    "type": "bookmark",
                    "name": "Documentation",
                    "url": "https://docs.typescript.org"
                },
                {
                    "type": "bookmark",
                    "name": "Typescript Tutorial",
                    "url": "https://learn.typescript.org"
                },
                {
                    "type": "folder",
                    "name": "Advanced",
                    "children": [
                        {
                            "type": "bookmark",
                            "name": "Documentation and Tutorial",
                            "url": "https://documentation.typescript.org"
                        },
                        {
                            "type": "bookmark",
                            "name": "Typescript Tricks Tutorial",
                            "url": "https://typescript.org"
                        },
                        {
                            "type": "bookmark",
                            "name": "Zen of Typescript",
                            "url": "https://notfound.com"
                        }
                    ]
                }

            ]
        }
    ]
}
class TestBookmarkQuerierNoFilterByFolders(unittest.TestCase):
    def setUp(self):
        self.querier = BookmarkQuerier()

    def test_matches_any_bookmark_that_contains_query_words(self):
        matches = []
        self.querier.search(bookmarks, "documentation", matches)
        self.assertEqual(len(matches), 4)
        self.assertEqual(matches[0]["name"], "Documentation")
        self.assertEqual(matches[0]["url"], "https://docs.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[1]["url"], "https://documentation.python.org")
        self.assertEqual(matches[2]["name"], "Documentation")
        self.assertEqual(matches[2]["url"], "https://docs.typescript.org")
        self.assertEqual(matches[3]["name"], "Documentation and Tutorial")
        self.assertEqual(matches[3]["url"], "https://documentation.typescript.org")

        matches = []
        self.querier.search(bookmarks, "documentation tutorial", matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[0]["url"], "https://documentation.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial")
        self.assertEqual(matches[1]["url"], "https://documentation.typescript.org")

        matches = []
        self.querier.search(bookmarks, "tutorial", matches)
        self.assertEqual(len(matches), 7)
        self.assertEqual(matches[0]["name"], "git tutorial")
        self.assertEqual(matches[1]["name"], "Python Tutorial")


    def test_doesnot_filter_by_folders(self):
        matches = []
        self.querier.search(bookmarks, "advanced documentation", matches)
        self.assertEqual(len(matches), 0)

        matches = []
        self.querier.search(bookmarks, "python advanced", matches)
        self.assertEqual(len(matches), 0)

        matches = []
        self.querier.search(bookmarks, "advanced tutorial", matches)
        self.assertEqual(len(matches), 0)

    def test_query_max_matches(self):
        # Create a bookmark structure with many entries
        many_bookmarks = {
                "type": "folder",
                "name": "root",
                "children": [
                    {
                        "type": "bookmark",
                        "name": f"Test {i}",
                        "url": f"https://test{i}.com"
                        } for i in range(15)
                    ]
                }

        matches = []
        self.querier.search(many_bookmarks, "Test", matches)
        self.assertEqual(len(matches), 10)  # Should stop at max_matches_len 

class TestBookmarkQuerierFilterByFolders(unittest.TestCase):
    def setUp(self):
        self.querier = BookmarkQuerier(filter_by_folders=True)

    def test_matches_any_bookmark_that_contains_query_words(self):
        matches = []
        self.querier.search(bookmarks, "documentation", matches)
        self.assertEqual(len(matches), 4)
        self.assertEqual(matches[0]["name"], "Documentation")
        self.assertEqual(matches[0]["url"], "https://docs.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[1]["url"], "https://documentation.python.org")
        self.assertEqual(matches[2]["name"], "Documentation")
        self.assertEqual(matches[2]["url"], "https://docs.typescript.org")
        self.assertEqual(matches[3]["name"], "Documentation and Tutorial")
        self.assertEqual(matches[3]["url"], "https://documentation.typescript.org")

        matches = []
        self.querier.search(bookmarks, "documentation tutorial", matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[0]["url"], "https://documentation.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial")
        self.assertEqual(matches[1]["url"], "https://documentation.typescript.org")

        matches = []
        self.querier.search(bookmarks, "tutorial", matches)
        self.assertEqual(len(matches), 7)
        self.assertEqual(matches[0]["name"], "git tutorial")
        self.assertEqual(matches[1]["name"], "Python Tutorial")

    def test_query_max_matches(self):
        # Create a bookmark structure with many entries
        many_bookmarks = {
            "type": "folder",
            "name": "root",
            "children": [
                {
                    "type": "bookmark",
                    "name": f"Test {i}",
                    "url": f"https://test{i}.com"
                } for i in range(15)
            ]
        }

        matches = []
        self.querier.search(many_bookmarks, "Test", matches)
        self.assertEqual(len(matches), 10)  # Should stop at max_matches_len 
    
    def test_search_matches_parent_folder(self):
        matches = []
        self.querier.search(bookmarks, "python documentation", matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["name"], "Documentation")
        self.assertEqual(matches[0]["url"], "https://docs.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[1]["url"], "https://documentation.python.org")

        # Make sure to consider URL matches as well
        matches = []
        self.querier.search(bookmarks, "python learn", matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Python Tutorial")
        self.assertEqual(matches[0]["url"], "https://learn.python.org")
    
    def test_filter_by_parent_tree(self):
        # Sanity check
        matches = []
        self.querier.search(bookmarks, "advanced", matches)
        self.assertEqual(len(matches), 6)

        matches = []
        self.querier.search(bookmarks, "python advanced", matches)
        self.assertEqual(len(matches), 3)
        matches = []
        self.querier.search(bookmarks, "typescript advanced", matches)
        self.assertEqual(len(matches), 3)
    
    def test_filter_by_children_and_grand_children(self):
        # Test that it matches when both parent and bookmark match
        # Should match: python/* && python/Advanced/*
        matches = []
        self.querier.search(bookmarks, "python tutorial", matches)
        self.assertEqual(len(matches), 3)
        self.assertEqual(matches[0]["name"], "Python Tutorial")
        self.assertEqual(matches[0]["url"], "https://learn.python.org")
        self.assertEqual(matches[1]["name"], "Documentation and Tutorial - python")
        self.assertEqual(matches[1]["url"], "https://documentation.python.org")
        self.assertEqual(matches[2]["name"], "Python Tricks Tutorial")
        self.assertEqual(matches[2]["url"], "https://realpython.com")

    def test_filter_by_bookmark_name_and_parent_dont_match(self):
        # Test that it doesn't match when neither parent nor bookmark match
        matches = []
        self.querier.search(bookmarks, "java", matches)
        self.assertEqual(len(matches), 0) 
        self.querier.search(bookmarks, "java docs", matches)
        self.assertEqual(len(matches), 0) 
