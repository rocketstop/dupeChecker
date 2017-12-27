import unittest
import sys

sys.path.append("..")

import dupeChecker

class testFileCompare(unittest.TestCase):

    def setUp(self):
        self.fa = "./FileA.jpg"
        self.fb = "./FileB.jpg"
        self.fc = "./CopyA.jpg"

    def test_hash(self):
        self.assertNotEqual(dupeChecker.getHash(self.fa), dupeChecker.getHash(self.fb))
        self.assertEqual(dupeChecker.getHash(self.fa), dupeChecker.getHash(self.fc))


if __name__ == '__main__':
    unittest.main()
