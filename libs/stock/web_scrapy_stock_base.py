# -*- coding: utf8 -*-

import os
import re
import json
import requests
import collections
import csv
import time
import copy
from abc import ABCMeta, abstractmethod
from random import randint
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import libs.common as CMN
import libs.base as BASE
import web_scrapy_company_group_set as CompanyGroupSet
import web_scrapy_company_profile as CompanyProfile
import web_scrapy_url_time_range as URLTimeRange
g_logger = CMN.WSL.get_web_scrapy_logger()


class WebScrapyStockBase(BASE.BASE.WebScrapyBase):

    # url_time_range = None
    def __init__(self, cur_file_path, **kwargs):
        super(WebScrapyStockBase, self).__init__(cur_file_path, **kwargs)
        self.company_group_set = None
        if kwargs.get("company_group_set", None) is None:
            self.company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_group_set()
        else:
            self.company_group_set = kwargs["company_group_set"]
        # self.time_slice_kwargs["company_code_number"] = None
        self.new_csv_time_duration_dict = None
        self.scrapy_company_progress_count = 0
        self.company_profile = None
        self.cur_company_code_number = None # Caution: This value is updated every time when assemble_web_url() is called


    def __get_company_profile(self):
        if self.company_profile is None:
            self.company_profile = CompanyProfile.WebScrapyCompanyProfile.Instance()
        return self.company_profile


    def _get_url_time_range(self):
        # import pdb; pdb.set_trace()
        if self.url_time_range is None:
            self.url_time_range = URLTimeRange.WebScrapyURLTimeRange.Instance()
        return self.url_time_range


    def assemble_csv_company_folderpath(self, company_code_number, company_group_number=-1):
        if company_group_number == -1:
            company_group_number = self.__get_company_profile().lookup_company_group_number(company_code_number)
        csv_company_folderpath = "%s/%s%02d/%s" % (self.xcfg["finance_root_folderpath"], CMN.DEF.DEF_CSV_STOCK_FOLDERNAME, int(company_group_number), company_code_number) 
        return csv_company_folderpath


    def assemble_csv_filepath(self, source_type_index, company_code_number, company_group_number=-1):
        if company_group_number == -1:
            company_group_number = self.__get_company_profile().lookup_company_group_number(company_code_number)
        # csv_filepath = "%s/%s%02d/%s/%s.csv" % (self.xcfg["finance_root_folderpath"], CMN.DEF.DEF_CSV_STOCK_FOLDERNAME, int(company_group_number), company_code_number, CMN.DEF.DEF_WEB_SCRAPY_MODULE_NAME_MAPPING[source_type_index]) 
        # return csv_filepath
        return CMN.FUNC.assemble_stock_csv_filepath(self.xcfg["finance_root_folderpath"], source_type_index, company_code_number, company_group_number)


    def _check_old_csv_time_duration_exist(self, *args):
        if self.xcfg["csv_time_duration_table"] is None:
            return False 
        company_csv_time_duration_table = self.xcfg["csv_time_duration_table"].get(args[0], None)
        if company_csv_time_duration_table is None:
            return False
        if company_csv_time_duration_table.get(self.source_type_index, None) is None:
            return False
        return True


    def _adjust_csv_time_duration(self, company_code_number):
        # import pdb; pdb.set_trace()
# Limit the time range from the web site
        time_duration_after_lookup_time = (self._adjust_time_duration_start_and_end_time_func_ptr(self.xcfg["time_duration_type"]))(self.source_type_index, company_code_number)
# Determine the CSV/Web time duration
        web2csv_time_duration_update = None
        if self._check_old_csv_time_duration_exist(company_code_number):
            web2csv_time_duration_update = self._get_overlapped_web2csv_time_duration_update_cfg(
                self.xcfg["csv_time_duration_table"][company_code_number][self.source_type_index], 
                time_duration_after_lookup_time.time_duration_start, 
                time_duration_after_lookup_time.time_duration_end
            )
        else:
            web2csv_time_duration_update = self._get_non_overlapped_web2csv_time_duration_update_cfg(
                time_duration_after_lookup_time.time_duration_start, 
                time_duration_after_lookup_time.time_duration_end
            )
        if web2csv_time_duration_update.NeedUpdate:
            self.new_csv_time_duration_dict[company_code_number] = CMN.CLS.TimeDurationTuple(web2csv_time_duration_update.NewCSVStart, web2csv_time_duration_update.NewCSVEnd)
        return web2csv_time_duration_update


    def scrap_web_to_csv(self):
        # import pdb; pdb.set_trace()
        self.new_csv_time_duration_dict = {}
        self.scrapy_company_progress_count = 0
        for company_group_number, company_code_number_list in self.company_group_set.items():
            for company_code_number in company_code_number_list:
# Create a folder for a specific company
                csv_company_folderpath = self.assemble_csv_company_folderpath(company_code_number, company_group_number)
                CMN.FUNC.create_folder_if_not_exist(csv_company_folderpath)
                # import pdb; pdb.set_trace()
# Find the file path for writing data into csv
                csv_filepath = self.assemble_csv_filepath(self.source_type_index, company_code_number, company_group_number)
