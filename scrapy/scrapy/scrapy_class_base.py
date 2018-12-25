#! /usr/bin/python
# -*- coding: utf8 -*-

from abc import ABCMeta, abstractmethod

import scrapy.common as CMN
# import scrapy_definition as SC_DEF
# import scrapy_function as SC_FUNC
# import libs.common as CMN
g_logger = CMN.LOG.get_logger()


class ScrapyBase(object):

    @classmethod
    def get_web_data(cls, url, parse_url_method_func_ptr, pre_check_web_data_func_ptr=None, post_check_web_data_func_ptr=None):
        # req = CMN.FUNC.try_to_request_from_url_and_check_return(url)
        req = CMN.FUNC.request_from_url_and_check_return(url)
        if pre_check_web_data_func_ptr is not None: 
            pre_check_web_data_func_ptr(req)
        web_data = parse_url_method_func_ptr(req, cls.CLASS_CONSTANT_CFG)
        assert (web_data is not None), "web_data should NOT be None"
        if post_check_web_data_func_ptr is not None:
            post_check_web_data_func_ptr(web_data)
        return web_data


    @classmethod
    def try_get_web_data(cls, url, parse_url_method_func_ptr, ignore_data_not_found_exception=False, pre_check_web_data_func_ptr=None, post_check_web_data_func_ptr=None):
        g_logger.debug("Scrape web data from URL: %s" % url)
        web_data = None
        try:
# Grab the data from website and assemble the data to the entry of CSV
            web_data = cls.get_web_data(url, parse_url_method_func_ptr, pre_check_web_data_func_ptr, post_check_web_data_func_ptr)
        except CMN.EXCEPTION.WebScrapyNotFoundException as e:
            if not ignore_data_not_found_exception:
                errmsg = None
                if isinstance(e.message, str):
                    errmsg = "WebScrapyNotFoundException occurs while scraping URL[%s], due to: %s" % (url, e.message)
                else:
                    errmsg = u"WebScrapyNotFoundException occurs while scraping URL[%s], due to: %s" % (url, e.message)
                CMN.FUNC.try_print(errmsg)
                g_logger.error(errmsg)
                raise e
        except CMN.EXCEPTION.WebScrapyServerBusyException as e:
    # Server is busy, let's retry......
            RETRY_TIMES = 5
            SLEEP_TIME_BEFORE_RETRY = 15
            scrapy_success = False
            for retry_times in range(1, RETRY_TIMES + 1):
                if scrapy_success: break
                g_logger.warn("Server is busy, let's retry...... %d", retry_times)
                time.sleep(SLEEP_TIME_BEFORE_RETRY * retry_times)
                try:
                    web_data = cls.get_web_data(url, parse_url_method_func_ptr, pre_check_web_data_func_ptr, post_check_web_data_func_ptr)
                    assert (web_data is not None), "web_data should NOT be None"
                    if post_check_web_data_func_ptr is not None:
                        post_check_web_data_func_ptr(web_data)
                except CMN.EXCEPTION.WebScrapyNotFoundException as e:
                    if not ignore_data_not_found_exception:
                        errmsg = None
                        if isinstance(e.message, str):
                            errmsg = "RETRY[%d]! WebScrapyNotFoundException occurs while scraping URL[%s], due to: %s" % (retry_times, url, e.message)
                        else:
                            errmsg = u"RETRY[%d]! WebScrapyNotFoundException occurs while scraping URL[%s], due to: %s" % (retry_times, url, e.message)
                        CMN.FUNC.try_print(errmsg)
                        g_logger.error(errmsg)
                        raise e
                    else:
                        scrapy_success = True
                except CMN.EXCEPTION.WebScrapyServerBusyException as e:
                    pass
                else:
                    scrapy_success = True
            if not scrapy_success:
                raise CMN.EXCEPTION.WebScrapyServerBusyException("Fail to scrape URL[%s] after retry for %d times" % (url, RETRY_TIMES))
        except Exception as e:
            # import pdb;pdb.set_trace()
            if isinstance(e.message, str):
                g_logger.warn("Exception occurs while scraping URL[%s], due to: %s" % (url, e.message))
            else:
                g_logger.warn(u"Exception occurs while scraping URL[%s], due to: %s" % (url, e.message))
