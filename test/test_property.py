# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

import datetime

import pytest
import six

from dataproperty import *


nan = float("nan")
inf = float("inf")


@pytest.fixture
def prop_extractor():
    return PropertyExtractor()


class Test_DataPeroperty_data_typecode:

    @pytest.mark.parametrize(
        ["value", "is_convert", "expected_data", "expected_typecode"],
        [
            [six.MAXSIZE, True, six.MAXSIZE, Typecode.INT],
            [-six.MAXSIZE, False, -six.MAXSIZE, Typecode.INT],
            [str(-six.MAXSIZE), True, -six.MAXSIZE, Typecode.INT],
            [str(six.MAXSIZE), False, str(six.MAXSIZE), Typecode.STRING],
            ["1.1", True, 1.1, Typecode.FLOAT],
            ["-1.1", False, "-1.1", Typecode.STRING],
            ["a", True, "a", Typecode.STRING],
            ["a", False, "a", Typecode.STRING],
            [None, True, None, Typecode.NONE],
            [None, False, None, Typecode.NONE],
        ]
    )
    def test_normal(self, value, is_convert, expected_data, expected_typecode):
        dp = DataProperty(value, is_convert=is_convert)
        assert dp.data == expected_data
        assert dp.typecode == expected_typecode

    @pytest.mark.parametrize(["value", "none_value", "expected"], [
        [None, None, None],
        [None, "null", "null"],
        [None, "", ""],
        [None, 0, 0],
    ])
    def test_none(self, value, none_value, expected):
        dp = DataProperty(value, none_value)
        assert dp.data == expected
        assert dp.typecode == Typecode.NONE

    @pytest.mark.parametrize(
        ["value", "is_convert", "expected"],
        [
            [inf, True, OverflowError],
            [inf, False, OverflowError],
        ]
    )
    def test_exception(self, value, is_convert, expected):
        with pytest.raises(expected):
            DataProperty(value, is_convert=is_convert)


class Test_DataPeroperty_set_data:

    @pytest.mark.parametrize(
        [
            "value", "none_value", "is_convert",
            "replace_tabs_with_spaces", "tab_length",
            "expected"
        ],
        [
            ["a\tb", None, True, True, 2, "a  b"],
            ["\ta\t\tb\tc\t", None, True, True, 2, "  a    b  c  "],
            ["a\tb", None, True, True, 4, "a    b"],
            ["a\tb", None, True, False, 4, "a\tb"],
            ["a\tb", None, True, True, None, "a\tb"],
        ])
    def test_normal(
            self, value, none_value, is_convert,
            replace_tabs_with_spaces, tab_length, expected):
        dp = DataProperty(
            value, none_value, is_convert,
            replace_tabs_with_spaces, tab_length)

        assert dp.data == expected


