# -*- coding: utf8 -*-

import os
import re
import sys
import time
import requests
import shutil
import copy
from datetime import datetime
import libs.common as CMN
import libs.base as BASE
import web_scrapy_company_profile as CompanyProfile
import web_scrapy_company_group_set as CompanyGroupSet
g_logger = CMN.WSL.get_web_scrapy_logger()


class WebSracpyStockMgr(BASE.MGR_BASE.WebSracpyMgrBase):

    company_profile = None
    def __init__(self):
        super(WebSracpyStockMgr, self).__init__()
        self.company_group_set = None
        self.source_type_csv_time_duration_dict = None


    @classmethod
    def __get_company_profile(cls):
        if cls.company_profile is None:
            cls.company_profile = CompanyProfile.WebScrapyCompanyProfile.Instance()
        return cls.company_profile


    def __get_finance_folderpath_format(self, finance_root_folderpath=None):
        if finance_root_folderpath is None:
            finance_root_folderpath = self.xcfg["finance_root_folderpath"]
        if finance_root_folderpath is None:
            finance_root_folderpath = CMN.DEF.DEF_CSV_ROOT_FOLDERPATH
        return ("%s/%s" % (finance_root_folderpath, CMN.DEF.DEF_CSV_STOCK_FOLDERNAME)) + "%02d"


    def _create_finance_folder_if_not_exist(self, finance_root_folderpath=None):
        self._create_finance_root_folder_if_not_exist(finance_root_folderpath)
        folderpath_format = self.__get_finance_folderpath_format(finance_root_folderpath)
        for index in range(self.__get_company_profile().CompanyGroupSize):
            folderpath = folderpath_format % index
            g_logger.debug("Try to create new folder: %s" % folderpath)
            CMN.FUNC.create_folder_if_not_exist(folderpath)


    def _remove_old_finance_folder(self, finance_root_folderpath=None):
# Remove the old data if necessary
        folderpath_format = self.__get_finance_folderpath_format(finance_root_folderpath)
        for index in range(self.__get_company_profile().CompanyGroupSize):
            folderpath = folderpath_format % index
            g_logger.debug("Remove old folder: %s" % folderpath)
            shutil.rmtree(folderpath, ignore_errors=True)


    def _init_csv_time_duration(self, company_group_set=None):
        # import pdb; pdb.set_trace()
        assert self.source_type_csv_time_duration_dict is None, "self.source_type_csv_time_duration_dict should be None"
        if company_group_set is None:
            company_group_set = self.company_group_set
        if company_group_set is None:
            company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        self.source_type_csv_time_duration_dict = {}
        for company_group_number, company_code_number_list in company_group_set.items():
            for company_code_number in company_code_number_list:
                # csv_time_duration_list = [None] * CMN.DEF.DEF_DATA_SOURCE_STOCK_SIZE
                self.source_type_csv_time_duration_dict[company_code_number] = {}


    def __parse_csv_time_duration_cfg(self, finance_root_folderpath=None, company_group_set=None):
        # whole_company_number_in_group_dict = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        folderpath_format = self.__get_finance_folderpath_format(finance_root_folderpath)
        if company_group_set is None:
            company_group_set = self.company_group_set
        if company_group_set is None:
            company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        source_type_csv_time_duration_dict = {}
        # for company_group_number, company_code_number_list in whole_company_number_in_group_dict:
        for company_group_number, company_code_number_list in company_group_set.items():
            folderpath_in_group = folderpath_format % int(company_group_number)
# If the company group folder does NOT exist, ignore it...
            if not CMN.FUNC.check_file_exist(folderpath_in_group):
                continue
            for company_code_number in company_code_number_list:
                csv_data_folderpath = "%s/%s" % (folderpath_in_group, company_code_number) 
                g_logger.debug("Try to parse CSV time range config in the folder: %s ......" % csv_data_folderpath)
                csv_time_duration_dict = CMN.FUNC.parse_csv_time_duration_config_file(CMN.DEF.DEF_CSV_DATA_TIME_DURATION_FILENAME, csv_data_folderpath)
                if csv_time_duration_dict is None:
                    g_logger.debug("The CSV time range config file[%s] does NOT exist !!!" % CMN.DEF.DEF_CSV_DATA_TIME_DURATION_FILENAME)
                    continue
