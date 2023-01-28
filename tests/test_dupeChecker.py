#!/usr/bin/env python

import unittest

import dupeChecker

class testFileCompare(unittest.TestCase):

    def setUp(self):
        self.fa = dupeChecker.FileHeuristicCache("./data/FileA.jpg")
        self.fb = dupeChecker.FileHeuristicCache("./data/FileB.jpg")
        self.fc = dupeChecker.FileHeuristicCache("./data/CopyA.jpg")
        self.faToo = dupeChecker.FileHeuristicCache("./data/FileA.jpg")
        self.fDne = dupeChecker.FileHeuristicCache("./data/DoesNotExist.jpg")

    def test_hash(self):
        self.assertNotEqual(self.fa.hash, self.fb.hash)
        self.assertEqual(self.fa.hash, self.fc.hash)

    def test_cache(self):
        self.assertNotEqual(self.fa, self.fb)
        self.assertEqual(self.fa, self.fc)
        self.assertEqual(self.fa, self.faToo)

    def test_missing_file(self):
        self.assertEqual(self.fDne.hash, None)

    def test_missing_not_equal(self):
        fDneToo = dupeChecker.FileHeuristicCache("./data/DoesNotExist.jpg")
        self.assertNotEqual(self.fDne, fDneToo)

if __name__ == '__main__':
    unittest.main()
