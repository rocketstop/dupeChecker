#!/usr/bin/env python

import unittest
import sys

sys.path.append("..")

import dupeChecker

class testFileCompare(unittest.TestCase):

    def setUp(self):
        self.fa = dupeChecker.FileHeuristicCache("./FileA.jpg")
        self.fb = dupeChecker.FileHeuristicCache("./FileB.jpg")
        self.fc = dupeChecker.FileHeuristicCache("./CopyA.jpg")

    def test_hash(self):
        self.assertNotEqual(self.fa.hash, self.fb.hash)
        self.assertEqual(self.fa.hash, self.fc.hash)

    def test_cache(self):
        self.assertNotEqual(self.fa, self.fb)
        self.assertEqual(self.fa, self.fc)


if __name__ == '__main__':
    unittest.main()