# update the time range of each source type of comapny from config files
                # csv_time_duration_list = [None] * CMN.DEF.DEF_DATA_SOURCE_STOCK_SIZE
                # for source_type_index, time_duration_tuple in csv_time_duration_dict.items():
                #     csv_time_duration_list[source_type_index - CMN.DEF.DEF_DATA_SOURCE_STOCK_START] = time_duration_tuple
                source_type_csv_time_duration_dict[company_code_number] = csv_time_duration_dict
        return source_type_csv_time_duration_dict if source_type_csv_time_duration_dict else None


    def _read_old_csv_time_duration(self):
        assert self.source_type_csv_time_duration_dict is not None, "self.source_type_csv_time_duration_dict should NOT be None"
#         # whole_company_number_in_group_dict = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
#         folderpath_format = self.__get_finance_folderpath_format()
#         # self.source_type_csv_time_duration_dict = {}
#         # for company_group_number, company_code_number_list in whole_company_number_in_group_dict:
#         for company_group_number, company_code_number_list in self.company_group_set.items():
#             folderpath_in_group = folderpath_format % int(company_group_number)
# # If the company group folder does NOT exist, ignore it...
#             if not CMN.FUNC.check_file_exist(folderpath_in_group):
#                 continue
#             for company_code_number in company_code_number_list:
#                 csv_data_folderpath = "%s/%s" % (folderpath_in_group, company_code_number) 
#                 g_logger.debug("Try to parse CSV time range config in the folder: %s ......" % csv_data_folderpath)
#                 csv_time_duration_dict = CMN.FUNC.parse_csv_time_duration_config_file(CMN.DEF.DEF_CSV_DATA_TIME_DURATION_FILENAME, csv_data_folderpath)
#                 if csv_time_duration_dict is None:
#                     g_logger.debug("The CSV time range config file[%s] does NOT exist !!!" % CMN.DEF.DEF_CSV_DATA_TIME_DURATION_FILENAME)
#                     continue
# # update the time range of each source type of comapny from config files
#                 # csv_time_duration_list = [None] * CMN.DEF.DEF_DATA_SOURCE_STOCK_SIZE
#                 # for source_type_index, time_duration_tuple in csv_time_duration_dict.items():
#                 #     csv_time_duration_list[source_type_index - CMN.DEF.DEF_DATA_SOURCE_STOCK_START] = time_duration_tuple
#                 self.source_type_csv_time_duration_dict[company_code_number] = csv_time_duration_dict
        source_type_csv_time_duration_dict = self.__parse_csv_time_duration_cfg()
        if source_type_csv_time_duration_dict is not None:
            self.source_type_csv_time_duration_dict = source_type_csv_time_duration_dict


    def _update_new_csv_time_duration(self, web_scrapy_obj):
        # import pdb; pdb.set_trace()
        assert self.source_type_csv_time_duration_dict is not None, "self.source_type_csv_time_duration_dict should NOT be None"
        new_csv_time_duration_dict = web_scrapy_obj.get_new_csv_time_duration_dict()
        # source_type_index_offset = web_scrapy_obj.SourceTypeIndex - CMN.DEF.DEF_DATA_SOURCE_STOCK_START
        for company_number, time_duration_tuple in new_csv_time_duration_dict.items():
            self.source_type_csv_time_duration_dict[company_number][web_scrapy_obj.SourceTypeIndex] = time_duration_tuple


    def __write_new_csv_time_duration_to_cfg(self, finance_root_folderpath=None, source_type_csv_time_duration_dict=None, company_group_set=None):
        # import pdb; pdb.set_trace()
        folderpath_format = self.__get_finance_folderpath_format(finance_root_folderpath)
        if source_type_csv_time_duration_dict is None:
            source_type_csv_time_duration_dict = self.source_type_csv_time_duration_dict
        if company_group_set is None:
            company_group_set = self.company_group_set
        if company_group_set is None:
            company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        for company_group_number, company_code_number_list in company_group_set.items():
            folderpath_in_group = folderpath_format % int(company_group_number)
            for company_code_number in company_code_number_list:
                csv_data_folderpath = "%s/%s" % (folderpath_in_group, company_code_number) 
