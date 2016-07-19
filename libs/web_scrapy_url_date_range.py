# -*- coding: utf8 -*-

import os
import sys
import re
# import requests
# import csv
# import shutil
# from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# import common as CMN
# import common_class as CMN.CLS
import libs.common as CMN
from libs import web_scrapy_company_profile_lookup as CompanyProfileLookup
from libs import web_scrapy_logging as WSL
g_logger = WSL.get_web_scrapy_logger()


# Find the first and last data
class WebScrapyURLDateRangeBase(object):

    def __init__(self):
        self.last_url_data_date = None


    def __get_date_range_end(self, today_data_exist_hour, today_data_exst_minute):
        self.last_url_data_date = CMN.CLS.FinanceDate(CMN.get_last_url_data_date(today_data_exist_hour, today_data_exst_minute))
        # datetime_now = datetime.today()
        # datetime_today = datetime(datetime_now.year, datetime_now.month, datetime_now.day)
        # datetime_yesterday = datetime_today + timedelta(days = -1)
        # datetime_threshold = datetime(datetime_today.year, datetime_today.month, datetime_today.day, today_data_exist_hour, today_data_exst_minute)
        # self.last_url_data_date = datetime_today if datetime_now >= datetime_threshold else datetime_yesterday


    def get_date_range_start(self, date_source_id):
        raise NotImplementedError


    def get_date_range_end(self, date_source_id):
        raise NotImplementedError

####################################################################################################

@CMN.CLS.Singleton
class WebScrapyMarketURLDateRange(WebScrapyURLDateRangeBase):

    def __init__(self):
        super(WebScrapyMarketURLDateRange, self).__init__()
        self.DEF_DATA_SOURCE_START_DATE_CFG = None
        self.DEF_DATA_SOURCE_START_DATE_CFG_LEN = 0


    def initialize(self):
        self.DEF_DATA_SOURCE_START_DATE_CFG = [
            CMN.CLS.FinanceDate("2001-01-01"),
            CMN.CLS.FinanceDate("2004-04-07"),
            CMN.CLS.FinanceDate("2001-01-01"),
            CMN.CLS.FinanceDate(self.__get_year_offset_datetime_cfg(datetime.today(), -3)),
            CMN.CLS.FinanceDate(self.__get_year_offset_datetime_cfg(datetime.today(), -3)),
            CMN.CLS.FinanceDate(self.__get_year_offset_datetime_cfg(datetime.today(), -3)),
            CMN.CLS.FinanceDate("2002-01-01"),
            CMN.CLS.FinanceDate("2004-07-01"),
            CMN.CLS.FinanceDate("2012-05-02"),
            CMN.CLS.FinanceDate("2012-05-02"),
            CMN.CLS.FinanceDate("2015-04-30"),
            # transform_string2datetime("2010-01-04"),
            # transform_string2datetime("2004-12-17"),
            # transform_string2datetime("2004-12-17"),
            # transform_string2datetime("2004-12-17"),
        ]
        self.DEF_DATA_SOURCE_START_DATE_CFG_LEN = len(self.DEF_DATA_SOURCE_START_DATE_CFG)


    def __get_year_offset_datetime_cfg(datetime_cfg, year_offset):
        return datetime(datetime_cfg.year + year_offset, datetime_cfg.month, datetime_cfg.day)


    def get_date_range_start(self, date_source_id):
        if date_source_id < 0 or date_source_id >= self.DEF_DATA_SOURCE_START_DATE_CFG_LEN:
            raise ValueError("The data source ID[%d] is OUT OF RANGE[0, %d)" % (date_source_id, self.DEF_DATA_SOURCE_START_DATE_CFG_LEN))
        return self.DEF_DATA_SOURCE_START_DATE_CFG[date_source_id]


    def get_date_range_end(self, date_source_id):
        if self.last_url_data_date is None:
            self.__get_date_range_end(CMN.DEF.DEF_TODAY_MARKET_DATA_EXIST_HOUR, CMN.DEF.DEF_TODAY_MARKET_DATA_EXIST_MINUTE)
        return self.last_url_data_date


####################################################################################################

@CMN.CLS.Singleton
class WebScrapyStockURLDateRange(WebScrapyURLDateRangeBase):

    def __init__(self):
        super(WebScrapyStockURLDateRange, self).__init__()
        self.company_profile_lookup = None
        self.company_listing_date_dict = None


    def initialize(self):
        self.company_profile_lookup = WebScrapyCompanyProfileLookup.Instance()
        self.company_listing_date_dict = {}


    def get_date_range_start(self, date_source_id):
        listing_date = self.company_listing_date_dict.get(date_source_id, None)
        if listing_date is None:
            listing_date_str = self.company_profile_lookup.lookup_company_listing_date(date_source_id)
            listing_date = self.company_listing_date_dict[date_source_id] = CMN.CLS.FinanceDate(listing_date_str)
        return listing_date


    def get_date_range_end(self, date_source_id):
        if self.last_url_data_date is None:
            self.__get_date_range_end(CMN.DEF.DEF_TODAY_STOCK_DATA_EXIST_HOUR, CMN.DEF.DEF_TODAY_STOCK_DATA_EXIST_MINUTE)
        return self.last_url_data_date
