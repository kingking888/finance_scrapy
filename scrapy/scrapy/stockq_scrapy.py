# -*- coding: utf8 -*-

import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import scrapy.common as CMN
import scrapy_class_base as ScrapyBase# as ScrapyBase
g_logger = CMN.LOG.get_logger()


def _scrape_vix_(scrapy_cfg, *args, **kwargs):
    # import pdb; pdb.set_trace()
    url = scrapy_cfg['url']
    # if kwargs.has_key("time_range"):
    #     # finance_month = kwargs["month"]
    #     # year = finance_month.year
    #     # month = finance_month.month
    #     # start_date = 1
    #     # end_date = finance_month.get_last_date_of_month()
    #     time_range_cfg = finance_month = kwargs["time_range"]
    #     time_start = time_range_cfg['start']
    #     time_end = time_range_cfg['end']
    #     url_time_range = scrapy_cfg["url_time_range_format"].format(time_start.year, time_start.month, time_start.day, time_end.year, time_end.month, time_end.day)  
    #     url += url_time_range

    parse_data_name = kwargs.get("parse_data_name", True)
    parse_data = kwargs.get("parse_data", True)
    def parse_url_data(req):
        # import pdb; pdb.set_trace()
        soup = BeautifulSoup(req.text)
        # print (soup.prettify())
        table_tags = soup.find_all("table", class_="indexpagetable")
        if table_tags is None:
            g_logger.error("Fail to find the table of VIX")
            return None
# The VIX table
        tr_tags = table_tags[4].find_all('tr')
# parse data name
        data_name_list = None
        if parse_data_name:
            data_name_list = [CMN.DEF.DATE_IN_CHINESE,]
            td_tags = tr_tags[0].find_all("td")
            for td_tag in td_tags[1:3]:
                data_name_list.append(td_tag.text)
# parse data
        # import pdb; pdb.set_trace()
        data_list = None
        if parse_data:
            data_list_row1 = []
            data_list_row2 = []
            for tr_tag in tr_tags[1:]:
                # print (tr_tag.text)
                td_tags = tr_tag.find_all("td")
# data in a row1                
                date_element_list = td_tags[0].string.split("/")
                assert len(date_element_list) == 3, "The length[%d] of date_element_list should be 3" % len(date_element_list)
                data_element_list = [CMN.DEF.DATE_STRING_FORMAT % (int(date_element_list[0]), int(date_element_list[1]), int(date_element_list[2])),]
                data_element_list.append(str(td_tags[1].string))
                data_element_list.append(str(td_tags[2].span.string))
                data_list_row1.append(data_element_list)
# data in a row2
                date_element_list = td_tags[3].string.split("/")
                assert len(date_element_list) == 3, "The length[%d] of date_element_list should be 3" % len(date_element_list)
                data_element_list = [CMN.DEF.DATE_STRING_FORMAT % (int(date_element_list[0]), int(date_element_list[1]), int(date_element_list[2])),]
                data_element_list.append(str(td_tags[4].string))
                data_element_list.append(str(td_tags[5].span.string))
                data_list_row2.append(data_element_list)
            data_list = []
            data_list.extend(data_list_row1)
            data_list.extend(data_list_row2)
        # import pdb; pdb.set_trace()
        return (data_list, data_name_list)
    # import pdb; pdb.set_trace()
    data_list, data_name_list = ScrapyBase.ScrapyBase.try_request_web_data(url, parse_url_data, url_encoding=scrapy_cfg['url_encoding'])
    if data_list is not None:
        data_list.reverse()
    return (data_list, data_name_list)


class StockQScrapyMeta(type):

    __ATTRS = {
        "_scrape_vix_": _scrape_vix_,
    }

    def __new__(mcs, name, bases, attrs):
        attrs.update(mcs.__ATTRS)
        return type.__new__(mcs, name, bases, attrs)


