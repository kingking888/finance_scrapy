# -*- coding: utf8 -*-

import os
import sys
import re
import requests
import csv
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import common as CMN
import common_class as CMN_CLS
from libs import web_scrapy_logging as WSL
g_logger = WSL.get_web_scrapy_logger()


@CMN_CLS.Singleton
class WebScrapyWorkdayCanlendar(object):

    def __init__(self, datetime_start=None, datetime_end=None):
        self.url_format = "http://www.twse.com.tw/ch/trading/exchange/FMTQIK/genpage/Report{0}{1:02d}/{0}{1:02d}_F3_1_2.php?STK_NO=&myear={0}&mmon={1:02d}"
        self.encoding = "big5"
        self.select_flag = ".board_trad tr"

        self.datetime_start = datetime_start if datetime_start is not None else CMN.transform_string2datetime(CMN.DEF_WEB_SCRAPY_BEGIN_DATE_STR)
        self.datetime_end = None
        if datetime_end is None:
            datetime_now = datetime.today()
            datetime_today = datetime(datetime_now.year, datetime_now.month, datetime_now.day)
            datetime_threshold = datetime(datetime_today.year, datetime_today.month, datetime_today.day, CMN.DEF_TODAY_DATA_EXIST_HOUR, CMN.DEF_TODAY_DATA_EXIST_MINUTE)
            if datetime_now >= datetime_threshold:
                self.datetime_end = datetime_today
            else:
                self.datetime_end = datetime_today + timedelta(days = -1)
        else:
            self.datetime_end = datetime_end
# The start/end time of scrapying data from the web
        self.datetime_start_from_web = self.datetime_start
        self.datetime_end_from_web = self.datetime_end

        self.datetime_start_year = self.datetime_start.year
        self.non_workday_canlendar = None


    def initialize(self):
        # import pdb; pdb.set_trace()
        self.update_workday_canlendar()


    def is_workday(self, datetime_cfg):
        return self.__is_workday(datetime_cfg.year, datetime_cfg.month, datetime_cfg.day)


    def __is_workday(self, year, month, day):
        if self.non_workday_canlendar is None:
            raise RuntimeError("Non Workday Canlendar is NOT initialized")
        datetime_check = datetime(year, month, day)
        if datetime_check < self.datetime_start or datetime_check > self.datetime_end:
            raise RuntimeError("The check date[%s] is OUT OF RANGE[%s-%s]" % datetime_check, self.datetime_start, self.datetime_end)
        return not day in self.non_workday_canlendar[year][month - 1]


    def update_workday_canlendar(self):
        # import pdb; pdb.set_trace()
# Update data from the file
        need_update_from_web = self.__update_no_workday_from_file()
# It's required to update the new data
        if need_update_from_web:
# Update data from the web
            self.__update_no_workday_from_web()
# Write the result into the config file
            self.__write_workday_canlendar_to_file()
