import os
import unittest

from db_builders.typedefs import Omniclass


class OmniclassParseIdentifier(unittest.TestCase):
    def test_parse_identifier(self):
        # test shorter omniclass identifier
        string = "12-34 56 78 Omniclass Name"
        number, name = Omniclass.parse_identifier(string)

        self.assertEqual(number, "12-34 56 78")
        self.assertEqual(name, "Omniclass Name")

        # test longer omniclass identifier
        string = "12-34 56 78 90 Omniclass Name"
        number, name = Omniclass.parse_identifier(string)

        self.assertEqual(number, "12-34 56 78 90")
        self.assertEqual(name, "Omniclass Name")

    def test_parse_longer_identifier(self):
        # test arbitrarily long omniclass identifier
        string = "12-34 56 78 90 12 34 56 Omniclass Name"
        number, name = Omniclass.parse_identifier(string)
        self.assertEqual(number, "12-34 56 78 90 12 34 56")
        self.assertEqual(name, "Omniclass Name")

    def test_parse_identifier_w_dash(self):
        string = "12-34 56 78 Omniclass-test Name"
        number, name = Omniclass.parse_identifier(string)
        self.assertEqual(number, "12-34 56 78")
        self.assertEqual(name, "Omniclass-test Name")

    def test_parse_identifier_w_symbols(self):
        filename = os.path.join("23-11 17 13 Crash Barriers ( including Impact Attenuating Devices)")

        number, name = Omniclass.parse_identifier(filename)

        self.assertEqual(number, "23-11 17 13")
        self.assertEqual(name, "Crash Barriers ( including Impact Attenuating Devices)")
