from unittest import TestCase
from db_builders.name_finder.finder import WebsiteFinder


class TestExtractUrl(TestCase):
    def test_basic_url_extraction(self):
        response = "https://www.example.com"
        expected = "https://www.example.com"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_appended_text(self):
        response = "https://www.example.com is the website"
        expected = "https://www.example.com"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_prepended_text(self):
        response = "The website is: https://www.example.com"
        expected = "https://www.example.com"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_path(self):
        response = "https://www.example.com/products"
        expected = "https://www.example.com/products"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_query_string(self):
        response = "https://www.example.com/products?category=1"
        expected = "https://www.example.com/products?category=1"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_complex_string(self):
        response = "The URL for the manufacturer is: https://www.example.com/products?category=1 is the URL"
        expected = "https://www.example.com/products?category=1"
        url = WebsiteFinder._extract_url(response)
        self.assertEqual(url, expected)

    def test_with_no_url(self):
        response = "No URL found"
        with self.assertRaises(IndexError):
            url = WebsiteFinder._extract_url(response)