# Determine the actual time range
                web2csv_time_duration_update = self._adjust_csv_time_duration(company_code_number)
                if not web2csv_time_duration_update.NeedUpdate:
                    g_logger.debug("[%s:%s] %s %s:%s => The CSV data already cover this time range !!!" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], company_code_number, CMN.DEF.DEF_TIME_DURATION_TYPE_DESCRIPTION[self.xcfg["time_duration_type"]], web2csv_time_duration_update.NewCSVStart, web2csv_time_duration_update.NewCSVEnd))
                    continue
                scrapy_msg = "[%s:%s] %s %s:%s => %s" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], company_code_number, CMN.DEF.DEF_TIME_DURATION_TYPE_DESCRIPTION[self.xcfg["time_duration_type"]], web2csv_time_duration_update.NewWebStart, web2csv_time_duration_update.NewWebEnd, csv_filepath)
                g_logger.debug(scrapy_msg)
# Check if only dry-run
                if self.xcfg["dry_run_only"]:
                    print scrapy_msg
                    continue
# If it's required to add the new web data in front of the old CSV data, a file is created to backup the old CSV data
                if web2csv_time_duration_update.AppendDirection == BASE.BASE.WebScrapyBase.Web2CSVTimeRangeUpdate.WEB2CSV_APPEND_FRONT:
                    g_logger.debug("Need add the new data in front of the old CSV data, rename the file: %s" % (csv_filepath + ".old"))
                    CMN.FUNC.rename_file_if_exist(csv_filepath, csv_filepath + ".old") 
# Create the time slice iterator due to correct time range
                # import pdb; pdb.set_trace()
# Update the time range of time slice
                time_slice_generator_cfg = {"company_code_number": company_code_number, "time_duration_start": web2csv_time_duration_update.NewWebStart, "time_duration_end": web2csv_time_duration_update.NewWebEnd,}
                # import pdb; pdb.set_trace()
# Generate the time slice
                timeslice_iterable = self._get_timeslice_iterable(**time_slice_generator_cfg)
                csv_data_list_each_year = []
                cur_year = None
                # import pdb; pdb.set_trace()
                web_data_emtpy_time_start = web_data_emtpy_time_end = None
                self.emtpy_web_data_list = []
# Generate the time slice list
                for timeslice in timeslice_iterable:
                    csv_data_list = None
# Write the data into csv year by year
                    if timeslice.year != cur_year:
                        if len(csv_data_list_each_year) > 0:
                            # import pdb; pdb.set_trace()
                            self._write_to_csv(csv_filepath, csv_data_list_each_year, self.source_url_parsing_cfg["url_multi_data_one_page"])
                            csv_data_list_each_year = []
                        cur_year = timeslice.year
                    url = self.assemble_web_url(timeslice, company_code_number)
                    g_logger.debug("Get the data from URL: %s" % url)
                    try:
                        # import pdb;pdb.set_trace()
# Grab the data from website and assemble the data to the entry of CSV
                        csv_data_list = self._parse_web_data(self.get_web_data(url))
                    except CMN.EXCEPTION.WebScrapyNotFoundException as e:
                        # import pdb;pdb.set_trace()
                        errmsg = None
                        if isinstance(e.message, str):
                            errmsg = "Fail to scrap URL[%s], due to: %s" % (url, e.message)
                        else:
                            errmsg = u"Fail to scrap URL[%s], due to: %s" % (url, e.message)
                        CMN.FUNC.try_print(errmsg)
                        g_logger.error(errmsg)
                        raise e
                    except CMN.EXCEPTION.WebScrapyServerBusyException as e:
                        RETRY_TIMES = 5
                        SLEEP_TIME_BEFORE_RETRY = 15
                        scrapy_success = False
                        for retry_times in range(1, RETRY_TIMES + 1):
                            if scrapy_success:
                                break
                            g_logger.warn("Server is busy, let's retry...... %d", retry_times)
                            time.sleep(SLEEP_TIME_BEFORE_RETRY * retry_times)
                            try:
# Grab the data from website and assemble the data to the entry of CSV
                                csv_data_list = self._parse_web_data(self.get_web_data(url))
                            except CMN.EXCEPTION.WebScrapyServerBusyException as e:
                                pass
                            else:
                                scrapy_success = True
                        if not scrapy_success:
                            raise CMN.EXCEPTION.WebScrapyServerBusyException("Fail to scrap URL[%s] after retry for %d times" % (url, RETRY_TIMES))
                    except Exception as e:
                        # import pdb;pdb.set_trace()
                        if isinstance(e.message, str):
                            g_logger.warn("Fail to scrap URL[%s], due to: %s" % (url, e.message))
                        else:
                            g_logger.warn(u"Fail to scrap URL[%s], due to: %s" % (url, e.message))
                    else:
                        if csv_data_list is None:
                            # import pdb;pdb.set_trace()
                            if web_data_emtpy_time_start is None:
                                web_data_emtpy_time_start = web_data_emtpy_time_end = timeslice
                            else:
                                if web_data_emtpy_time_end.check_continous_time_duration(timeslice):
                                    web_data_emtpy_time_end = timeslice
                                else:
# Keep track of the time range in which the web data is empty
                                    self.emtpy_web_data_list.append(
                                        CMN.CLS.SourceTypeCompanyTimeDurationTuple(
                                            self.source_type_index,
                                            company_code_number,
                                            CMN.DEF.DATA_TIME_DURATION_RANGE, 
                                            web_data_emtpy_time_start, 
                                            web_data_emtpy_time_end
                                        )
                                    )
                                    web_data_emtpy_time_start = web_data_emtpy_time_end = None
                            # raise RuntimeError(url)
                        else:
                            csv_data_list_each_year.append(csv_data_list)
# Keep track of the time range in which the web data is empty
                if web_data_emtpy_time_start is not None:
                    self.emtpy_web_data_list.append(
                        CMN.CLS.SourceTypeCompanyTimeDurationTuple(
                            self.source_type_index,
                            company_code_number,
                            CMN.DEF.DATA_TIME_DURATION_RANGE, 
                            web_data_emtpy_time_start, 
                            web_data_emtpy_time_end
                        )
                    )
# Write the data of last year into csv
                if len(csv_data_list_each_year) > 0:
                    self._write_to_csv(csv_filepath, csv_data_list_each_year, self.source_url_parsing_cfg["url_multi_data_one_page"])
# Append the old CSV data after the new web data if necessary
                if web2csv_time_duration_update.AppendDirection == BASE.BASE.WebScrapyBase.Web2CSVTimeRangeUpdate.WEB2CSV_APPEND_FRONT:
                    g_logger.debug("Append the old CSV data to the file: %s" % csv_filepath)
                    CMN.FUNC.append_data_into_file(csv_filepath + ".old", csv_filepath)
                    CMN.FUNC.remove_file_if_exist(csv_filepath + ".old") 
                self.scrapy_company_progress_count += 1


    def get_new_csv_time_duration_dict(self):
# No matter the csv time range would be updated, the new time duration is required to re-write into the config file
        assert self.new_csv_time_duration_dict is not None, "self.new_csv_time_duration_dict should NOT be None"
        return self.new_csv_time_duration_dict


    def assemble_web_url(self, timeslice, company_code_number):
        # raise NotImplementedError
        self.cur_company_code_number = company_code_number


    @property
    def CompanyProgressCount(self):
        return self.scrapy_company_progress_count

##########################################################################

class WebScrapyStockStatementBase(WebScrapyStockBase):

    __metaclass__ = ABCMeta
    TABLE_COLUMN_FIELD_EXIST = False
    def __init__(self, cur_file_path, **kwargs):
        super(WebScrapyStockStatementBase, self).__init__(cur_file_path, **kwargs)
        # import pdb;pdb.set_trace()
        if not kwargs.get("renew_statement_field", False):
            if self.TABLE_FIELD_INTEREST_TITLE_LIST is None:
                raise ValueError("TABLE_FIELD_INTEREST_TITLE_LIST is None")
        self.cur_quarter_str = None


    @classmethod
    def _init_statement_field_class_variables(cls, conf_filename):
        # import pdb; pdb.set_trace()
        if not CMN.FUNC.check_config_file_exist(conf_filename):
            raise CMN.EXCEPTION.WebScrapyNotFoundException("The %s file does NOT exist" % conf_filename)
        table_field_title_list = None
        table_column_field_title_list = None
        if cls.TABLE_COLUMN_FIELD_EXIST:
            total_table_field_title_list = CMN.FUNC.read_config_file_lines_ex(conf_filename, "rb")
            try:
                column_field_start_flag_index = total_table_field_title_list.index(CMN.DEF.DEF_COLUMN_FIELD_START_FLAG_IN_CONFIG)
                table_field_title_list = copy.deepcopy(total_table_field_title_list[0:column_field_start_flag_index])
                table_column_field_title_list = copy.deepcopy(total_table_field_title_list[column_field_start_flag_index + 1:])
            except ValueError:
                raise CMN.EXCEPTION.WebScrapyIncorrectFormatException("The column field flag is NOT found in the config file" % conf_filename)        
        else:
            table_field_title_list = CMN.FUNC.read_config_file_lines_ex(conf_filename, "rb")
        cls.TABLE_FIELD_INTEREST_TITLE_LIST = [title for title in table_field_title_list if title not in cls.TABLE_FIELD_NOT_INTEREST_TITLE_LIST]
        # cls.TABLE_FIELD_INTEREST_TITLE_INDEX_DICT = {title: title_index for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST)}
        cls.TABLE_FIELD_NOT_INTEREST_TITLE_LIST_LEN = len(cls.TABLE_FIELD_NOT_INTEREST_TITLE_LIST)
        cls.TABLE_FIELD_INTEREST_TITLE_LIST_LEN = len(cls.TABLE_FIELD_INTEREST_TITLE_LIST)
        if cls.TABLE_COLUMN_FIELD_EXIST:
            cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST = [title for title in table_column_field_title_list if title not in cls.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST]           
            cls.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST_LEN = len(cls.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST)
            cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST_LEN = len(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST)
        else:
            cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT = collections.defaultdict(lambda: cls.TABLE_FIELD_INTEREST_ENTRY_LEN)


    @classmethod
    def _show_statement_field_dimension_internal(cls, interest_conf_filename, auto_gen_sql_element):
        # import pdb; pdb.set_trace()
        field_count = len(cls.TABLE_FIELD_INTEREST_TITLE_LIST)
        field_element_count = 0
        table_field_interest_description_list = []
        for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
            entry_list_entry = cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
            field_entry_index_list = None
            if isinstance(entry_list_entry, list):
                # print u"title: %s, entry_list_entry: %s" % (title, entry_list_entry)
                field_entry_index_list = entry_list_entry
                field_element_count += len(entry_list_entry)
            else:
                # print "title: %s, entry_list_entry: %d" % (title, entry_list_entry)
                table_field_interest_entry_end_index = cls.TABLE_FIELD_INTEREST_ENTRY_START_INDEX + cls.TABLE_FIELD_INTEREST_ENTRY_LEN
                field_entry_index_list = range(cls.TABLE_FIELD_INTEREST_ENTRY_START_INDEX, table_field_interest_entry_end_index)
                field_element_count += entry_list_entry