class Test_DataPeroperty_align:

    @pytest.mark.parametrize(["value", "expected"], [
        [1, Align.RIGHT],
        [1.0, Align.RIGHT],
        ["a", Align.LEFT],
        [None, Align.LEFT],
        [nan, Align.RIGHT],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert dp.align == expected


class Test_DataPeroperty_str_len:

    @pytest.mark.parametrize(["value", "expected"], [
        [1, 1],
        [-1, 2],
        [1.0, 3],
        [-1.0, 4],
        [12.34, 5],

        ["000", 1],
        ["123456789", 9],
        ["-123456789", 10],

        ["a", 1],
        [None, 4],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert dp.str_len == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [nan, nan],
    ])
    def test_abnormal(self, value, expected):
        dp = DataProperty(value)
        is_nan(dp.str_len)


class Test_DataPeroperty_integer_digits:

    @pytest.mark.parametrize(["value", "expected"], [
        [1, 1],
        [1.0, 1],
        [12.34, 2],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert dp.integer_digits == expected

    @pytest.mark.parametrize(["value"], [
        [None],
        ["a"],
        [nan],
    ])
    def test_abnormal(self, value):
        dp = DataProperty(value)
        is_nan(dp.integer_digits)


class Test_DataPeroperty_decimal_places:

    @pytest.mark.parametrize(["value", "expected"], [
        [1, 0],
        [1.0, 1],
        [12.34, 2],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert dp.decimal_places == expected

    @pytest.mark.parametrize(["value"], [
        [None],
        ["a"],
        [nan],
    ])
    def test_abnormal(self, value):
        dp = DataProperty(value)
        is_nan(dp.decimal_places)


class Test_DataPeroperty_additional_format_len:

    @pytest.mark.parametrize(["value", "expected"], [
        [2147483648, 0],
        [0, 0],
        [-1, 1],
        [-0.01, 1],
        ["2147483648", 0],
        ["1", 0],
        ["-1", 1],
        ["-0.01", 1],

        [None, 0],
        ["a", 0],
        [nan, 0],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert dp.additional_format_len == expected


class Test_DataPeroperty_repr:

    @pytest.mark.parametrize(["value", "expected"], [
        [
            0,
            "data=0, typename=INT, align=right, str_len=1, "
            "integer_digits=1, decimal_places=0, additional_format_len=0",
        ],
        [
            -1.0,
            "data=-1.0, typename=FLOAT, align=right, str_len=4, "
            "integer_digits=1, decimal_places=1, additional_format_len=1",
        ],
        [
            -12.234,
            "data=-12.23, typename=FLOAT, align=right, str_len=6, "
            "integer_digits=2, decimal_places=2, additional_format_len=1",
        ],
        [
            "abcdefg",
            "data=abcdefg, typename=STRING, align=left, str_len=7, "
            "integer_digits=nan, decimal_places=nan, additional_format_len=0",
        ],
        [
            None,
            "data=None, typename=NONE, align=left, str_len=4, "
            "integer_digits=nan, decimal_places=nan, additional_format_len=0",
        ],
    ])
    def test_normal(self, value, expected):
        dp = DataProperty(value)
        assert str(dp) == expected


class Test_ColumnDataPeroperty:
    DATATIME_DATA = datetime.datetime(2017, 1, 1)

    @pytest.mark.parametrize(["value_list", "expected"], [
        [[None, None], Typecode.STRING],
        [[None, 1], Typecode.INT],
        [[1.0, None], Typecode.FLOAT],
        [[None, "test"], Typecode.STRING],
        [
            [0, six.MAXSIZE, -six.MAXSIZE],
            Typecode.INT,
        ],
        [
            [0, 1.1, -six.MAXSIZE],
            Typecode.FLOAT,
        ],
        [
            [0, 1.1, -six.MAXSIZE, "test"],
            Typecode.STRING,
        ],
        [
            [DATATIME_DATA, DATATIME_DATA],
            Typecode.DATETIME,
        ],
        [[DATATIME_DATA, 1], Typecode.STRING],
        [[1, DATATIME_DATA], Typecode.STRING],
        [[DATATIME_DATA, 1.0], Typecode.STRING],
        [[1.0, DATATIME_DATA], Typecode.STRING],
        [[DATATIME_DATA, "test"], Typecode.STRING],
        [["test", DATATIME_DATA], Typecode.STRING],
        [[1, DATATIME_DATA, 1.0, "test", None], Typecode.STRING],
    ])
    def test_normal_typecode(self, value_list, expected):
        col_prop = ColumnDataProperty()
        col_prop.update_header(DataProperty("dummy"))

        for value in value_list:
            col_prop.update_body(DataProperty(value))

        assert col_prop.typecode == expected

    def test_normal_0(self):
        col_prop = ColumnDataProperty()
        col_prop.update_header(DataProperty("abc"))

        for value in [0, -1.234, 55.55]:
            col_prop.update_body(DataProperty(value))

        assert col_prop.align == Align.RIGHT
        assert col_prop.decimal_places == 3
        assert col_prop.typecode == Typecode.FLOAT
        assert col_prop.padding_len == 6

        assert col_prop.minmax_integer_digits.min_value == 1
        assert col_prop.minmax_integer_digits.max_value == 2

        assert col_prop.minmax_decimal_places.min_value == 2
        assert col_prop.minmax_decimal_places.max_value == 3

        assert col_prop.minmax_additional_format_len.min_value == 0
        assert col_prop.minmax_additional_format_len.max_value == 1

        assert str(col_prop) == (
            "typename=FLOAT, align=right, padding_len=6, "
            "integer_digits=(min=1, max=2), decimal_places=(min=2, max=3), "
            "additional_format_len=(min=0, max=1)")

    def test_normal_1(self):
        col_prop = ColumnDataProperty()
        col_prop.update_header(DataProperty("abc"))

        for value in [0, -1.234, 55.55, "abcdefg"]:
            col_prop.update_body(DataProperty(value))

        assert col_prop.align == Align.LEFT
        assert col_prop.decimal_places == 3
        assert col_prop.typecode == Typecode.STRING
        assert col_prop.padding_len == 7

        assert col_prop.minmax_integer_digits.min_value == 1
        assert col_prop.minmax_integer_digits.max_value == 2

        assert col_prop.minmax_decimal_places.min_value == 2
        assert col_prop.minmax_decimal_places.max_value == 3

        assert col_prop.minmax_additional_format_len.min_value == 0
        assert col_prop.minmax_additional_format_len.max_value == 1

        assert str(col_prop) == (
            "typename=STRING, align=left, padding_len=7, "
            "integer_digits=(min=1, max=2), decimal_places=(min=2, max=3), "
            "additional_format_len=(min=0, max=1)")

    def test_min_padding_len(self):
        min_padding_len = 100

        col_prop = ColumnDataProperty(min_padding_len)
        col_prop.update_header(DataProperty("abc"))

        for value in [0, -1.234, 55.55]:
            col_prop.update_body(DataProperty(value))

        assert col_prop.align == Align.RIGHT
        assert col_prop.decimal_places == 3
        assert col_prop.typecode == Typecode.FLOAT
        assert col_prop.padding_len == min_padding_len

        assert col_prop.minmax_integer_digits.min_value == 1
        assert col_prop.minmax_integer_digits.max_value == 2

        assert col_prop.minmax_decimal_places.min_value == 2
        assert col_prop.minmax_decimal_places.max_value == 3

        assert col_prop.minmax_additional_format_len.min_value == 0
        assert col_prop.minmax_additional_format_len.max_value == 1

        assert str(col_prop) == (
            "typename=FLOAT, align=right, padding_len=100, "
            "integer_digits=(min=1, max=2), decimal_places=(min=2, max=3), "
            "additional_format_len=(min=0, max=1)")

    def test_null(self):
        col_prop = ColumnDataProperty()
        assert col_prop.align == Align.LEFT
        assert is_nan(col_prop.decimal_places)
        assert col_prop.typecode == Typecode.STRING
        assert col_prop.padding_len == 0


class Test_PropertyExtractor_extract_data_property_matrix:

    @pytest.mark.parametrize(["value", "non_value"], [
        [
            [
                [None, 1],
                [1.1, "a"],
            ],
            "null",
        ],
    ])
    def test_normal(self, prop_extractor, value, non_value):
        prop_extractor.data_matrix = value
        prop_extractor.none_value = non_value
        prop_matrix = prop_extractor.extract_data_property_matrix()

        assert len(prop_matrix) == 2

        prop = prop_matrix[0][0]
        assert prop.data == "null"
        assert prop.typecode == Typecode.NONE
        assert prop.align.align_code == Align.LEFT.align_code
        assert prop.align.align_string == Align.LEFT.align_string
        assert prop.str_len == 4
        assert is_nan(prop.decimal_places)
        assert prop.format_str == "s"

        prop = prop_matrix[0][1]
        assert prop.typecode == Typecode.INT
        assert prop.align.align_code == Align.RIGHT.align_code
        assert prop.align.align_string == Align.RIGHT.align_string
        assert prop.str_len == 1
        assert prop.decimal_places == 0
        assert prop.format_str == "d"

        prop = prop_matrix[1][0]
        assert prop.typecode == Typecode.FLOAT
        assert prop.align.align_code == Align.RIGHT.align_code
        assert prop.align.align_string == Align.RIGHT.align_string
        assert prop.str_len == 3
        assert prop.decimal_places == 1
        assert prop.format_str == ".1f"

        prop = prop_matrix[1][1]
        assert prop.typecode == Typecode.STRING
        assert prop.align.align_code == Align.LEFT.align_code
        assert prop.align.align_string == Align.LEFT.align_string
        assert prop.str_len == 1
        assert is_nan(prop.decimal_places)
        assert prop.format_str == "s"

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
    ])
    def test_exception(self, prop_extractor, value, expected):
        with pytest.raises(expected):
            prop_extractor.extract_data_property_matrix(value)


class Test_PropertyExtractor_extract_column_property_list:
    TEST_DATA_MATRIX = [
        [1, 1.1, "aa",  1,   1],
        [2, 2.2, "bbb", 2.2, 2.2],
        [3, 3.33, "cccc", -3, "ccc"],
    ]

    @pytest.mark.parametrize(["header_list", "value"], [
        [
            ["i", "f", "s", "if", "mix"],
            TEST_DATA_MATRIX,
        ],
        [
            None,
            TEST_DATA_MATRIX,
        ],
        [
            [],
            TEST_DATA_MATRIX,
        ],
    ])
    def test_normal(self, prop_extractor, header_list, value):
        prop_extractor.header_list = header_list
        prop_extractor.data_matrix = value
        col_prop_list = prop_extractor.extract_column_property_list()

        assert len(col_prop_list) == 5

        prop = col_prop_list[0]
        assert prop.typecode == Typecode.INT
        assert prop.align.align_code == Align.RIGHT.align_code
        assert prop.align.align_string == Align.RIGHT.align_string
        assert prop.padding_len == 1
        assert is_nan(prop.decimal_places)
        assert prop.format_str == "d"

        prop = col_prop_list[1]
        assert prop.typecode == Typecode.FLOAT
        assert prop.align.align_code == Align.RIGHT.align_code
        assert prop.align.align_string == Align.RIGHT.align_string
        assert prop.padding_len == 4
        assert prop.decimal_places == 2
        assert prop.format_str == ".2f"

        prop = col_prop_list[2]
        assert prop.typecode == Typecode.STRING
        assert prop.align.align_code == Align.LEFT.align_code
        assert prop.align.align_string == Align.LEFT.align_string
        assert prop.padding_len == 4
        assert is_nan(prop.decimal_places)
        assert prop.format_str == "s"

        prop = col_prop_list[3]
        assert prop.typecode == Typecode.FLOAT
        assert prop.align.align_code == Align.RIGHT.align_code
        assert prop.align.align_string == Align.RIGHT.align_string
        assert prop.padding_len == 3
        assert prop.decimal_places == 1
        assert prop.format_str == ".1f"

        prop = col_prop_list[4]
        assert prop.typecode == Typecode.STRING
        assert prop.align.align_code == Align.LEFT.align_code
        assert prop.align.align_string == Align.LEFT.align_string
        assert prop.padding_len == 3
        assert prop.decimal_places == 1
        assert prop.format_str == "s"

    @pytest.mark.parametrize(["header_list", "value", "expected"], [
        [
            None,
            None,
            TypeError
        ],
        [
            ["i", "f", "s", "if", "mix"],
            None,
            TypeError
        ],
    ])
    def test_exception(self, prop_extractor, header_list, value, expected):
        with pytest.raises(expected):
            prop_extractor.header_list = header_list
            prop_extractor.data_matrix = value
            prop_extractor.extract_column_property_list()
