import unittest
from querier import BookmarkQuerier

class TestBookmarkQuerierNoFilterByFolders(unittest.TestCase):
    def setUp(self):
        self.querier = BookmarkQuerier(
            filter_by_folders=False
        )

    def test_contains_all_substrings(self):
        test_bookmarks = {
            "type": "folder",
            "name": "root",
            "children": [
                {
                    "type": "bookmark",
                    "name": "Google Search",
                    "url": "https://google.com"
                },
                {
                    "type": "bookmark",
                    "name": "Google profile",
                    "url": "https://me.google.com"
                },
                {
                    "type": "folder",
                    "name": "Social Media",
                    "children": [
                        {
                            "type": "bookmark",
                            "name": "GitHub Profile",
                            "url": "https://github.com"
                        },
                        {
                            "type": "bookmark",
                            "name": "LinkedIn profile",
                            "url": "https://linkedin.com"
                        }
                    ]
                }
            ]
        }

        matches = []
        self.querier.search(test_bookmarks, "google", matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["name"], "Google Search")
        self.assertEqual(matches[1]["name"], "Google profile")

        matches = []
        self.querier.search(test_bookmarks, "profile", matches)
        self.assertEqual(len(matches), 3)

        matches = []
        self.querier.search(test_bookmarks, "google profile", matches)
        self.assertEqual(len(matches), 1)
    

class TestBookmarkQuerierFilterByFolders(unittest.TestCase):
    def setUp(self):
        # Sample bookmark structure for testing
        self.test_bookmarks = {
            "type": "folder",
            "name": "root",
            "children": [
                {
                    "type": "bookmark",
                    "name": "Google Search",
                    "url": "https://google.com"
                },
                {
                    "type": "folder",
                    "name": "Social Media",
                    "children": [
                        {
                            "type": "bookmark",
                            "name": "GitHub Profile",
                            "url": "https://github.com"
                        },
                        {
                            "type": "bookmark",
                            "name": "LinkedIn Page",
                            "url": "https://linkedin.com"
                        }
                    ]
                }
            ]
        }
        self.querier = BookmarkQuerier(
            filter_by_folders=True
        )

    def test_contains_all_substrings(self):
        # Test basic substring matching
        self.assertTrue(self.querier.contains_all_substrings("Hello World", ["hello", "world"]))
        self.assertTrue(self.querier.contains_all_substrings("Hello World", ["HeLLo", "WORLD"]))
        self.assertFalse(self.querier.contains_all_substrings("Hello World", ["hello", "python"]))
        self.assertTrue(self.querier.contains_all_substrings("Hello World", []))

    def test_query_single_word(self):
        matches = []
        self.querier.search(self.test_bookmarks, "github", matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "GitHub Profile")

    def test_query_multiple_words(self):
        matches = []
        self.querier.search(self.test_bookmarks, "github profile", matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "GitHub Profile")

    def test_query_no_matches(self):
        matches = []
        self.querier.search(self.test_bookmarks, "nonexistent", matches)
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
        
        querier = BookmarkQuerier(
            filter_by_folders=True
        )
        matches = []
        querier.search(many_bookmarks, "Test", matches)
        self.assertEqual(len(matches), 10)  # Should stop at max_matches_len 

    def test_search_matches_parent_folder(self):
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
                        # Test subfolder
                        {
                            "type": "folder",
                            "name": "Advanced",
                            "children": [
                                {
                                    "type": "bookmark",
                                    "name": "Python Tricks Tutorial",
                                    "url": "https://realpython.com"
                                }
                            ]
                        }

                    ]
                }
            ]
        }
        
        querier = BookmarkQuerier(
            filter_by_folders=True
        )
        matches = []
        querier.search(bookmarks, "python documentation", matches)
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Documentation")
        self.assertEqual(matches[0]["url"], "https://docs.python.org")

        # Make sure to consider URL matches as well
        matches = []
        querier.search(bookmarks, "python learn", matches)
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Python Tutorial")
        self.assertEqual(matches[0]["url"], "https://learn.python.org")

        # Test that it still works with just the bookmark name
        matches = []
        querier.search(bookmarks, "documentation", matches)
        self.assertEqual(len(matches), 1)

        # Test that it matches folder and subfolder
        matches = []
        querier.search(bookmarks, "python advanced", matches)
        self.assertEqual(len(matches), 1)

        matches = []
        querier.search(bookmarks, "tutorial", matches)
        self.assertEqual(len(matches), 3)
        self.assertEqual(matches[0]["name"], "git tutorial")

        matches = []
        querier.search(bookmarks, "advanced tutorial", matches)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "Python Tricks Tutorial")

        # Test that it matches when both parent and bookmark match
        # Should match: python/* && python/Advanced/*
        matches = []
        querier.search(bookmarks, "python tutorial", matches)
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0]["name"], "Python Tutorial")
        self.assertEqual(matches[1]["name"], "Python Tricks Tutorial")
        
        # Test that it doesn't match when neither parent nor bookmark match
        matches = []
        querier.search(bookmarks, "java docs", matches)
        self.assertEqual(len(matches), 0) 