# Remove the whitespace and Add the field index list
            field_string_entry_index_list = [str(field_entry_index) for field_entry_index in field_entry_index_list]
            title_without_whitesapce = re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE) + u"[%d]: %s" % (title_index, ",".join(field_string_entry_index_list))
            table_field_interest_description_list.append(title_without_whitesapce.encode(CMN.DEF.URL_ENCODING_UTF8))
        field_count_msg = "Field Count: %d, Field Element Count: %d" % (field_count, field_element_count)
        CMN.FUNC.try_print(field_count_msg)
        table_field_interest_description_list.insert(0, field_count_msg)

        # import pdb; pdb.set_trace()
##############################################################################
# Generate the Table Field Definition/Table Field Type Definition list element
# for the finance_recorder_java project
##############################################################################
        if auto_gen_sql_element:
            table_field_interest_description_list.append(u"\n\n".encode(CMN.DEF.URL_ENCODING_UTF8))
# Table Field Definition
            table_field_interest_description_list.append(u"##### TABLE_FIELD_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"date\", // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            field_count = 0
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                entry_list_entry = cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
                field_index_list_len = len(entry_list_entry) if isinstance(entry_list_entry, list) else entry_list_entry
                for entry_index in range(field_index_list_len):
                    field_count += 1
                    table_field_element_definition = u"\"value%d\", // %s" % (field_count, re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE))
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
# Table Field Type Definition
            table_field_interest_description_list.append(u"##### TABLE_FIELD_TYPE_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"DATE NOT NULL PRIMARY KEY\", // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            # field_type_count = 0
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                entry_list_entry = cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
                field_index_list_len = len(entry_list_entry) if isinstance(entry_list_entry, list) else entry_list_entry
                for entry_index in range(field_index_list_len):
                    # field_type_count += 1
                    table_field_element_definition = u"\"BIGINT\", // %s" % re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE)
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
##############################################################################
# Generate the Field Type Definition/Field Description list element
# for the finance_analyzer project
##############################################################################
        if auto_gen_sql_element:
            table_field_interest_description_list.append(u"\n\n".encode(CMN.DEF.URL_ENCODING_UTF8))
# Field Type Definition
            table_field_interest_description_list.append(u"##### FIELD_TYPE_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"FinanceField_DATE, // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                entry_list_entry = cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
                field_index_list_len = len(entry_list_entry) if isinstance(entry_list_entry, list) else entry_list_entry
                for entry_index in range(field_index_list_len):
                    table_field_element_definition = u"FinanceField_LONG, // %s" % re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE)
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
# Field Description
            table_field_interest_description_list.append(u"##### FIELD_DESCRIPTION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"日期\", // FinanceField_DATE".encode(CMN.DEF.URL_ENCODING_UTF8))
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                entry_list_entry = cls.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
                field_index_list_len = len(entry_list_entry) if isinstance(entry_list_entry, list) else entry_list_entry
                for entry_index in range(field_index_list_len):
                    table_field_element_definition = u"\"%s\", // FinanceField_LONG" % re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE)
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
        CMN.FUNC.write_config_file_lines_ex(table_field_interest_description_list, interest_conf_filename, "wb")


    @classmethod
    def _show_statement_column_field_dimension_internal(cls, interest_conf_filename, auto_gen_sql_element):
        # field_count = len(cls.TABLE_FIELD_INTEREST_TITLE_LIST)
        # field_element_count = 0
        table_field_interest_description_list = []
        for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
            title_without_whitesapce = re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE) + u"[%d]" % title_index
            table_field_interest_description_list.append(title_without_whitesapce.encode(CMN.DEF.URL_ENCODING_UTF8))
        table_field_interest_description_list_len = len(table_field_interest_description_list)