# Caution: web_data should NOT be None. Exception occurs while exploiting len(web_data)
# The len() function can NOT calculate the length of the None object
            web_data = []
        return web_data


    @classmethod
    def get_scrapy_method_list(cls):
        # return cls.__METHOD_NAME_LIST
        method_name_list = None
        try:
            method_name_list = cls.__METHOD_NAME_LIST
        except AttributeError:
            raise AttributeError("The variable[__METHOD_NAME_LIST] is NOT defined in :%s" % cls.__name__)
        return method_name_list


    @classmethod
    def print_scrapy_method(cls):
        # print ", ".join(cls.__METHOD_NAME_LIST)
        print ", ".join(cls.get_scrapy_method_list())


    @classmethod
    def print_scrapy_method_time_unit_description(cls, scrapy_method):
        # print ", ".join(cls.__TIME_UNIT_DESCRIPTION_LIST[scrapy_method])
        time_unit_description_list = None
        try:
            time_unit_description_list = cls.__TIME_UNIT_DESCRIPTION_LIST
        except AttributeError:
            raise AttributeError("The variable[__TIME_UNIT_DESCRIPTION_LIST] is NOT defined in :%s" % cls.__name__)
        print ", ".join(time_unit_description_list[scrapy_method])


    @classmethod
    def _write_scrapy_data_to_csv(cls, csv_data_list, scrapy_method_index, finance_parent_folderpath, company_number=None, company_group_number=None, dry_run_only=False):
        def get_old_csv_time_duration_if_exist(scrapy_method_index, csv_time_duration_dict):
            if csv_time_duration_dict is not None:
                if csv_time_duration_dict.get(scrapy_method_index, None) is not None:
                    return csv_time_duration_dict[scrapy_method_index]
            return None

        assert csv_data_list is not None, "csv_data_list should NOT be None"

        # import pdb; pdb.set_trace()
        csv_time_duration_folderpath = SC_FUNC.get_finance_data_csv_folderpath(scrapy_method_index, finance_parent_folderpath, company_group_number)
        csv_time_duration_dict = SC_FUNC.read_csv_time_duration_config_file(SC_DEF.CSV_DATA_TIME_DURATION_FILENAME, csv_time_duration_folderpath)

        url_time_unit = SC_DEF.SCRAPY_CLASS_CONSTANT_CFG[scrapy_method_index]["url_time_unit"]
# Caution: Need transfrom the time string from unicode to string
        time_duration_start = CMN.CLS.FinanceTimeBase.from_time_string(str(csv_data_list[0][0]), url_time_unit)
        time_duration_end = CMN.CLS.FinanceTimeBase.from_time_string(str(csv_data_list[-1][0]), url_time_unit)

        csv_old_time_duration_tuple = get_old_csv_time_duration_if_exist(scrapy_method_index, csv_time_duration_dict)

        new_csv_extension_time_duration, web2csv_time_duration_update_tuple = CMN.CLS.CSVTimeRangeUpdate.get_csv_time_duration_update(
            time_duration_start, 
            time_duration_end,
            csv_old_time_duration_tuple
        )
        # import pdb; pdb.set_trace()
        if  web2csv_time_duration_update_tuple is None:
            msg = None
            if company_number is not None:
                msg = u"The data[%s:%s] is Update-to-Date" % (SC_DEF.SCRAPY_METHOD_DESCRIPTION[scrapy_method_index], company_number)
            else:
                msg = u"The data[%s] is Update-to-Date" % SC_DEF.SCRAPY_METHOD_DESCRIPTION[scrapy_method_index]
            g_logger.debug(msg)
            return