# Create the folder for each company if not exist
                CMN.FUNC.create_folder_if_not_exist(csv_data_folderpath)
                g_logger.debug("Try to write CSV time range config in the folder: %s ......" % csv_data_folderpath)
                CMN.FUNC.write_csv_time_duration_config_file(CMN.DEF.DEF_CSV_DATA_TIME_DURATION_FILENAME, csv_data_folderpath, source_type_csv_time_duration_dict[company_code_number])


    def _write_new_csv_time_duration(self):
        self.__write_new_csv_time_duration_to_cfg()


    def __transform_company_word_list_to_group_set(self, company_word_list):
        """
        The argument type:
        Company code number: 2347
        Company code number range: 2100-2200
        Company group number: [Gg]12
        Company code number/number range hybrid: 2347,2100-2200,2362,g2,1500-1510
        """
        self.company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet()
        for company_number in company_word_list:
            mobj = re.match("([\d]{4})-([\d]{4})", company_number)
            if mobj is None:
# Check if data is company code/group number
                mobj = re.match("[Gg]([\d]{1,})", company_number)
                if mobj is None:
# Company code number
                    if not re.match("([\d]{4})", company_number):
                        raise ValueError("Unknown company number format: %s" % company_number)
                    self.company_group_set.add_company(company_number)
                else:
# Compgny group number
                    company_group_number = int(mobj.group(1))
                    self.company_group_set.add_company_group(company_group_number)
            else:
# Company code number Range
                start_company_number_int = int(mobj.group(1))
                end_company_number_int = int(mobj.group(2))
                number_list = []
                for number in range(start_company_number_int, end_company_number_int + 1):
                    number_list.append("%04d" % number)
                self.company_group_set.add_company_word_list(number_list)
        self.company_group_set.add_done()


    def set_company_from_file(self, filename):
        company_word_list = CMN.FUNC.parse_source_type_time_duration_config_file(filename)
        self.__transform_company_word_list_to_group_set(company_word_list)


    def set_company(self, company_word_list):
        self.__transform_company_word_list_to_group_set(company_word_list)


    # def initialize(**kwargs):
    #     super(WebSracpyStockMgr, self).initialize(**kwargs)
    #     if kwargs.get("company_word_list", None) is not None:
    #         company_group_set = WebScrapyCompanyGroupSet()
    #         for company_number in kwargs["company_word_list"]:
    #             company_group_set.add_company(company_number)
    #         company_group_set.add_done();
    #         if kwargs.get("company_group_set", None) is not None:
    #             g_logger.warn("The company_group_set field is ignored......")
    #     elif kwargs.get("company_group_set", None) is not None:
    #         self.xcfg["company_group_set"] = kwargs["company_group_set"]
    #     else:
    #         self.xcfg["company_group_set"] = CompanyGroupSet.get_whole_company_group_set()


    # def _add_cfg_for_scrapy_obj(self, source_type_time_duration):
    #     scrapy_obj_cfg = self._init_cfg_for_scrapy_obj(source_type_time_duration)
    #     if not scrapy_obj_cfg.has_key("company_group_set") # for sub group company set in multi-thread
    #         scrapy_obj_cfg["company_group_set"] = self.company_group_set
    #     scrapy_obj_cfg["csv_time_duration_table"] = self.source_type_csv_time_duration_dict
    def _scrap_single_source_data(self, source_type_time_duration):
        # import pdb;pdb.set_trace()
        if self.company_group_set is None:
            self.company_group_set = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_group_set()