# Column
        table_column_field_interest_description_list = []
        for column_title_index, column_title in enumerate(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST):
            column_title_without_whitesapce = re.sub(r"\s+", "", column_title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE) + u"[%d]" % column_title_index
            table_column_field_interest_description_list.append(column_title_without_whitesapce.encode(CMN.DEF.URL_ENCODING_UTF8))
        table_column_field_interest_description_list_len = len(table_column_field_interest_description_list)
        field_count_msg = "Field Count: %d, Column Field Count: %d, Field Element Count: %d" % (table_field_interest_description_list_len, table_column_field_interest_description_list_len, table_field_interest_description_list_len * table_column_field_interest_description_list_len)
        CMN.FUNC.try_print(field_count_msg)
        table_field_interest_description_list.insert(0, field_count_msg)
        table_field_interest_description_list.append(u"##### Column Field #####".encode(CMN.DEF.URL_ENCODING_UTF8))
        table_field_interest_description_list.extend(table_column_field_interest_description_list)

        # import pdb; pdb.set_trace()
##############################################################################
# Generate the Table Field Definition/Table Field Type Definition list element
# for the finance_recorder_java project
##############################################################################
        if auto_gen_sql_element:
            table_field_interest_description_list.append(u"\n\n".encode(CMN.DEF.URL_ENCODING_UTF8))
# Table Field Definition
            table_field_interest_description_list.append(u"##### TABLE_FIELD_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"date\", // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            field_count = 0
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                for column_title_index, column_title in enumerate(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST):
                    field_count += 1
                    table_field_element_definition = u"\"value%d\", // %s:%s" % (field_count, re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE), re.sub(r"\s+", "", column_title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE))
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
# Table Field Type Definition
            table_field_interest_description_list.append(u"##### TABLE_FIELD_TYPE_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"DATE NOT NULL PRIMARY KEY\", // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            # field_type_count = 0
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                for column_title_index, column_title in enumerate(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST):
                    # field_type_count += 1
                    table_field_element_definition = u"\"BIGINT\", // %s:%s" % (re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE), re.sub(r"\s+", "", column_title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE))
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
##############################################################################
# Generate the Field Type Definition/Field Description list element
# for the finance_analyzer project
##############################################################################
        if auto_gen_sql_element:
            table_field_interest_description_list.append(u"\n\n".encode(CMN.DEF.URL_ENCODING_UTF8))
# Field Type Definition
            table_field_interest_description_list.append(u"##### FIELD_TYPE_DEFINITION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"FinanceField_DATE, // 日期".encode(CMN.DEF.URL_ENCODING_UTF8))
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                for column_title_index, column_title in enumerate(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST):
                    table_field_element_definition = u"FinanceField_LONG, // %s:%s" % (re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE), re.sub(r"\s+", "", column_title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE))
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
# Field Description
            table_field_interest_description_list.append(u"##### FIELD_DESCRIPTION #####".encode(CMN.DEF.URL_ENCODING_UTF8))
            table_field_interest_description_list.append(u"\"日期\", // FinanceField_DATE".encode(CMN.DEF.URL_ENCODING_UTF8))
            for title_index, title in enumerate(cls.TABLE_FIELD_INTEREST_TITLE_LIST):
                for column_title_index, column_title in enumerate(cls.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST):
                    table_field_element_definition = u"\"%s:%s\", // FinanceField_LONG" % (re.sub(r"\s+", "", title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE), re.sub(r"\s+", "", column_title.decode(CMN.DEF.URL_ENCODING_UTF8), flags=re.UNICODE))
                    table_field_interest_description_list.append(table_field_element_definition.encode(CMN.DEF.URL_ENCODING_UTF8))
        CMN.FUNC.write_config_file_lines_ex(table_field_interest_description_list, interest_conf_filename, "wb")


    def _modify_time_for_timeslice_generator(self, finance_time_start, finance_time_end):
        assert finance_time_start.get_time_unit_type() == CMN.DEF.DATA_TIME_UNIT_DAY, "The input start time unit type should be %d, not %d" % (CMN.DEF.DATA_TIME_UNIT_DAY, finance_time_start.get_time_unit_type())
        assert finance_time_end.get_time_unit_type() == CMN.DEF.DATA_TIME_UNIT_DAY, "The input end time unit type should be %d, not %d" % (CMN.DEF.DATA_TIME_UNIT_DAY, finance_time_end.get_time_unit_type())
        finance_quarter_start = CMN.CLS.FinanceQuarter.get_start_finance_quarter_from_date(finance_time_start)
        finance_quarter_end = CMN.CLS.FinanceQuarter.get_end_finance_quarter_from_date(finance_time_end)
        return (finance_quarter_start, finance_quarter_end)


    def _insert_not_exist_statement_element(self, dst_statement_field_list, src_statement_list):
        dst_index = 0
        src_index = 0
        dst_statement_field_list_len = len(dst_statement_field_list)
        # import pdb; pdb.set_trace()
        for src_data in src_statement_list:
            try:
                # g_logger.debug(u"Check the statement field[%s] exist" % src_data)
                # cur_offset = (dst_statement_field_list[dst_index:]).index(src_data)
                # dst_index = dst_index + cur_offset + 1
                dst_index = dst_statement_field_list.index(src_data)
                dst_index += 1
            except ValueError:
# New element, insert the data into the list
                if dst_index == dst_statement_field_list_len:
                    dst_statement_field_list.append(src_data)
                else:
                    dst_statement_field_list.insert(dst_index, src_data)
                dst_index += 1
                dst_statement_field_list_len += 1
            # print "FUNC: %s" % dst_statement_field_list


    def update_statement_field(self, dst_statement_field_list, dst_statement_column_field_list=None):
        # import pdb; pdb.set_trace()
# Check if _parse_web_statement_column_field_data() is implemented before it's invoked
        if dst_statement_column_field_list is not None:
            if not hasattr(self, "_parse_web_statement_column_field_data"):
                raise AttributeError("_parse_web_statement_column_field_data() is NOT implemented")
# Update statement field from each company
        for company_group_number, company_code_number_list in self.company_group_set.items():
            for company_code_number in company_code_number_list:
# Create the time slice iterator due to correct time range
                # import pdb; pdb.set_trace()
# Update the time range of time slice
# Limit the time range from the web site
                time_duration_after_lookup_time = (self._adjust_time_duration_start_and_end_time_func_ptr(self.xcfg["time_duration_type"]))(self.source_type_index, company_code_number)
                g_logger.debug("Update statement field => [%s:%s] %s:%s" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], company_code_number, time_duration_after_lookup_time.time_duration_start, time_duration_after_lookup_time.time_duration_end))
                time_slice_generator_cfg = {"company_code_number": company_code_number, "time_duration_start": time_duration_after_lookup_time.time_duration_start, "time_duration_end": time_duration_after_lookup_time.time_duration_end,}
# Generate the time slice
                timeslice_iterable = self._get_timeslice_iterable(**time_slice_generator_cfg)
                # import pdb; pdb.set_trace()
                company_statement_field_list = None
                company_statement_column_field_list = None
                # if company_code_number == "2317":
                #     import pdb; pdb.set_trace()
# Generate the time slice list                
                for timeslice in timeslice_iterable:
                    url = self.assemble_web_url(timeslice, company_code_number)
                    g_logger.debug("Get the statement data from URL: %s" % url)
                    try:
# Find the statement field
                        company_statement_field_list = self._parse_web_statement_field_data(self.get_web_data(url))
                        if company_statement_field_list is None:
                            raise RuntimeError(url)
# Find the statement column field
                        if dst_statement_column_field_list is not None:
                            company_statement_column_field_list = self._parse_web_statement_column_field_data(self.get_web_data(url))
                            if company_statement_column_field_list is None:
                                raise RuntimeError(url)
                    except CMN.EXCEPTION.WebScrapyNotFoundException as e:
                        # import pdb;pdb.set_trace()
                        errmsg = None
                        if isinstance(e.message, str):
                            errmsg = "Fail to scrap URL[%s], due to: %s" % (url, e.message)
                        else:
                            errmsg = u"Fail to scrap URL[%s], due to: %s" % (url, e.message)
                        CMN.FUNC.try_print(errmsg)
                        g_logger.error(errmsg)
                        raise e
                    except CMN.EXCEPTION.WebScrapyServerBusyException as e:
                        RETRY_TIMES = 5
                        SLEEP_TIME_BEFORE_RETRY = 15
                        scrapy_success = False
                        for retry_times in range(1, RETRY_TIMES + 1):
                            if scrapy_success:
                                break
                            g_logger.warn("Server is busy, let's retry...... %d", retry_times)
                            time.sleep(SLEEP_TIME_BEFORE_RETRY * retry_times)
                            try:
# Find the statement field
                                company_statement_field_list = self._parse_web_statement_field_data(self.get_web_data(url))
                                if company_statement_field_list is None:
                                    raise RuntimeError(url)
# Find the statement column field
                                if dst_statement_column_field_list is not None:
                                    company_statement_column_field_list = self._parse_web_statement_column_field_data(self.get_web_data(url))
                                    if company_statement_column_field_list is None:
                                        raise RuntimeError(url)
                            except CMN.EXCEPTION.WebScrapyServerBusyException as e:
                                pass
                            else:
                                scrapy_success = True
                        if not scrapy_success:
                            raise CMN.EXCEPTION.WebScrapyServerBusyException("Fail to scrap URL[%s] after retry for %d times" % (url, RETRY_TIMES))
                    except Exception as e:
                        # import pdb;pdb.set_trace()
                        if isinstance(e.message, str):
                            g_logger.warn("Fail to scrap URL[%s], due to: %s" % (url, e.message))
                        else:
                            g_logger.warn(u"Fail to scrap URL[%s], due to: %s" % (url, e.message))
                    # g_logger.debug("Update statement field from company: %s" % company_code_number)
                    else:
# Update the new statement field
                        self._insert_not_exist_statement_element(dst_statement_field_list, company_statement_field_list)
                        if dst_statement_column_field_list is not None:
