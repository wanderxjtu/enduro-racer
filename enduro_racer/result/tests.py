import datetime

from django.test import TestCase

# Create your tests here.

from result.read_result_raw_bb import BBRawResultReader


# class TestBBRawResultReader(TestCase):
    # def test_ms_to_tstr(self):
    #     self.reader = BBRawResultReader()
    #     self.assertEqual("00:00:06.000", self.reader._misecs_to_datetime(6000))
    #     self.assertEqual("08:16:22.727", self.reader._misecs_to_datetime(1558253782727))
    #
    # def test_read_result(self):
    #     reader = BBRawResultReader()
    #     res = reader._get_raw_file_paires("test")
    #     print(res)
    #     self.assertIn('', res)
    #     rs = reader.read_result_from_file("test2")
    #     print(rs)


