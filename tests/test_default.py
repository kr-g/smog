import os
import unittest
from smog.file import FileStat
from smog.memo import (
    Memo,
    PreludeException,
    PreludeDateException,
    PreludeTimeException,
    S_DATE,
    S_TIME,
    S_REFER,
    hashtag,
)


MEMO01 = "memo-01.txt"
MEMO02 = "memo-02.txt"
MEMO03 = "memo-03.txt"


class Memo_TestCase(unittest.TestCase):
    def setUp(self):
        self.datadir = FileStat().join(["tests", "data"])

    def tearDown(self):
        pass

    def readmemo(self, fnam):
        return Memo(self.datadir.join([fnam]).name).open().read()

    def test_000_default(self):
        self.assertIsNotNone(self.datadir.exists())

    def test_001_read(self):
        mt = self.readmemo(MEMO01)
        self.assertIsNotNone(mt)

    def test_002_content(self):
        mt = self.readmemo(MEMO01)
        body = """
this is a first text

end

#end of file -- here --
            """.strip()
        b = mt.body().strip()
        self.assertEqual(body, b)

    def test_003_header_mandatory(self):
        mt = self.readmemo(MEMO01)
        self.assertEqual(mt.head("version"), 1)
        self.assertEqual(mt.head("date"), (2021, 8, 9))
        self.assertEqual(mt.head("time"), (8, 3, 0))

    def test_004_header_optional(self):
        mt = self.readmemo(MEMO01)
        # check if exist and occurance
        for h, cnt in [
            ("id", 1),
            ("type", 2),
            ("meta", 3),
            ("tag", 2),
            ("category", 2),
            ("refer", 2),
        ]:
            rc = mt.has_head(h)
            self.assertTrue(rc, h)
            hc = mt.head(h)
            self.assertEqual(len(hc), cnt)
        self.assertFalse(mt.has_head("gps-lat-lon"))

    def test_100_read_memo2(self):
        self.assertRaises(PreludeDateException, self.readmemo, MEMO02)

    def test_200_read_memo3(self):
        self.assertRaises(PreludeTimeException, self.readmemo, MEMO03)

    def test_800_hashtag(self):
        inp = """sample text #here is a #sample-text     one
showing all #hashTag.probs or no #more:or
#see,also #tags_here-or-what and #guess+this
#com#bine#this #without-slash/ or #, #/ <-invalid
"""
        expect_rc = [
            "#here",
            "#sample-text",
            "#hashTag",
            "#more",
            "#see",
            "#tags_here-or-what",
            "#guess+this",
            "#com",
            "#bine",
            "#this",
            "#without-slash",
        ]
        ht = hashtag(inp)
        self.assertEqual(expect_rc, ht)

    def test_999_more_tests__missing__(self):
        pass
