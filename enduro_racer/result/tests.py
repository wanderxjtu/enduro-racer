import datetime

from django.test import TestCase

# Create your tests here.

from result.read_result_csv import BBRawResultReader, CsvResultReader


class TestBBRawResultReader(TestCase):
    def test_ms_to_tstr(self):
        self.reader = BBRawResultReader()
        self.assertEqual("00:00:06.000", self.reader._ms_to_tstr(6000))
        self.assertEqual("08:16:22.727", self.reader._ms_to_tstr(1558253782727))

    def test_read_result(self):
        reader = BBRawResultReader()
        res = reader._get_raw_file_paires("test")
        print(res)
        self.assertIn('', res)
        rs = reader.read_bb_raw_result("test2")
        print(rs)


