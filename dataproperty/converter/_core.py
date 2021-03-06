# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import abc

from .._error import TypeConversionError


class ValueConverterInterface(object):

    @abc.abstractmethod
    def convert(self):   # pragma: no cover
        pass


class ValueConverter(ValueConverterInterface):

    @abc.abstractmethod
    def convert(self):   # pragma: no cover
        pass

    def __init__(self, value, is_convert=True):
        self._value = value
        self._is_convert = is_convert

    def __repr__(self):
        return str(self.convert())


class IntegerConverter(ValueConverter):

    def convert(self):
        if not self._is_convert:
            return self._value

        try:
            return int(self._value)
        except (TypeError, ValueError, OverflowError):
            raise TypeConversionError


class FloatConverter(ValueConverter):

    def convert(self):
        if not self._is_convert:
            return self._value

        try:
            return float(self._value)
        except (TypeError, ValueError):
            raise TypeConversionError


class DateTimeConverter(ValueConverter):

    __DAYS_TO_SECONDS_COEF = 60 ** 2 * 24
    __MICROSECONDS_TO_SECONDS_COEF = 1000.0 ** 2
    __COMMON_DST_TIMEZONE_TABLE = {
        -36000: "America/Adak",  # -1000
        -32400: "US/Alaska",  # -0900
        -28800: "US/Pacific",  # -0800
        -25200: "US/Mountain",  # -0700
        -21600: "US/Central",  # -0600
        -18000: "US/Eastern",  # -0500
        -14400: "Canada/Atlantic",  # -0400
        -12600: "America/St_Johns",  # -0330
        -10800: "America/Miquelon",  # -0300
        7200: "Africa/Tripoli",  # 0200
    }

    def __init__(self, value, is_convert=True):
        super(DateTimeConverter, self).__init__(value, is_convert)

        self.__datetime = None

    def convert(self):
        import datetime
        import dateutil.parser
        import pytz

        if isinstance(self._value, datetime.datetime):
            self.__datetime = self._value
            return self.__datetime

        if not self._is_convert:
            return self._value
        try:
            self.__datetime = dateutil.parser.parse(self._value)
        except (AttributeError, ValueError):
            raise TypeConversionError

        try:
            dst_timezone_name = self.__get_dst_timezone_name(
                self.__get_timedelta_sec())
        except (AttributeError, KeyError):
            return self.__datetime

        pytz_timezone = pytz.timezone(dst_timezone_name)
        self.__datetime = self.__datetime.replace(tzinfo=None)
        self.__datetime = pytz_timezone.localize(self.__datetime)

        return self.__datetime

    def __get_timedelta_sec(self):
        dt = self.__datetime.utcoffset()

        return int(
            (
                dt.days *
                self.__DAYS_TO_SECONDS_COEF +
                float(dt.seconds)
            ) +
            float(dt.microseconds / self.__MICROSECONDS_TO_SECONDS_COEF)
        )

    def __get_dst_timezone_name(self, offset):
        return self.__COMMON_DST_TIMEZONE_TABLE[offset]
