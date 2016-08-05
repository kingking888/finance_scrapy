from datetime import datetime, timedelta
import math
import collections
MonthTuple = collections.namedtuple('MonthTuple', ('year', 'month'))
QuarterTuple = collections.namedtuple('QuarterTuple', ('year', 'quarter'))
import common_definition as CMN_DEF
import common_function as CMN_FUNC


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the class that should be a singleton.

    The decorated class can define one `__init__` function that takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated


    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        # import pdb; pdb.set_trace()
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            if hasattr(self._instance, "initialize"):
                self._instance.initialize()
            return self._instance


    def __call__(self):
        raise TypeError('Singletons must be accessed through Instance()')


    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

#############################################################################################

class FinanceTimeBase(object):

    def __init__(self):
        self.year = None
        self.republic_era_year = None
        pass


    def to_string(self):
        raise NotImplementedError


    def get_value(self):
        raise NotImplementedError


    def get_value_tuple(self):
        raise NotImplementedError


    @classmethod
    def from_string(cls, time_string):
        raise NotImplementedError


    def get_year(self):
        assert (self.year is not None), "year value should NOT be None"
        return self.year


    def get_republic_era_year(self):
        assert (self.republic_era_year is not None), "republic_era_year value should NOT be None"
        return self.republic_era_year


    def setup_year_value(self, year_value):
        if CMN_FUNC.is_republic_era_year(year_value):
            self.republic_era_year = int(year_value)
            self.year = self.republic_era_year + CMN_DEF.DEF_REPUBLIC_ERA_YEAR_OFFSET
        else:
            self.year = int(year_value)
            self.republic_era_year = self.year - CMN_DEF.DEF_REPUBLIC_ERA_YEAR_OFFSET


    def __str__(self):
        return self.to_string()


    def __lt__(self, other):
        return self.get_value() < other.get_value()


    def __le__(self, other):
        return self.get_value() <= other.get_value()


    def __eq__(self, other):
        return self.get_value() == other.get_value()


    def __ne__(self, other):
        return self.get_value() != other.get_value()


    def __gt__(self, other):
        return self.get_value() > other.get_value()


    def __ge__(self, other):
        return self.get_value() >= other.get_value()


class FinanceDate(FinanceTimeBase):

    def __init__(self, *args):
        super(FinanceDate, self).__init__()
        self.month = None # range: 1 - 12
        self.day = None # range: 1 - last date of month
        self.date_str = None
        self.datetime_cfg = None
        try:
            if len(args) == 1:
                time_cfg = None
                if isinstance(args[0], str):
                    mobj = CMN_FUNC.check_date_str_format(args[0])
                    self.setup_year_value(mobj.group(1))
                    # self.year = mobj.group(1)
                    self.month = int(mobj.group(2))
                    self.day = int(mobj.group(3))
                elif isinstance(args[0], datetime):
                    self.setup_year_value(args[0].year)
                    # self.year = args[0].year
                    self.month = args[0].month
                    self.day = args[0].day   
                else:
                    raise
            elif len(args) == 3:
                for index in range(3):
                    if type(args[index]) is not int:
                        raise
                self.setup_year_value(args[0])
                # self.year = args[0]
                self.month = args[1]
                self.day = args[2]
            else:
                raise
        except Exception:
            raise ValueError("Unknown argument in FormatDate format: %s" % args)
# Check value range
        FinanceDate.check_value_range(self.year, self.month, self.day)


    @staticmethod
    def check_value_range(year, month, day):
# Check Year Range
        CMN_FUNC.check_year_range(year)
# Check Month Range
        CMN_FUNC.check_month_range(month)
# Check Day Range
        CMN_FUNC.check_day_range(day, year, month)


    @classmethod
    def from_string(cls, time_string):
        return cls(time_string)


    def __add__(self, day_delta):
        # if not isinstance(delta, timedelta):
        #     raise TypeError('The type[%s] of the other variable is NOT timedelta' % type(delta))
        if not isinstance(day_delta, int):
            raise TypeError('The type[%s] of the day_delta argument is NOT int' % type(day_delta))
        return FinanceDate(self.to_datetime() + timedelta(days = day_delta))


    def __sub__(self, day_delta):
        # if not isinstance(delta, timedelta):
        #     raise TypeError('The type[%s] of the other variable is NOT timedelta' % type(delta))
        if not isinstance(day_delta, int):
            raise TypeError('The type[%s] of the day_delta argument is NOT int' % type(day_delta))
        return FinanceDate(self.to_datetime() - timedelta(days = day_delta))


    def to_string(self):
        if self.date_str is None:
            self.date_str = CMN_FUNC.transform_date_str(self.year, self.month, self.day)
        return self.date_str


    def get_value(self):
        return (self.year << 8 | self.month << 4 | self.day)


    def get_value_tuple(self):
        return (self.year, self.month, self.day)


    def to_datetime(self):
        if self.datetime_cfg is None:
            self.datetime_cfg = datetime(self.year, self.month, self.day)
        return self.datetime_cfg


    @staticmethod
    def is_same_month(finance_date1, finance_date2):
        return (True if FinanceMonth(finance_date1.year, finance_date1.month) == FinanceMonth(finance_date2.year, finance_date2.month) else False)


class FinanceMonth(FinanceTimeBase):

    def __init__(self, *args):
        super(FinanceMonth, self).__init__()
        self.month = None # range: 1 - 12
        self.month_str = None
        try:
            if len(args) == 1:
                time_cfg = None
                if isinstance(args[0], str):
                    mobj = CMN_FUNC.check_month_str_format(args[0])
                    self.setup_year_value(mobj.group(1))
                    # self.year = mobj.group(1)
                    self.month = int(mobj.group(2))
                elif isinstance(args[0], datetime):
                    self.setup_year_value(args[0].year)
                    # self.year = args[0].year
                    self.month = args[0].month
                else:
                    raise
            elif len(args) == 2:
                for index in range(2):
                    if type(args[index]) is not int:
                        raise
                self.setup_year_value(args[0])
                # self.year = args[0]
                self.month = args[1]
            else:
                raise
        except Exception:
            raise ValueError("Unknown argument in FormatMonth format: %s" % args)