# Update the new statement column field
                            self._insert_not_exist_statement_element(dst_statement_column_field_list, company_statement_column_field_list)


    def assemble_web_url(self, timeslice, company_code_number):
        # import pdb; pdb.set_trace()
        super(WebScrapyStockStatementBase, self).assemble_web_url(timeslice, company_code_number)
        url = self.url_format.format(
            *(
                company_code_number,
                timeslice.year - 1911, 
                "%02d" % timeslice.quarter,
            )
        )
        self.cur_quarter_str = CMN.FUNC.transform_quarter_str(timeslice.year, timeslice.quarter)
        return url


    def _parse_web_statement_field_data_internal(self, web_data, web_data_start_index, web_data_end_index=None):
        web_data_len = len(web_data)
        if web_data_len == 0:
            return None
        if web_data_end_index is None:
            web_data_end_index = web_data_len
        data_list = []
# Filter the data which is NOT interested in
        for tr in web_data[web_data_start_index:web_data_end_index]:
        #     print "%d: %s" % (index, tr.text)
            td = tr.select('td')
            # data_list.append(td[0].text.encode(CMN.DEF.URL_ENCODING_UTF8))
            data_list.append(td[0].text)
        if len(data_list) == 0:
            # import pdb;pdb.set_trace()
            raise CMN.EXCEPTION.WebScrapyServerBusyException(u"The field data[%s:%s] is EMPTY" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], self.cur_company_code_number))
        return data_list


    def _parse_web_statement_column_field_data_internal(self, web_data, web_column_data_start_index):
        web_data_len = len(web_data)
        if web_data_len == 0:
            return None
        data_list = []
# Filter the data which is NOT interested in
        td = web_data[web_column_data_start_index].select('td')
        td_len = len(td)
        for i in range(0, td_len):
            # print "%d: %s" % (i, td[i].text)
            data_list.append(td[i].text)
        if len(data_list) == 0:
            # import pdb;pdb.set_trace()
            raise CMN.EXCEPTION.WebScrapyServerBusyException(u"The column field data[%s:%s] is EMPTY" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], self.cur_company_code_number))
        return data_list


    def _parse_web_data_internal(self, web_data, web_data_start_index, web_data_end_index=None):
        web_data_len = len(web_data)
        if web_data_len == 0:
            return None
        if web_data_end_index is None:
            web_data_end_index = web_data_len
        # import pdb; pdb.set_trace()
        # data_list = []
        table_column_field_index_list = None
        table_column_field_index_mapping_list = None
        if self.TABLE_COLUMN_FIELD_EXIST:
            table_column_field_index_list = []
            table_column_field_index_mapping_list = []
            td = web_data[web_data_start_index].select('td')
            td_len = len(td)
            interest_index = 0
            not_interest_index = 0
            for i in range(0, td_len):
                data_found = False
                data_can_ignore = False
                data_index = None
                title = td[i].text.encode(CMN.DEF.URL_ENCODING_UTF8)
                # if interest_index < self.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST_LEN:
                #     try:
                #         # g_logger.error(u"Search for the index of the title[%s] ......" % td[0].text)
                #         data_index = cur_interest_index = (self.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST[interest_index:]).index(title) + interest_index
                #         interest_index = cur_interest_index + 1
                #         data_found = True
                #     except ValueError:
                #         pass
                try:
                    # g_logger.error(u"Search for the index of the title[%s] ......" % td[0].text)
                    data_index = self.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST.index(title)
                    data_found = True
                except ValueError:
                    pass
                if not data_found:
                    # if not_interest_index < self.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST_LEN:
                    #     try:
                    #         cur_not_interest_index = (self.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST[not_interest_index:]).index(title) + not_interest_index
                    #         not_interest_index = cur_not_interest_index + 1
                    #         data_can_ignore = True
                    #     except ValueError:
                    #         pass
                    try:
                        self.TABLE_COLUMN_FIELD_NOT_INTEREST_TITLE_LIST.index(title)
                        data_can_ignore = True
                    except ValueError:
                        pass           
# Check if the entry is NOT in the title list of interest
                if (not data_found) and (not data_can_ignore):
                    # import pdb; pdb.set_trace()
                    raise CMN.EXCEPTION.WebScrapyNotFoundException(u"The column title[%s] in company[%s] does NOT exist in the title list of interest" % (title.decode(CMN.DEF.URL_ENCODING_UTF8), self.cur_company_code_number))
                if data_can_ignore:
                    continue
# Parse the content of this entry, and the interested field into data structure
                table_column_field_index_list.append(i + 1)
                table_column_field_index_mapping_list.append(data_index)
            self.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT = collections.defaultdict(list) # Caution: Add the value in every row
# Caution: Point to the first web data
            web_data_start_index += 1
        # import pdb; pdb.set_trace()
        data_list = [self.cur_quarter_str,]
        table_field_list = [None] * self.TABLE_FIELD_INTEREST_TITLE_LIST_LEN
        # interest_index = 0
        # not_interest_index = 0