# Find the file path for writing data into csv
        csv_filepath = SC_FUNC.get_finance_data_csv_filepath(scrapy_method_index, finance_parent_folderpath, company_group_number, company_number)

# Scrape the web data from each time duration
        for web2csv_time_duration_update in web2csv_time_duration_update_tuple: 

            scrapy_msg = None
            if company_number is not None:
                scrapy_msg = u"[%s:%s] %s:%s => %s" % (SC_DEF.SCRAPY_METHOD_DESCRIPTION[scrapy_method_index], company_number, web2csv_time_duration_update.NewWebStart, web2csv_time_duration_update.NewWebEnd, csv_filepath)
            else:
                scrapy_msg = "[%s] %s:%s => %s" % (SC_DEF.SCRAPY_METHOD_DESCRIPTION[scrapy_method_index], web2csv_time_duration_update.NewWebStart, web2csv_time_duration_update.NewWebEnd, csv_filepath)
            g_logger.info(scrapy_msg)
# Check if only dry-run
            if dry_run_only:
                print scrapy_msg
                continue

# If it's required to add the new web data in front of the old CSV data, a file is created to backup the old CSV data
            web2csv_time_duration_update.backup_old_csv_if_necessary(csv_filepath)
            # sub_csv_data_list = cls._filter_scrapy_data(csv_data_list, web2csv_time_duration_update)
            sub_csv_data_list = []
            if web2csv_time_duration_update.AppendDirection == CMN.CLS.CSVTimeRangeUpdate.CSV_APPEND_BEFORE:
                for csv_data in csv_data_list:
                    time_duration = CMN.CLS.FinanceTimeBase.from_time_string(str(csv_data[0]), url_time_unit)
                    if time_duration > web2csv_time_duration_update.NewWebEnd:
                        break
                    sub_csv_data_list.append(csv_data)
            elif web2csv_time_duration_update.AppendDirection == CMN.CLS.CSVTimeRangeUpdate.CSV_APPEND_AFTER:
                # for csv_data in reversed(csv_data_list):
                for csv_data in csv_data_list:
                    time_duration = CMN.CLS.FinanceTimeBase.from_time_string(str(csv_data[0]), url_time_unit)
                    if time_duration < web2csv_time_duration_update.NewWebStart:
                        continue
                    sub_csv_data_list.append(csv_data)
            else:
                raise ValueError("Unsupport AppendDirection: %d" % web2csv_time_duration_update.AppendDirection)

            g_logger.debug("Write %d data to %s" % (len(sub_csv_data_list), csv_filepath))
            CMN.FUNC.write_csv_file_data(sub_csv_data_list, csv_filepath)
# Append the old CSV data after the new web data if necessary
            web2csv_time_duration_update.append_old_csv_if_necessary(csv_filepath)

        if dry_run_only:
            return
        # import pdb; pdb.set_trace()
