import unittest
from src.app import _get_float

class TestGetFloat(unittest.TestCase):

    def test_get_float_valid_float(self):
        data = {"key": 123.45}
        self.assertEqual(_get_float(data, "key"), 123.45)

    def test_get_float_valid_int(self):
        data = {"key": 123}
        self.assertEqual(_get_float(data, "key"), 123.0)

    def test_get_float_valid_string_float(self):
        data = {"key": "123.45"}
        self.assertEqual(_get_float(data, "key"), 123.45)

    def test_get_float_valid_string_int(self):
        data = {"key": "123"}
        self.assertEqual(_get_float(data, "key"), 123.0)

    def test_get_float_missing_key(self):
        data = {}
        self.assertEqual(_get_float(data, "key"), 0.0)

    def test_get_float_missing_key_with_default(self):
        data = {}
        self.assertEqual(_get_float(data, "key", default=99.9), 99.9)

    def test_get_float_invalid_string(self):
        data = {"key": "abc"}
        self.assertEqual(_get_float(data, "key"), 0.0)

    def test_get_float_none_value(self):
        data = {"key": None}
        self.assertEqual(_get_float(data, "key"), 0.0)

if __name__ == '__main__':
    unittest.main()