class StockQScrapy(ScrapyBase.ScrapyBase):

    __metaclass__ = StockQScrapyMeta

    _CAN_SET_TIME_RANGE = False

    __STOCKQ_ULR_PREFIX = "http://www.stockq.org/"

    __MARKET_SCRAPY_CFG = {
        "vix": { # VIX波動率
            "url": __STOCKQ_ULR_PREFIX + "index/VIX.php",
            "url_encoding": CMN.DEF.URL_ENCODING_UTF8,
        },
    }

    __STOCK_SCRAPY_CFG = {
    }

    # __MARKET_URL = {key: value["url_format"] for (key, value) in __MARKET_SCRAPY_CFG.items()}
    # __MARKET_TIME_UNIT_URL_LIST = {key: value["table_time_unit_url_list"] for (key, value) in __MARKET_SCRAPY_CFG.items()}
    # __MARKET_TIME_UNIT_DESCRIPTION_LIST = {key: value["table_time_unit_description_list"] for (key, value) in __MARKET_SCRAPY_CFG.items()}

    # __STOCK_URL_FORMAT = {key: value["url_format"] for (key, value) in __STOCK_SCRAPY_CFG.items()}
    # __STOCK_TIME_UNIT_URL_LIST = {key: value["table_time_unit_url_list"] for (key, value) in __STOCK_SCRAPY_CFG.items()}
    # __STOCK_TIME_UNIT_DESCRIPTION_LIST = {key: value["table_time_unit_description_list"] for (key, value) in __STOCK_SCRAPY_CFG.items()}

    # __TIME_UNIT_URL_LIST = {}
    # __TIME_UNIT_URL_LIST.update(__MARKET_TIME_UNIT_URL_LIST)
    # __TIME_UNIT_URL_LIST.update(__STOCK_TIME_UNIT_URL_LIST)

    # __TIME_UNIT_DESCRIPTION_LIST = {}
    # __TIME_UNIT_DESCRIPTION_LIST.update(__MARKET_TIME_UNIT_DESCRIPTION_LIST)
    # __TIME_UNIT_DESCRIPTION_LIST.update(__STOCK_TIME_UNIT_DESCRIPTION_LIST)

    __SCRAPY_CFG = {}
    __SCRAPY_CFG.update(__MARKET_SCRAPY_CFG)
    __SCRAPY_CFG.update(__STOCK_SCRAPY_CFG)

    __FUNC_PTR = {
# market start
        "vix": _scrape_vix_,
# market end
# stock start
# stock end
    }
    __METHOD_NAME_LIST = __FUNC_PTR.keys()


    # @classmethod
    # def get_scrapy_method_list(cls):
    #     return cls.__METHOD_NAME_LIST


    # @classmethod
    # def print_scrapy_method(cls):
    #     print ", ".join(cls.__METHOD_NAME_LIST)


    # @classmethod
    # def print_scrapy_method_time_unit_description(cls, scrapy_method):
    #     print ", ".join(cls.__TIME_UNIT_DESCRIPTION_LIST[scrapy_method])


    def __init__(self, **cfg):
        super(StockQScrapy, self).__init__()
# For the variables which are NOT changed during scraping
        # self.xcfg = {
        #     "dry_run_only": False,
        #     # "finance_root_folderpath": CMN.DEF.CSV_ROOT_FOLDERPATH,
        #     "max_data_count": None,
        # }
        # self.xcfg.update(cfg)
        self.xcfg = self._update_cfg_dict(cfg)

        # self.url = url
        # self.csv_time_duration = None


    def scrape_web(self, *args, **kwargs):
        # url = None
        # import pdb; pdb.set_trace()
        # scrapy_method_name = None
        # try:
        #     scrapy_method_name = self.__METHOD_NAME_LIST[self.scrapy_method]
        # except:
        #     raise ValueError("Unknown scrapy method: %s" % self.scrapy_method)
        # scrapy_cfg = self.__SCRAPY_CFG[scrapy_method_name]
        return (self.__FUNC_PTR[self.scrapy_method])(self.__SCRAPY_CFG[self.scrapy_method], *args, **kwargs)


    # def update_csv_field(self):
    #     _, csv_data_field_list = self.scrape_web()
    #     self._write_scrapy_field_data_to_config(csv_data_field_list, self.scrapy_method_index, self.xcfg['finance_root_folderpath'])


    # @property
    # def CSVTimeDuration(self):
    #     return self.csv_time_duration

    # @CSVTimeDuration.setter
    # def CSVTimeDurationCSVTimeDuration(self, csv_time_duration):
    # 	self.csv_time_duration = csv_time_duration


    # @property
    # def ScrapyMethod(self):
    #     return self.scrapy_method

    # @ScrapyMethod.setter
    # def ScrapyMethod(self, value):
    #     # try:
    #     #     self.method_list.index(value)
    #     # except ValueError:
    #     #     errmsg = "The method[%s] is NOT support in %s" % (value, CMN.FUNC.get_instance_class_name(self))
    #     #     g_logger.error(errmsg)
    #     #     raise ValueError(errmsg)
    #     # self.scrapy_method = value
    #     # if self.scrapy_method_index is not None:
    #     #     g_logger.warn("The {0}::scrapy_method_index is reset since the {0}::scrapy_method is set ONLY".format(CMN.FUNC.get_instance_class_name(self)))
    #     #     self.scrapy_method_index = None
    #     # raise NotImplementedError
    #     self._set_scrapy_method(self, value)


    # @property
    # def ScrapyMethodIndex(self):
    #     return self.scrapy_method_index

    # @ScrapyMethodIndex.setter
    # def ScrapyMethodIndex(self, value):
    #     # if CMN_DEF.SCRAPY_CLASS_CONSTANT_CFG[value]['class_name'] != CMN.FUNC.get_instance_class_name(self):
    #     #     raise ValueError("The scrapy index[%d] is NOT supported by the Scrapy class: %s" % (value, CMN.FUNC.get_instance_class_name(self)))
    #     # self.scrapy_method_index = value
    #     # self.scrapy_method = CMN_DEF.SCRAPY_CLASS_CONSTANT_CFG[self.scrapy_method_index]['scrapy_class_method']
    #     self._set_scrapy_method_index(self, value)


    # @property
    # def TimeCfg(self):
    #     return self.time_cfg

    # @TimeCfg.setter
    # def TimeCfg(self, value):
    #     self.time_cfg = value


if __name__ == '__main__':
    with StockQScrapy() as stockq:
        kwargs = {}
        # import pdb; pdb.set_trace()
        stockq.scrape("option put call ratio", **kwargs)