# Setup the time duration configuration for the scrapy object
        scrapy_obj_cfg = self._init_cfg_for_scrapy_obj(source_type_time_duration)
        scrapy_obj_cfg["csv_time_duration_table"] = self.source_type_csv_time_duration_dict
# Create the scrapy object to transform the data from Web to CSV
        if self.multi_thread_amount is not None:
            g_logger.debug("Scrap %s in %d threads" % (CMN.DEF.DEF_DATA_SOURCE_INDEX_MAPPING[source_type_time_duration.source_type_index], self.multi_thread_amount))
# Run in multi-threads
            sub_scrapy_obj_cfg_list = []
            sub_company_group_list = self.company_group_set.get_sub_company_group_set_list(self.multi_thread_amount)
# Perpare the config for each thread
            for sub_company_group in sub_company_group_list:
                sub_scrapy_obj_cfg = copy.deepcopy(scrapy_obj_cfg)
                sub_scrapy_obj_cfg["company_group_set"] = sub_company_group
                sub_scrapy_obj_cfg_list.append(sub_scrapy_obj_cfg)
# Start the thread to scrap data
            self._multi_thread_scrap_web_data_to_csv_file(source_type_time_duration.source_type_index, sub_scrapy_obj_cfg_list)
        else:
            scrapy_obj_cfg["company_group_set"] = self.company_group_set
            self._scrap_web_data_to_csv_file(source_type_time_duration.source_type_index, **scrapy_obj_cfg)


    def show_company_list_in_finance_folder(self, finance_root_folderpath=None):
        # import pdb; pdb.set_trace()
        if not CMN.FUNC.check_file_exist(self.xcfg["finance_root_folderpath"]):
            print "The root finance folder[%s] does NOT exist" % self.xcfg["finance_root_folderpath"]
            return
        company_group_folderpath_format = self.__get_finance_folderpath_format()
        # for index in range(self.__get_company_profile().CompanyGroupSize):
        whole_company_number_in_group_dict = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        for company_group_number, company_code_number_list in whole_company_number_in_group_dict.items():
            company_group_folderpath = company_group_folderpath_format % company_group_number
            if not CMN.FUNC.check_file_exist(company_group_folderpath):
                raise ValueError("The folder[%s] should exist !!!" % company_group_folderpath)
            company_ode_number_in_group_list = []
            for company_code_number in company_code_number_list:
                company_folderpath = "%s/%s" % (company_group_folderpath, company_code_number)
                if not CMN.FUNC.check_file_exist(company_folderpath):
                    continue
                company_ode_number_in_group_list.append(company_code_number)
            if len(company_ode_number_in_group_list) != 0:
                print "%s: %s" % (company_group_number, ",".join(company_ode_number_in_group_list))


    # def do_scrapy(self):
    #     self._scrap_data()


    def check_scrapy(self):
        file_not_found_list = []
        file_is_empty_list = []
        for source_type_time_duration in self.source_type_time_duration_list:
            for company_group_number, company_code_number_list in self.company_group_set.items():
                for company_code_number in company_code_number_list:
                    csv_filepath = CMN.FUNC.assemble_stock_csv_filepath(self.xcfg["finance_root_folderpath"], source_type_time_duration.source_type_index, company_code_number, company_group_number)
# Check if the file exists
                    if not os.path.exists(csv_filepath):
                        file_not_found_list.append(
                            {
                                "index": source_type_time_duration.source_type_index,
                                "filename" : CMN.FUNC.get_filename_from_filepath(csv_filepath),
                            }
                        )
                    elif os.path.getsize(csv_filepath) == 0:
                        file_is_empty_list.append(
                            {
                                "index": source_type_time_duration.source_type_index,
                                "filename" : CMN.FUNC.get_filename_from_filepath(csv_filepath),
                            }
                        )
        return (file_not_found_list, file_is_empty_list)


    def _find_existing_source_type_finance_folder_index(self, csv_time_duration_cfg_list, source_type_index, company_code_number):