# Filter the data which is NOT interested in
        for index, tr in enumerate(web_data[web_data_start_index:web_data_end_index]):
            # print "%d: %s" % (index, tr.text)
            td = tr.select('td')
            data_found = False
            data_can_ignore = False
            data_index = None
            title = td[0].text.encode(CMN.DEF.URL_ENCODING_UTF8)
            # import pdb; pdb.set_trace()
            # if interest_index < self.TABLE_FIELD_INTEREST_TITLE_LIST_LEN:
            #     try:
            #         # g_logger.error(u"Search for the index of the title[%s] ......" % td[0].text)
            #         data_index = cur_interest_index = (self.TABLE_FIELD_INTEREST_TITLE_LIST[interest_index:]).index(title) + interest_index
            #         interest_index = cur_interest_index + 1
            #         data_found = True
            #     except ValueError:
            #         pass
            try:
                # g_logger.error(u"Search for the index of the title[%s] ......" % td[0].text)
                data_index = self.TABLE_FIELD_INTEREST_TITLE_LIST.index(title)
                data_found = True
            except ValueError:
                pass
            if not data_found:
                # if not_interest_index < self.TABLE_FIELD_NOT_INTEREST_TITLE_LIST_LEN:
                #     try:
                #         cur_not_interest_index = (self.TABLE_FIELD_NOT_INTEREST_TITLE_LIST[not_interest_index:]).index(title) + not_interest_index
                #         not_interest_index = cur_not_interest_index + 1
                #         data_can_ignore = True
                #     except ValueError:
                #         pass
                try:
                    self.TABLE_FIELD_NOT_INTEREST_TITLE_LIST.index(title)
                    data_can_ignore = True
                except ValueError:
                    pass            
# Check if the entry is NOT in the title list of interest
            if (not data_found) and (not data_can_ignore):
                # import pdb; pdb.set_trace()
                raise CMN.EXCEPTION.WebScrapyNotFoundException(u"The title[%s] in company[%s] does NOT exist in the title list of interest" % (title.decode(CMN.DEF.URL_ENCODING_UTF8), self.cur_company_code_number))
            if data_can_ignore:
                continue
# Parse the content of this entry, and the interested field into data structure
            entry_list_entry = table_column_field_index_list if self.TABLE_COLUMN_FIELD_EXIST else self.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[title]
            # print "data_index: %d, title: [%s]" % (data_index, title)
            # import pdb;pdb.set_trace()
            field_index_list = None
            if isinstance(entry_list_entry, list):
                field_index_list = entry_list_entry
            else:
                field_index_list = range(self.TABLE_FIELD_INTEREST_ENTRY_START_INDEX, self.TABLE_FIELD_INTEREST_ENTRY_START_INDEX + entry_list_entry)
            table_field_list[data_index] = []
            for field_index in field_index_list:
                # import pdb; pdb.set_trace()
                # print "data_index: %d, field_index: %d, data: [%s]" % (data_index, field_index, td[field_index].text)
                # field_value = str(td[field_index].text).strip(" ").replace(",", "")
                field_value = CMN.FUNC.remove_comma_in_string(str(td[field_index].text).strip(" "))
                if field_value.find('.') == -1: # Integer
                    table_field_list[data_index].append(int(field_value))
                else: # Floating point
                    table_field_list[data_index].append(float(field_value))
        data_is_empty = True
        for index in range(self.TABLE_FIELD_INTEREST_TITLE_LIST_LEN):
            if table_field_list[index] is not None:
                data_is_empty = False
                break
        if data_is_empty:
            # import pdb;pdb.set_trace()
            raise CMN.EXCEPTION.WebScrapyServerBusyException(u"The data[%s:%s] is EMPTY" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[self.source_type_index], self.cur_company_code_number))
# Transforms the table into the 1-Dimension list
        # import pdb;pdb.set_trace()
        padding_entry = "0" 
        if self.TABLE_COLUMN_FIELD_EXIST:
            for index in range(self.TABLE_FIELD_INTEREST_TITLE_LIST_LEN):
                # entry_list_len = entry_list_entry = self.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[self.TABLE_FIELD_INTEREST_TITLE_LIST[index]]
# Padding in column
                data_entry_list = [padding_entry] * self.TABLE_COLUMN_FIELD_INTEREST_TITLE_LIST_LEN
                for column_field_key, column_field_value in enumerate(table_column_field_index_mapping_list):
                    data_entry_list[column_field_value] = table_field_list[index][column_field_key]
                data_list.extend(data_entry_list)
                # print "index: %d, len: [%s]" % (index, len(data_list))
        else:
            for index in range(self.TABLE_FIELD_INTEREST_TITLE_LIST_LEN):
                if table_field_list[index] is None:
# Padding
                    entry_list_len = entry_list_entry = self.TABLE_FIELD_INTEREST_ENTRY_DEFAULTDICT[self.TABLE_FIELD_INTEREST_TITLE_LIST[index]]
                    # print "data_index: %d, title: [%s]" % (data_index, title)
                    if isinstance(entry_list_entry, list):
                        entry_list_len = len(entry_list_entry)
                    data_list.extend([padding_entry] * entry_list_len)
                else:
                    data_list.extend(table_field_list[index])
                # print "index: %d, len: [%s]" % (index, len(data_list))
        # import pdb;pdb.set_trace()
        return data_list


    @abstractmethod
    def _parse_web_statement_field_data(self, web_data):
        pass


    @abstractmethod
    def _parse_web_data(self, web_data):
        pass