# Update the time duration
        if csv_time_duration_dict is None:
            csv_time_duration_dict = {}
        csv_time_duration_dict[scrapy_method_index] = new_csv_extension_time_duration
        SC_FUNC.write_csv_time_duration_config_file(SC_DEF.CSV_DATA_TIME_DURATION_FILENAME, csv_time_duration_folderpath, csv_time_duration_dict)


    @classmethod
    def check_scrapy_field_description_exist(cls, scrapy_method_index, finance_parent_folderpath):
        conf_filepath = "%s/%s/%s%s" % (finance_parent_folderpath, CMN.DEF.CSV_FIELD_DESCRIPTION_FOLDERNAME, SC_DEF.SCRAPY_CSV_FILENAME[scrapy_method_index], CMN.DEF.CSV_COLUMN_DESCRIPTION_CONF_FILENAME_POSTFIX)
        return CMN.FUNC.check_file_exist(conf_filepath)


    @classmethod
    def _write_scrapy_field_data_to_config(cls, csv_data_field_list, scrapy_method_index, finance_parent_folderpath):
        conf_folderpath = "%s/%s" % (finance_parent_folderpath, CMN.DEF.CSV_FIELD_DESCRIPTION_FOLDERNAME)
        conf_filename = ("%s" % SC_DEF.SCRAPY_CSV_FILENAME[scrapy_method_index]) + CMN.DEF.CSV_COLUMN_DESCRIPTION_CONF_FILENAME_POSTFIX
        CMN.FUNC.unicode_write_config_file_lines(csv_data_field_list, conf_filename, conf_folderpath)


    @classmethod
    def _set_scrapy_method(cls, obj, value):
        try:
            obj.method_list.index(value)
        except ValueError:
            errmsg = "The method[%s] is NOT support in %s" % (value, CMN.FUNC.get_instance_class_name(self))
            g_logger.error(errmsg)
            raise ValueError(errmsg)
        obj.scrapy_method = value
        if obj.scrapy_method_index is not None:
            g_logger.warn("The {0}::scrapy_method_index is reset since the {0}::scrapy_method is set ONLY".format(CMN.FUNC.get_instance_class_name(obj)))
            obj.scrapy_method_index = None
        raise NotImplementedError


    @classmethod
    def _set_scrapy_method_index(cls, obj, value):
        if SC_DEF.SCRAPY_CLASS_CONSTANT_CFG[value]['class_name'] != CMN.FUNC.get_instance_class_name(obj):
            raise ValueError("The scrapy index[%d] is NOT supported by the Scrapy class: %s" % (value, CMN.FUNC.get_instance_class_name(obj)))
        obj.scrapy_method_index = value
        obj.scrapy_method = SC_DEF.SCRAPY_CLASS_CONSTANT_CFG[obj.scrapy_method_index]['scrapy_class_method']


    def update_csv_field(self):
        _, csv_data_field_list = self.scrape_web()
        self._write_scrapy_field_data_to_config(csv_data_field_list, self.scrapy_method_index, self.xcfg['finance_root_folderpath'])


    def scrape_web_to_csv(self, *args, **kwargs):
        # scrapy_method = SC_DEF.SCRAPY_CLASS_CONSTANT_CFG[scrapy_method_index]["scrapy_class_method"]
        csv_data_list, _ = self.scrape_web(*args, **kwargs)
        # import pdb; pdb.set_trace()
        company_number = None
        company_group_number = None
        if SC_FUNC.is_stock_scrapy_method(self.scrapy_method_index):
            company_number = self.company_number
            company_group_number = self.company_group_number
        self._write_scrapy_data_to_csv(csv_data_list, self.scrapy_method_index, self.xcfg['finance_root_folderpath'], company_number, company_group_number, dry_run_only=self.xcfg['dry_run_only'])


    @abstractmethod
    def scrape_web(self, *args, **kwargs):
        raise NotImplementedError


    # @abstractmethod
    # def update_csv_field(self):
    #     raise NotImplementedError


    # @abstractmethod
    # def _transform_time_str2obj(cls, time_unit, time_str):
    #     raise NotImplementedError


    @property
    def ScrapyMethod(self):
        raise NotImplementedError

    @ScrapyMethod.setter
    def ScrapyMethod(self, value):
        raise NotImplementedError


    @property
    def ScrapyMethodIndex(self):
        raise NotImplementedError

    @ScrapyMethodIndex.setter
    def ScrapyMethodIndex(self, value):
        raise NotImplementedError


    @property
    def CompanyNumber(self):
        raise NotImplementedError

    @CompanyNumber.setter
    def CompanyNumber(self, value):
        raise NotImplementedError


    @property
    def CompanyGroupNumber(self):
        raise NotImplementedError

    @CompanyGroupNumber.setter
    def CompanyGroupNumber(self, value):
        raise NotImplementedError