# Search for the index of the finance folder which the specific source type index exists
# -1 if not found
# Exception occur if the source type is found in more than one finance folder
        finance_folder_index = -1
        for index, csv_time_duration_cfg in enumerate(csv_time_duration_cfg_list):
            if not csv_time_duration_cfg.has_key(company_code_number):
                continue
            # import pdb; pdb.set_trace()
            if csv_time_duration_cfg[company_code_number].has_key(source_type_index):
                if finance_folder_index != -1:
                    raise ValueError("The source type index[%d] in %s is duplicate" % (source_type_index, company_code_number))
                else:
                    finance_folder_index = index
        return finance_folder_index


    def merge_finance_folder(self, finance_folderpath_src_list, finance_folderpath_dst):
        self._check_merge_finance_folder_exist(finance_folderpath_src_list, finance_folderpath_dst)
        if CMN.FUNC.check_file_exist(finance_folderpath_dst):
            raise ValueError("The destination folder[%s] after mering has already exist" % finance_folderpath_dst)
        self._create_finance_folder_if_not_exist(finance_folderpath_dst)
# Find source type list in each source finance folder
        csv_time_duration_cfg_list = []
        for finance_folderpath_src in finance_folderpath_src_list:
            csv_time_duration_cfg_list.append(self.__parse_csv_time_duration_cfg(finance_folderpath_src))
# Merge the finance folder
# Copy the CSV files from source folder to destiantion one
        (source_type_index_start, source_type_index_end) = CMN.FUNC.get_source_type_index_range()
        new_source_type_csv_time_duration = {}
        # import pdb; pdb.set_trace()
        company_group_set_dst = {}
        whole_company_number_in_group_dict = CompanyGroupSet.WebScrapyCompanyGroupSet.get_whole_company_number_in_group_dict()
        for company_group_number, company_code_number_list in whole_company_number_in_group_dict.items():
            for company_code_number in company_code_number_list:
                new_source_type_csv_time_duration_for_one_company = {}           
                for source_type_index in range(source_type_index_start, source_type_index_end):
                    finance_folder_index = self._find_existing_source_type_finance_folder_index(csv_time_duration_cfg_list, source_type_index, company_code_number)
                    if finance_folder_index == -1:
                        continue
                    src_csv_filepath = CMN.FUNC.assemble_stock_csv_filepath(finance_folderpath_src_list[finance_folder_index], source_type_index, company_code_number, company_group_number)
                    CMN.FUNC.create_folder_if_not_exist(CMN.FUNC.assemble_stock_csv_folderpath(finance_folderpath_dst, company_code_number, company_group_number))
                    dst_csv_filepath = CMN.FUNC.assemble_stock_csv_filepath(finance_folderpath_dst, source_type_index, company_code_number, company_group_number)
                    CMN.FUNC.copy_file(src_csv_filepath, dst_csv_filepath)
# Keep track of the company code number of exsiting data
                    if not company_group_set_dst.has_key(company_group_number):
                        company_group_set_dst[company_group_number] = set()
                    company_group_set_dst[company_group_number].add(company_code_number)
# Update the new time duration config
                    # import pdb; pdb.set_trace()
                    new_source_type_csv_time_duration_for_one_company[source_type_index] = csv_time_duration_cfg_list[finance_folder_index][company_code_number][source_type_index]
                new_source_type_csv_time_duration[company_code_number] = new_source_type_csv_time_duration_for_one_company
        # import pdb; pdb.set_trace()
        self.__write_new_csv_time_duration_to_cfg(finance_folderpath_dst, new_source_type_csv_time_duration, company_group_set_dst)


    def enable_multithread(self, thread_amount):
        self.multi_thread_amount = thread_amount