# Copy the config file to the finance_analyzer project
            self.__copy_no_workday_canlendar_config_file()


    def __copy_no_workday_canlendar_config_file(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        [working_folder, project_name, lib_folder] = current_path.rsplit('/', 2)
        src_filepath = "%s/%s/%s/%s" % (working_folder, project_name,  CMN.DEF_CONF_FOLDER, CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILENAME)
        dst_folderpath =  "%s/%s/%s" % (working_folder, CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILE_DST_PROJECT_NAME, CMN.DEF_CONF_FOLDER)
        g_logger.debug("Copy the file[%s] to %s" % (CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILENAME, dst_folderpath))
        shutil.copy2(src_filepath, dst_folderpath)


    def __update_no_workday_from_file(self):
        need_update_from_web = True
        conf_filepath = "%s/%s/%s" % (os.getcwd(), CMN.DEF_CONF_FOLDER, CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILENAME)
        g_logger.debug("Try to Acquire the Non Workday Canlendar data from the file: %s......" % conf_filepath)
        if not os.path.exists(conf_filepath):
            g_logger.warn("The Non Workday Canlendar config file does NOT exist")
            return need_update_from_web
        try:
            date_range_str = None
            with open(conf_filepath, 'r') as fp:
                for line in fp:
                    if date_range_str is None:
                        date_range_str = line
                        mobj = re.search("([\d]{4}-[\d]{2}-[\d]{2}) ([\d]{4}-[\d]{2}-[\d]{2})", date_range_str)
                        if mobj is None:
                            raise RuntimeError("Unknown format[%s] of date range in No Workday Canlendar config file", line)
                        datetime_start_from_file = CMN.transform_string2datetime(mobj.group(1))
                        datetime_end_from_file = CMN.transform_string2datetime(mobj.group(2))
                        g_logger.debug("Origianl Date Range in Non Workday Canlendar config file: %s, %s" % (mobj.group(1), mobj.group(2)))
                        if datetime_start_from_file > self.datetime_start:
                            raise RuntimeError("Incorrect start date; File: %s, Expected: %s", datetime_start_from_file, self.datetime_start)
# Check the time range in the file and adjust the range of scrapying data from the web
                        if datetime_end_from_file >= self.datetime_end:
                            g_logger.debug("The latest data has already existed in the file. It's no need to scrapy data from the web")
                            need_update_from_web = False
                        else:
                            self.datetime_start_from_web = datetime_end_from_file + timedelta(days = 1)
                            g_logger.debug("Adjust the time range of web scrapy to %04d-%02d-%02d %04d-%02d-%02d" % (self.datetime_start_from_web.year, self.datetime_start_from_web.month, self.datetime_start_from_web.day, self.datetime_end_from_web.year, self.datetime_end_from_web.month, self.datetime_end_from_web.day))
                    else:
# Obtain the "year" value
                        mobj = re.search("\[([\d]{4})\]", line)
                        if mobj is None:
                            raise RuntimeError("Incorrect year format in Non Workday Canlendar config file: %s", line)
                        year = int(mobj.group(1))
                        # self.non_workday_canlendar[year] = self.__init_canlendar_each_year_list()
                        tmp_data_list = line.split(']')
                        if len(tmp_data_list) != 2:
                            raise RuntimeError("Incorrect data format in Non Workday Canlendar config file: %s", line)
# Parse the non workday in each month
                        year_non_workday_list = tmp_data_list[1].rstrip("\n").split(";")
                        for year_non_workday_list_per_month in year_non_workday_list:
                            tmp_data1_list = year_non_workday_list_per_month.split(':')
                            if len(tmp_data1_list) != 2:
                                raise RuntimeError("Incorrect per month data format in Non Workday Canlendar config file: %s", line)
                            month = int(tmp_data1_list[0])
                            non_workday_list_str = tmp_data1_list[1]
                            non_workday_list = [int(non_workday_str) for non_workday_str in non_workday_list_str.split(",")]
                            self.__set_canlendar_each_month(year, month, non_workday_list)
        except Exception as e:
            g_logger.error("Error occur while No Workday Canlendar, due to %s" % str(e))
            raise e

        return need_update_from_web


    def __update_no_workday_from_web(self):
        # import pdb; pdb.set_trace()
        g_logger.debug("Try to Acquire the No Workday Canlendar data from the web......")
        if self.datetime_start_from_web.year == self.datetime_end_from_web.year and self.datetime_start_from_web.month == self.datetime_end_from_web.month:
            self.__update_no_workday_from_web_by_month(self.datetime_start_from_web.year, self.datetime_start_from_web.month, self.datetime_start_from_web.day, self.datetime_end_from_web.day)
        else:
            self.__update_no_workday_from_web_by_month(self.datetime_start_from_web.year, self.datetime_start_from_web.month, start_day=self.datetime_start_from_web.day)
            year = self.datetime_start_from_web.year
            month = self.datetime_start_from_web.month
            year_end = self.datetime_end_from_web.year
            month_end = self.datetime_end_from_web.month
            def get_next_month(cur_year, cur_month):
                next_year = cur_year + 1 if cur_month == 12 else cur_year
                next_month = 1 if cur_month == 12 else cur_month + 1
                return (next_year, next_month)
            while True:
                (year, month) = get_next_month(year, month)
                if year == year_end and month == month_end:
                    break
                self.__update_no_workday_from_web_by_month(year, month)
            self.__update_no_workday_from_web_by_month(self.datetime_end_from_web.year, self.datetime_end_from_web.month, end_day=self.datetime_end_from_web.day)


    def __update_no_workday_from_web_by_month(self, year, month, start_day=None, end_day=None):
# Check if scrapying the whole month data 
        whole_month_data = False
        if start_day is None and end_day is None:
            whole_month_data = True
        elif end_day is None and start_day == 1:
            whole_month_data = True
        elif start_day is None and end_day == CMN.get_month_last_day(year, month):
            whole_month_data = True

# Assemble the URL
        url = self.url_format.format(*(year, month))
# Scrap the web data
        try:
            # g_logger.debug("Try to Scrap data [%s]" % url)
            res = requests.get(url, timeout=CMN.DEF_SCRAPY_WAIT_TIMEOUT)
        except requests.exceptions.Timeout as e:
            # g_logger.debug("Try to Scrap data [%s]... Timeout" % url)
            fail_to_scrap = False
            for index in range(self.SCRAPY_RETRY_TIMES):
                time.sleep(randint(1,3))
                try:
                    res = requests.get(url, timeout=CMN.DEF_SCRAPY_WAIT_TIMEOUT)
                except requests.exceptions.Timeout as ex:
                    fail_to_scrap = True
                if not fail_to_scrap:
                    break
            if fail_to_scrap:
                g_logger.error("Fail to scrap workday list data even retry for %d times !!!!!!" % self.SCRAPY_RETRY_TIMES)
                raise e
# Select the section we are interested in
        res.encoding = self.encoding
        # print res.text
        soup = BeautifulSoup(res.text)
        web_data = soup.select(self.select_flag)
        workday_list = []
# Parse the web data and obtain the workday list
        if len(web_data) != 0:
        # print "len: %d" % data_len
            for tr in web_data[2:]:
                td = tr.select('td')
                date_list = td[0].text.split('/')
                if len(date_list) != 3:
                    raise RuntimeError("The date format is NOT as expected: %s", date_list)
                cur_day = int(date_list[2])
                if not whole_month_data and cur_day < start_day:
# Caution: It's NO need to consider the end date since the latest data is always today
                    continue
                workday_list.append(cur_day)
# Find the non workday list
        allday_list = []
        if whole_month_data:
            allday_list = range(1, CMN.get_month_last_day(year, month) + 1)
        else:        
            list_start_date = 1 if start_day is None else start_day
            list_end_date = CMN.get_month_last_day(year, month) if end_day is None else end_day
            allday_list = range(list_start_date, list_end_date + 1)
# Get the non-workday list and set to the data structure
        non_workday_list = list(set(allday_list) - set(workday_list))
        self.__set_canlendar_each_month(year, month, non_workday_list)


    def __set_canlendar_each_month(self, year, month, non_workday_list):
        if not non_workday_list:
            return
        if self.non_workday_canlendar is None:
            self.non_workday_canlendar = {}
        if year not in self.non_workday_canlendar:
            self.non_workday_canlendar[year] = self.__init_canlendar_each_year_list()
        self.non_workday_canlendar[year][month - 1].extend(non_workday_list)
        self.non_workday_canlendar[year][month - 1].sort()


    def __init_canlendar_each_year_list(self):
        non_workday_canlendar_year_list = []
        for index in range(12):
            non_workday_canlendar_year_list.append([])
        return non_workday_canlendar_year_list


    def __write_workday_canlendar_to_file(self):
        # import pdb; pdb.set_trace()
        conf_filepath = "%s/%s/%s" % (os.getcwd(), CMN.DEF_CONF_FOLDER, CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILENAME)
        g_logger.debug("Write the No Workday Canlendar data to the file: %s......" % conf_filepath)
        try:
            date_range_str = None
            with open(conf_filepath, 'w') as fp:
                g_logger.debug("Start to write non workday into %s", CMN.DEF_NO_WORKDAY_CANLENDAR_CONF_FILENAME)
                fp.write("%04d-%02d-%02d %04d-%02d-%02d\n" % (self.datetime_start.year, self.datetime_start.month, self.datetime_start.day, self.datetime_end.year, self.datetime_end.month, self.datetime_end.day))
                for year, non_workday_month_list in self.non_workday_canlendar.items():
                    # sys.stderr.write("%s" % ("[%04d]" % year + ";".join(["%d:%s" % (month + 1, ",".join([str(non_workday) for non_workday in non_workday_month_list[month]])) for month in range(12)]) + "\n"))
                    non_workday_each_year_str = "[%04d]" % year + ";".join(["%d:%s" % (month + 1, ",".join([str(non_workday) for non_workday in non_workday_month_list[month]])) for month in range(12)]) + "\n"
                    # for month in range(12):
                    #     non_workday_each_year_str += "%d:%s;" % (month + 1, ",".join([str(non_workday) for non_workday in non_workday_month_list[month]]))
                    # non_workday_each_year_str += "\n"
                    g_logger.debug("Write data: %s" % non_workday_each_year_str)
                    fp.write(non_workday_each_year_str)

        except Exception as e:
            g_logger.error("Error occur while writing Non Workday Canlendar into config file, due to %s" % str(e))
            raise e