# Check value range
        FinanceMonth.check_value_range(self.year, self.month)


    @staticmethod
    def check_value_range(year, month):
# Check Year Range
        CMN_FUNC.check_year_range(year)
# Check Month Range
        CMN_FUNC.check_month_range(month)


    @classmethod
    def from_string(cls, time_string):
        return cls(time_string)


    def __to_month_index(self):
        return self.year * 12 + self.month - 1


    def __from_month_index_to_value(self, month_index):
        # year = month_index / 12
        # month = month_index % 12 + 1
        return MonthTuple(month_index / 12, month_index % 12 + 1)


    def __add__(self, month_delta):
        if not isinstance(month_delta, int):
            raise TypeError('The type[%s] of the delta argument is NOT int' % type(month_delta))

        new_month_index = self.__to_month_index() + month_delta
        new_month_tuple = self.__from_month_index_to_value(new_month_index)
        return FinanceMonth(new_month_tuple.year, new_month_tuple.month)


    def __sub__(self, month_delta):
        if not isinstance(month_delta, int):
            raise TypeError('The type[%s] of the delta argument is NOT int' % type(month_delta))

        new_month_index = self.__to_month_index() - month_delta
        new_month_tuple = self.__from_month_index_to_value(new_month_index)
        return FinanceMonth(new_month_tuple.year, new_month_tuple.month)


    def to_string(self):
        if self.month_str is None:
            self.month_str = CMN_FUNC.transform_month_str(self.year, self.month)
        return self.month_str


    def get_value(self):
        return (self.year << 4 | self.month)


    def get_value_tuple(self):
        return (self.year, self.month)


class FinanceQuarter(FinanceTimeBase):

    def __init__(self, *args):
        super(FinanceQuarter, self).__init__()
        self.quarter = None
        self.quarter_str = None
        # import pdb; pdb.set_trace()
        try:
            if len(args) == 1:
                if isinstance(args[0], str):
                    mobj = CMN_FUNC.check_quarter_str_format(args[0])
                    self.setup_year_value(mobj.group(1))
                    # self.year = mobj.group(1)
                    self.quarter = int(mobj.group(2))
                elif isinstance(args[0], datetime):
                    self.setup_year_value(args[0].year)
                    # self.year = args[0].year
                    self.quarter = (int)(math.ceil(args[0].month / 3.0))
                else:
                    raise
            elif len(args) == 2:
                for index in range(2):
                    if type(args[index]) is not int:
                        raise
                self.year = args[0]
                self.quarter = args[1]
            else:
                raise
        except Exception:
            raise ValueError("Unknown argument in FormatQuarter format: %s" % args)
# Check value Range
        FinanceQuarter.check_value_range(self.year, self.quarter)


    @staticmethod
    def check_value_range(year, quarter):
# Check Year Range
        CMN_FUNC.check_year_range(year)
# Check Quarter Range
        CMN_FUNC.check_quarter_range(quarter)


    @classmethod
    def from_string(cls, time_string):
        return cls(time_string)


    def __to_quarter_index(self):
        return self.year * 4 + self.quarter - 1


    def __from_quarter_index_to_value(self, quarter_index):
        return QuarterTuple(quarter_index / 4, quarter_index % 4 + 1)


    def __add__(self, quarter_delta):
        if not isinstance(quarter_delta, int):
            raise TypeError('The type[%s] of the delta argument is NOT int' % type(quarter_delta))

        new_quarter_index = self.__to_quarter_index() + quarter_delta
        new_quarter_tuple = self.__from_quarter_index_to_value(new_quarter_index)
        return FinanceQuarter(new_quarter_tuple.year, new_quarter_tuple.quarter)


    def __sub__(self, quarter_delta):
        if not isinstance(quarter_delta, int):
            raise TypeError('The type[%s] of the delta argument is NOT int' % type(quarter_delta))

        new_quarter_index = self.__to_quarter_index() - quarter_delta
        new_quarter_tuple = self.__from_quarter_index_to_value(new_quarter_index)
        return FinanceQuarter(new_quarter_tuple.year, new_quarter_tuple.quarter)


    def to_string(self):
        if self.quarter_str is None:
            self.quarter_str = CMN_FUNC.transform_quarter_str(self.year, self.quarter)
        return self.quarter_str


    def get_value(self):
        return (self.year << 3 | self.quarter)


    def get_value_tuple(self):
        return (self.year, self.quarter)

# class ParseURLDataType:

#     def __init__(self):
#         # self.parse_url_data_type = None
#         pass


#     def get_type(self):
#         raise NotImplementedError


# class ParseURLDataByBS4(ParseURLDataType):

#     def __init__(self, encoding, select_flag):
#         # self.parse_url_data_type = CMN.PARSE_URL_DATA_BY_BS4
#         self.encoding = encoding
#         self.select_flag = select_flag


#     def get_type(self):
#         return CMN.PARSE_URL_DATA_BY_BS4


# class ParseURLDataByJSON(ParseURLDataType):

#     def __init__(self, data_field_name):
#         # self.parse_url_data_type = CMN.PARSE_URL_DATA_BY_BS4
#         self.data_field_name = data_field_name


#     def get_type(self):
#         return CMN.PARSE_URL_DATA_BY_JSON
