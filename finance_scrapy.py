#! /usr/bin/python
# -*- coding: utf8 -*-

import os
import re
import sys
import time
import subprocess
from scrapy import common as CMN
from scrapy.common.common_variable import GlobalVar as GV
from scrapy import libs as LIBS
import scrapy.scrapy_mgr as MGR
import scrapy.libs.company_profile as CompanyProfile


g_mgr = None
g_logger = CMN.LOG.get_logger()
g_company_profile_obj = None
param_cfg = {}
combination_param_cfg = {}

check_param_time_cnt = 0
check_param_time_param_first = None
set_combination_param = False

SHOW_USAGE_ALL = 0
SHOW_USAGE_AFTER_EXECUTION = 1
SHOW_USAGE_SCRAPY_ARGUMENT = 2
SHOW_USAGE_COMBINATION_ARGUMENT = 3
SHOW_USAGE_SIZE =  4
SHOW_USAGE_BIT_ALL = 0x1
SHOW_USAGE_BIT_AFTER_EXECUTION = 0x1 << 1
SHOW_USAGE_BIT_SCRAPY_ARGUMENT = 0x1 << 2
SHOW_USAGE_BIT_COMBINATION_ARGUMENT = 0x1 << 3
SHOW_USAGE_BIT_LIST = [
    SHOW_USAGE_BIT_ALL,
    SHOW_USAGE_BIT_AFTER_EXECUTION,
    SHOW_USAGE_BIT_SCRAPY_ARGUMENT,
    SHOW_USAGE_BIT_COMBINATION_ARGUMENT,
]
# SHOW_USAGE_MASK_ALL = SHOW_USAGE_BIT_ALL
SHOW_USAGE_MASK_AFTER_EXECUTION = (SHOW_USAGE_BIT_AFTER_EXECUTION |SHOW_USAGE_BIT_ALL)
SHOW_USAGE_MASK_SCRAPY_ARGUMENT = (SHOW_USAGE_BIT_SCRAPY_ARGUMENT |SHOW_USAGE_BIT_ALL)
SHOW_USAGE_MASK_COMBINATION_ARGUMENT = (SHOW_USAGE_BIT_COMBINATION_ARGUMENT |SHOW_USAGE_BIT_ALL)

def show_usage_of_after_execution():
    print "-h | --help\nDescription: The usage\nCaution: Ignore other parameters when set\n"
    print "--update_workday_calendar\nDescription: Update the workday calendar only\nCaution: Ignore other parameters when set\n"
    print "--show_workday_calendar_range\nDescription: Show the date range of the workday calendar only\nCaution: The canlendar is updated before display. Ignore other parameters when set\n"
    print "--show_data_time_range\nDescription: Show the time range of the market data in the dataset\nCaution: Ignore other parameters when set\n"
    print "--show_company_data_time_range\nDescription: Show the time range of the specific company data in the dataset\nCaution: Ignore other parameters when set\n"
    print "--remove_data\nDescription: Remove the market data in the dataset\nCaution: Ignore other parameters when set\n"
    print "--remove_company_data\nDescription: Remove the specific company data in the dataset\nCaution: Ignore other parameters when set\n"
    print "--show_scrapy_method_metadata\nDescription: Show the metadata of the scrapy method\nCaution: Ignore other parameters when set\n"
    print "--update_csv_field\nDescription: Update the CSV file description\n"


def show_usage_of_scrapy_argument():
    print "--no_scrapy\nDescription: Don't scrape Web data\n"
    print "--reserve_old\nDescription: Reserve the old destination finance folders if exist\nDefault exmaples: %s, %s\n" % (CMN.DEF.CSV_ROOT_FOLDERPATH, CMN.DEF.CSV_DST_MERGE_ROOT_FOLDERPATH)
    print "--append_before\nDescription: Update the earlier scrapy data into database\n"
    print "--dry_run\nDescription: Dry-run only. Will NOT scrape data from the web\n"
    print "--finance_folderpath\nDescription: The finance root folder\nDefault: %s\n" % CMN.DEF.CSV_ROOT_FOLDERPATH
    # print "--dataset_finance_folderpath\nDescription: Set the finance root folder to the dataset folder\n"
    print "--config_from_filename\nDescription: The methods, time_range, company from config filie\n"
    print "-m | --method\nDescription: The list of the methods\nDefault: All finance methods\nCaution: Only take effect when config_from_filename is NOT set"
    print "Scrapy Method:"
    for method_index in range(CMN.DEF.SCRAPY_METHOD_LEN):
        print "  %d: %s" % (method_index, CMN.DEF.SCRAPY_METHOD_DESCRIPTION[method_index])
    print "  Format 1: Method (ex. 1,3,5)"
    print "  Format 2: Method range (ex. 2-6)"
    print "  Format 3: Method/Method range hybrid (ex. 1,3-4,6)"
    print ""
    print "-c | --company\nDescription: The list of the company code number\nDefault: All company code nubmers\nCaution: Only take effect when config_from_filename is NOT set"
    print "  Format1: Company code number (ex. 2347)"
    print "  Format2: Company code number range (ex. 2100-2200)"
    print "  Format3: Company group number (ex. [Gg]12)"
    print "  Format4: Company code number/number range/group hybrid (ex. 2347,2100-2200,G12,2362,g2,1500-1510)"
    print ""
    print "-t | --time\nDescription: The time range\nCaution: Some Scrapy Methods can't set time range\nOnly take effect when config_from_filename is NOT set"
    print "  Format1: start_time,end_time,time_slice"
    print "  Format2: start_time,end_time"
    print "  Format1: start_time,,time_slice"
    print "  Format2: start_time,"
    print "  Format1: ,end_time,time_slice"
    print "  Format2: ,end_time"
    print "--time_at\nDescription: The time\nCaution: Some Scrapy Methods can't set time\nOnly take effect when config_from_filename is NOT set"
    print "  Format1: time,time_slice; Eqaul to --time time,time,time_slice"
    print "  Format2: time; Eqaul to --time time,time"
    print "--time_from\nDescription: From the time\nCaution: Some Scrapy Methods can't set time\nOnly take effect when config_from_filename is NOT set"
    print "  Format1: time, time_slice; Eqaul to --time time,,time_slice"
    print "  Format2: time; Eqaul to --time time,"
    print "--time_until\nDescription: Util the time\nCaution: Some Scrapy Methods can't set time\nOnly take effect when config_from_filename is NOT set"
    print "  Format1: time, time_slice; Eqaul to --time ,time,time_slice"
    print "  Format2: time; Eqaul to --time ,time"
    print "--time_until_last\nDescription: The time range until last day"
    print ""
    print "--max_data_count\nDescription: Only scrape the latest N data\n"
    print "--enable_company_not_found_exception\nDescription: Enable the mechanism that the exception is rasied while encoutering the unknown company code number\n"


def show_usage_of_combination_argument():
    print "Combination argument:\n Caution: Exclusive. Only the first combination argument takes effect. Some related arguments may be overwriten"
    print "--update_config_from_filename\nDescription: Update dataset from config file\nCaution: This arugment is equal to the argument combination as below: --finance_folderpath %s --reserve_old --config_from_filename xxx\n" % GV.FINANCE_DATASET_DATA_FOLDERPATH
    print "*** Scrapy Method ***"
    for scrapy_method_index, csv_filename in enumerate(CMN.DEF.SCRAPY_CSV_FILENAME):
        # import pdb; pdb.set_trace()
        scrapy_method = CMN.DEF.SCRAPY_METHOD_NAME[scrapy_method_index]
        scrarpy_method_costant_cfg = CMN.DEF.SCRAPY_METHOD_CONSTANT_CFG[scrapy_method]
        can_set_time_range = scrarpy_method_costant_cfg["can_set_time_range"]
        if not scrarpy_method_costant_cfg["need_company_number"]:
            print "--update_%s | --update_method%d\nDescription: Update %s\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s %s --reserve_old\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH, ("--time_until_last" if can_set_time_range else ""))
            # print "--update_%s_from_file\n--update_method%d_from_file\nDescription: Update %s\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s --reserve_old --config_from_filename\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH)
            if can_set_time_range: print "--update_%s | --update_method%d --time_from ooo\nDescription: Update Older %s\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s --reserve_old --append_before --time_from ooo\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH)
        else:
            print "--update_company_%s | --update_company_method%d\nDescription: Update %s of specific companies\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s %s --reserve_old --company xxxx\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH, ("--time_until_last" if can_set_time_range else ""))
            # print "--update_company_%s_from_file\n--update_company_method%d_from_file\nDescription: Update %s of specific companies. Companies are from file\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s --reserve_old --config_from_filename\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH)
            if can_set_time_range: print "--update_company_%s | --update_company_method%d --time_from ooo\nDescription: Update Older %s\nCaution: This arugment is equal to the argument combination as below: --method %d --finance_folderpath %s --reserve_old --append_before --time_from ooo --company xxxx\n" % (csv_filename, scrapy_method_index, scrapy_method, scrapy_method_index, GV.FINANCE_DATASET_DATA_FOLDERPATH)
    print "--update_methods\nDescription: Update dataset of all market methods"
    print "--update_company_methods\nDescription: Update dataset of all stock methods of specific companies"
    # for time_unit_description in CMN.DEF.DATA_TIME_UNIT_DESCRIPTION:
    #     time_unit_description = time_unit_description.lower()
    #     print "--update_{0}_methods\nDescription: Update dataset of market methods where the time units are equal to {0}".format(time_unit_description)
    #     print "--update_company_{0}_methods\nDescription: Update dataset of all stock methods of specific companies where the time units are equal to {0}".format(time_unit_description)
    #     print "--update_gt_{0}_methods\nDescription: Update dataset of market methods where the time units are greater than {0}".format(time_unit_description)
    #     print "--update_company_gt_{0}_methods\nDescription: Update dataset of all stock methods of specific companies where the time units are greater than {0}".format(time_unit_description)
    print "--update_(time_unit)_methods\nDescription: Update dataset of market methods where the time units are equal to (time_unit)"
    print "--update_company_(time_unit)_methods\nDescription: Update dataset of all stock methods of specific companies where the time units are equal to (time_unit)"
    print "--update_gt_(time_unit)_methods\nDescription: Update dataset of market methods where the time units are greater than (time_unit)"
    print "--update_company_gt_(time_unit)_methods\nDescription: Update dataset of all stock methods of specific companies where the time units are greater than (time_unit)"
    print "(time_unit) list: %s" % ", ".join(CMN.DEF.DATA_TIME_UNIT_DESCRIPTION).lower()


def show_usage_and_exit(show_usage_bit=SHOW_USAGE_BIT_ALL):
    print "=========================== Usage ==========================="
# Exit after execution
    if show_usage_bit & SHOW_USAGE_MASK_AFTER_EXECUTION:
        show_usage_of_after_execution()
        print ""
# Scrapy argument
    if show_usage_bit & SHOW_USAGE_MASK_SCRAPY_ARGUMENT:
        show_usage_of_scrapy_argument()
        print ""
# Combination argument
    if show_usage_bit & SHOW_USAGE_MASK_COMBINATION_ARGUMENT:
        show_usage_of_combination_argument()
        print ""
    print "============================================================="
    sys.exit(0)


def show_debug(msg):
    g_logger.debug(msg)
    if not param_cfg["silent"]:
        sys.stdout.write(msg + "\n")
def show_info(msg):
    g_logger.info(msg)
    if not param_cfg["silent"]:
        sys.stdout.write(msg + "\n")
def show_warn(msg):
    g_logger.warn(msg)
    if not param_cfg["silent"]:
        sys.stdout.write(msg + "\n")
def show_error(msg):
    g_logger.error(msg)
    if not param_cfg["silent"]:
        sys.stderr.write(msg + "\n")

def show_error_and_exit(errmsg):
    show_error(errmsg)
    sys.exit(1)


def init_param():
    # import pdb; pdb.set_trace()
    param_cfg["silent"] = False
    param_cfg["help"] = False
    param_cfg["show_help_bit"] = SHOW_USAGE_BIT_ALL
    param_cfg["update_workday_calendar"] = False
    param_cfg["show_workday_calendar_range"] = False
    param_cfg["show_data_time_range"] = False
    param_cfg["show_data_time_range_company_list"] = None
    param_cfg["remove_data"] = False
    param_cfg["remove_data_company_list"] = None
    param_cfg["show_scrapy_method_metadata"] = False
    param_cfg["no_scrapy"] = False
    param_cfg["reserve_old"] = False
    param_cfg["append_before"] = False
    param_cfg["dry_run"] = False
    # param_cfg["dataset_finance_folderpath"] = False
    param_cfg["finance_folderpath"] = None
    param_cfg["config_from_filename"] = None
    param_cfg["update_csv_field"] = False
    param_cfg["method"] = None
    param_cfg["company"] = None
    param_cfg["time_at"] = None
    param_cfg["time_from"] = None
    param_cfg["time_until"] = None
    param_cfg["time_until_last"] = False
    param_cfg["time"] = None
    param_cfg["max_data_count"] = None
    param_cfg["enable_company_not_found_exception"] = False
# combination arguments
# parameter from the config file
    combination_param_cfg["update_dataset_config_from_filename"] = None
# parameter from the setup
    combination_param_cfg["update_dataset_method"] = None
    combination_param_cfg["update_dataset_company_list"] = None
    combination_param_cfg["update_dataset_time"] = None
    combination_param_cfg["update_dataset_all_methods"] = False
    combination_param_cfg["update_dataset_time_unit_filter"] = None
    # combination_param_cfg["update_dataset_company_methods"] = None
    # combination_param_cfg['update_dataset_duplicate_setting'] = False
    # check_param_time_cnt = 0


def parse_param():
    argc = len(sys.argv)
    index = 1
    index_offset = None

    global check_param_time_cnt
    global check_param_time_param_first
    global set_combination_param

    # import pdb; pdb.set_trace()
    while index < argc:
        if not sys.argv[index].startswith('-'):
            show_error_and_exit("Incorrect Parameter format: %s" % sys.argv[index])
        if re.match("(-hs|--help_short)", sys.argv[index]):
            param_cfg["help"] = True
            param_cfg["show_help_bit"] = SHOW_USAGE_BIT_LIST[int(sys.argv[index + 1])]
            index_offset = 2
        elif re.match("(-h|--help)", sys.argv[index]):
            param_cfg["help"] = True
            index_offset = 1
        elif re.match("--update_workday_calendar", sys.argv[index]):
            param_cfg["update_workday_calendar"] = True
            index_offset = 1
        elif re.match("--show_workday_calendar_range", sys.argv[index]):
            param_cfg["show_workday_calendar_range"] = True
            index_offset = 1
        elif re.match("--show_company_data_time_range", sys.argv[index]):
            param_cfg["show_data_time_range"] = True
            param_cfg["show_data_time_range_company_list"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("--show_data_time_range", sys.argv[index]):
            param_cfg["show_data_time_range"] = True
            index_offset = 1
        elif re.match("--remove_company_data", sys.argv[index]):
            param_cfg["remove_data"] = True
            param_cfg["remove_data_company_list"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("--remove_data", sys.argv[index]):
            param_cfg["remove_data"] = True
            index_offset = 1
        elif re.match("--show_scrapy_method_metadata", sys.argv[index]):
            param_cfg["show_scrapy_method_metadata"] = True
            index_offset = 1
        elif re.match("--no_scrapy", sys.argv[index]):
            param_cfg["no_scrapy"] = True
            index_offset = 1
        elif re.match("--reserve_old", sys.argv[index]):
            param_cfg["reserve_old"] = True
            index_offset = 1
        elif re.match("--append_before", sys.argv[index]):
            param_cfg["append_before"] = True
            index_offset = 1
        elif re.match("--dry_run", sys.argv[index]):
            param_cfg["dry_run"] = True
            index_offset = 1
        # elif re.match("--dataset_finance_folderpath", sys.argv[index]):
        #     param_cfg["dataset_finance_folderpath"] = True
        #     index_offset = 1
        elif re.match("--finance_folderpath", sys.argv[index]):
            param_cfg["finance_folderpath"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("--config_from_filename", sys.argv[index]):
            param_cfg["config_from_filename"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("--update_csv_field", sys.argv[index]):
            param_cfg["update_csv_field"] = True
            index_offset = 1
        elif re.match("--method", sys.argv[index]):
            param_cfg["method"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("(-c|--company)", sys.argv[index]):
            param_cfg["company"] = sys.argv[index + 1]
            index_offset = 2
        elif re.match("--time_at", sys.argv[index]):
            param_cfg["time_at"] = sys.argv[index + 1]
            check_param_time_cnt += 1
            if check_param_time_cnt == 1:
                check_param_time_param_first = "time_at"
            index_offset = 2
        elif re.match("--time_from", sys.argv[index]):
            param_cfg["time_from"] = sys.argv[index + 1]
            check_param_time_cnt += 1
            if check_param_time_cnt == 1:
                check_param_time_param_first = "time_from"
            index_offset = 2
        elif re.match("--time_until", sys.argv[index]):
            param_cfg["time_until"] = sys.argv[index + 1]
            check_param_time_cnt += 1
            if check_param_time_cnt == 1:
                check_param_time_param_first = "time_until"
            index_offset = 2
        elif re.match("--time_until_last", sys.argv[index]):
            param_cfg["time_until_last"] = True
            check_param_time_cnt += 1
            if check_param_time_cnt == 1:
                check_param_time_param_first = "time_until_last"
            index_offset = 1
        elif re.match("(-t|--time)", sys.argv[index]):
            param_cfg["time"] = sys.argv[index + 1]
            check_param_time_cnt += 1
            if check_param_time_cnt == 1:
                check_param_time_param_first = "time"
            index_offset = 2
        elif re.match("--max_data_count", sys.argv[index]):
            param_cfg["max_data_count"] = int(sys.argv[index + 1])
            index_offset = 2
        elif re.match("--enable_company_not_found_exception", sys.argv[index]):
            param_cfg["enable_company_not_found_exception"] = True
            index_offset = 1
        elif re.match("--update_config_from_filename", sys.argv[index]):
            # import pdb; pdb.set_trace()
            if set_combination_param:
                show_warn("combination argument can only be set ONCE")
            else:
                set_combination_param = True
                combination_param_cfg['update_dataset_config_from_filename'] = sys.argv[index + 1]
            index_offset = 2
        # elif re.match("--update_company_methods", sys.argv[index]):
        elif re.match("--update_company_([\w_]*)methods", sys.argv[index]):
            if set_combination_param:
                show_warn("combination argument can only be set ONCE")
            else:
                set_combination_param = True
                combination_param_cfg["update_dataset_all_methods"] = True
                combination_param_cfg["update_dataset_company_list"] = sys.argv[index + 1]
                # import pdb; pdb.set_trace()
                time_unit_filter = re.match("--update_company_([\w_]*)methods", sys.argv[index]).group(1).rstrip("_")
                if len(time_unit_filter) > 0:
                    combination_param_cfg["update_dataset_time_unit_filter"] = time_unit_filter
            index_offset = 2
        # elif re.match("--update_methods", sys.argv[index]):
        elif re.match("--update_([\w_]*)methods", sys.argv[index]):
            # import pdb; pdb.set_trace()
            if set_combination_param:
                show_warn("combination argument can only be set ONCE")
            else:
                set_combination_param = True
                combination_param_cfg["update_dataset_all_methods"] = True
                time_unit_filter = re.match("--update_([\w_]*)methods", sys.argv[index]).group(1).rstrip("_")
                if len(time_unit_filter) > 0:
                    combination_param_cfg["update_dataset_time_unit_filter"] = time_unit_filter
            index_offset = 1
        elif re.match("--update", sys.argv[index]):
            # import pdb; pdb.set_trace()
            mobj = None
            if re.search("company", sys.argv[index]):
                if set_combination_param:
                    show_warn("combination argument can only be set ONCE")
                else:
                    set_combination_param = True
                    if re.search("method", sys.argv[index]):
                        mobj = re.match("--update_company_method([\d]{1,})", sys.argv[index])
                        if mobj is None: raise ValueError("Incorrect argument format: %s" % sys.argv[index])
                        combination_param_cfg["update_dataset_method"] = mobj.group(1)
                    else:
                        mobj = re.match("--update_company_([\w]+)", sys.argv[index])
                        if mobj is None: raise ValueError("Incorrect argument format: %s" % sys.argv[index])
                        combination_param_cfg["update_dataset_method"] = CMN.FUNC.scrapy_method_name_to_index(mobj.group(1).replace("_", " "))
                    combination_param_cfg["update_dataset_company_list"] = sys.argv[index + 1]
                    if not CMN.FUNC.scrapy_method_need_company_number(int(combination_param_cfg["update_dataset_method"])):
                        raise ValueError("The method[%s:%s] Need Company number" % (combination_param_cfg["update_dataset_method"], CMN.DEF.SCRAPY_METHOD_NAME[int(mobj.group(1))]))
                index_offset = 2
            else:
                if set_combination_param:
                    show_warn("combination argument can only be set ONCE")
                else:
                    set_combination_param = True
                    if re.search("method", sys.argv[index]):
                        mobj = re.match("--update_method([\d]{1,})", sys.argv[index])
                        if mobj is None: raise ValueError("Incorrect argument format: %s" % sys.argv[index])
                        combination_param_cfg["update_dataset_method"] = mobj.group(1)
                    else:
                        mobj = re.match("--update_([\w]+)", sys.argv[index])
                        if mobj is None: raise ValueError("Incorrect argument format: %s" % sys.argv[index])
                        combination_param_cfg["update_dataset_method"] = CMN.FUNC.scrapy_method_name_to_index(mobj.group(1).replace("_", " "))
                    if CMN.FUNC.scrapy_method_need_company_number(int(mobj.group(1))):
                        raise ValueError("The method[%s] Don't Need Company number" % combination_param_cfg["update_dataset_method"])
                index_offset = 1
            if mobj is None: raise ValueError("Incorrect argument format: %s" % sys.argv[index])
        else:
            show_error_and_exit("Unknown Parameter: %s" % sys.argv[index])
        index += index_offset


def check_param():
    global set_combination_param

    if param_cfg["help"]:
        show_warn("Show Usage and Exit. Other parameters are ignored")
    if param_cfg["update_csv_field"]:
        show_warn("Update CSV field description and Exit. Other parameters are ignored")
    if param_cfg["show_workday_calendar_range"]:
        show_warn("Show workday calendar range and Exit. Other parameters are ignored")
    if param_cfg["show_data_time_range"]:
        show_warn("Show data time range and Exit. Other parameters are ignored")
    if param_cfg['remove_data']:
        show_warn("Remove data and Exit. Other parameters are ignored")
    # import pdb; pdb.set_trace()
    # combination_argument = (combination_param_cfg["update_dataset_config_from_filename"] is not None) or (combination_param_cfg["update_dataset_method"] is not None)
    combination_argument = set_combination_param
    if combination_argument:
        append_before = False
# Disable the other parameters while combination argment is set
        if param_cfg["method"] is not None:
            show_warn("The 'method' argument won't take effect since 'combination argument' is set")
            param_cfg["method"] = None
        if param_cfg["company"] is not None:
            show_warn("company' argument won't take effect since 'combination argument' is set")
            param_cfg["company"] = None
        if param_cfg["time_at"] is not None:
            show_warn("The 'time_at' argument is ignored since 'combination argument' is set")
            param_cfg["time_at"] = None
        if param_cfg["time_from"] is not None:
            # show_warn("The 'time_from' argument is ignored since 'combination argument' is set")
            # param_cfg["time_from"] = None
            append_before = True
        if param_cfg["time_until"] is not None:
            show_warn("The 'time_until' argument is ignored since 'combination argument' is set")
            param_cfg["time_until"] = None
        if param_cfg["time_until_last"]:
            show_warn("The 'time_until_last' argument is ignored since 'combination argument' is set")
            param_cfg["time_until_last"] = False
        if param_cfg["time"] is not None:
            show_warn("time' argument won't take effect since 'combination argument' is set")
            param_cfg["time"] = None
        # if not param_cfg["dataset_finance_folderpath"]:
        #     show_warn("dataset_finance_folderpath' argument should be TRUE since 'combination argument' is set")
        #     param_cfg["dataset_finance_folderpath"] = False
        if not param_cfg["reserve_old"]:
            show_warn("reserve_old' argument should be TRUE since 'combination argument' is set")
            param_cfg["reserve_old"] = False
        if not param_cfg["append_before"]:
            show_warn("append_before' argument should be TRUE since 'combination argument' is set")
            param_cfg["append_before"] = False
        if param_cfg["config_from_filename"]:
            show_warn("The 'config_from_filename' argument won't take effect since 'update_config_from_filename' is set")
            param_cfg["config_from_filename"] = None
        if param_cfg["finance_folderpath"]:
            show_warn("The 'finance_folderpath' argument won't take effect since 'update_config_from_filename' is set")
            param_cfg["finance_folderpath"] = None
# Setup the parameters for the combination argument
        if combination_param_cfg["update_dataset_config_from_filename"] is not None:
# From config
            if combination_param_cfg["update_dataset_method"] is not None:
                show_warn("The 'update_dataset_method' argument won't take effect since 'update_config_from_filename' is set")
                combination_param_cfg["update_dataset_method"] = None
            param_cfg["config_from_filename"] = combination_param_cfg["update_dataset_config_from_filename"]
            if append_before:
                show_warn("Append Before mode is NOT supported since 'update_config_from_filename' is set")
                append_before = False
        else:
            # import pdb; pdb.set_trace()
            if combination_param_cfg["update_dataset_all_methods"]:
                if combination_param_cfg["update_dataset_company_list"] is None:
                    param_cfg["method"] = ",".join(map(str, CMN.DEF.MARKET_SCRAPY_METHOD_INDEX))
                else:
                    param_cfg["method"] = ",".join(map(str, CMN.DEF.STOCK_SCRAPY_METHOD_INDEX))
                    param_cfg["company"] = combination_param_cfg["update_dataset_company_list"]
            else:
                param_cfg["method"] = combination_param_cfg["update_dataset_method"]
                method_index = int(param_cfg["method"])
                if CMN.FUNC.scrapy_method_need_company_number(method_index):
                    param_cfg["company"] = combination_param_cfg["update_dataset_company_list"]
            if append_before:
                param_cfg["append_before"] = True
                if param_cfg["time_from"].find(",") == -1:
                    param_cfg["time"] = "{0},".format(param_cfg["time_from"])
                else:
                    [time_str, time_slice_str] = param_cfg["time_from"].split(",")
                    param_cfg["time"] = "{0},,{1}".format(time_str, time_slice_str)
            # if CMN.FUNC.scrapy_method_can_set_time_range(method_index):
            #     param_cfg["time"] = combination_param_cfg["update_dataset_time"]
        # import pdb; pdb.set_trace()
        param_cfg["finance_folderpath"] = GV.FINANCE_DATASET_DATA_FOLDERPATH
        param_cfg["reserve_old"] = True
    else:
        if param_cfg["config_from_filename"]:
            if param_cfg["method"] is not None:
                param_cfg["method"] = None
                show_warn("The 'method' argument is ignored since 'config_from_file' is set")
            if param_cfg["company"] is not None:
                param_cfg["company"] = None
                show_warn("The 'company' argument is ignored since 'config_from_file' is set")
            if param_cfg["time_at"] is not None:
                param_cfg["time_at"] = None
                show_warn("The 'time_at' argument is ignored since 'config_from_file' is set")
            if param_cfg["time_from"] is not None:
                param_cfg["time_from"] = None
                show_warn("The 'time_from' argument is ignored since 'config_from_file' is set")
            if param_cfg["time_until"] is not None:
                param_cfg["time_until"] = None
                show_warn("The 'time_until' argument is ignored since 'config_from_file' is set")
            if param_cfg["time_until_last"]:
                param_cfg["time_until_last"] = False
                show_warn("The 'time_until_last' argument is ignored since 'config_from_file' is set")
            if param_cfg["time"] is not None:
                param_cfg["time"] = None
                show_warn("The 'time' argument is ignored since 'config_from_file' is set")
        else:
            # import pdb; pdb.set_trace()
            # if param_cfg["method"] is None:
            #     # import pdb; pdb.set_trace()
            #     param_cfg["method"] = ",".join(map(str, range(CMN.DEF.SCRAPY_METHOD_END)))
            if check_param_time_cnt > 0:
                if check_param_time_cnt > 1:
                    show_warn("Multiple 'time' related arguments are set, only select the first one: %s" % check_param_time_param_first)
                if check_param_time_param_first == "time_at":
                    if param_cfg["time_at"].find(",") == -1:
                        param_cfg["time"] = "{0},{0}".format(param_cfg["time_at"])
                    else:
                        [time_str, time_slice_str] = param_cfg["time_at"].split(",")
                        param_cfg["time"] = "{0},{0},{1}".format(time_str, time_slice_str)
                elif check_param_time_param_first == "time_from":
                    if param_cfg["time_from"].find(",") == -1:
                        param_cfg["time"] = "{0},".format(param_cfg["time_from"])
                    else:
                        [time_str, time_slice_str] = param_cfg["time_from"].split(",")
                        param_cfg["time"] = "{0},,{1}".format(time_str, time_slice_str)
                elif check_param_time_param_first == "time_until":
                    if param_cfg["time_until"].find(",") == -1:
                        param_cfg["time"] = ",{0}".format(param_cfg["time_until"])
                    else:
                        [time_str, time_slice_str] = param_cfg["time_until"].split(",")
                        param_cfg["time"] = ",{0},{1}".format(time_str, time_slice_str)
                elif check_param_time_param_first == "time_until_last":
                    param_cfg["time"] = None
                else:
                    raise ValueError("Incorrect time argument: %s" % check_param_time_param_first)

            # if param_cfg["time_at"] is not None:
            #     if param_cfg["time"] is not None:
            #         param_cfg["time"] = None
            #         show_warn("The 'time' argument is ignored since 'time_at' is set")
            #     param_cfg["time"] = param_cfg["time_at"].split(",")[0] + "," + param_cfg["time_at"]
            # if param_cfg["time_until_last"]:
            #     if param_cfg["time"] is not None:
            #         param_cfg["time"] = None
            #         show_warn("The 'time' argument is ignored since 'time_until_last' is set")
            #         # param_cfg["time"] = ",%s," % CMN.FUNC.generate_today_time_str()


def setup_param():
    # import pdb; pdb.set_trace()
    if param_cfg["finance_folderpath"] is not None:
        g_mgr.set_finance_root_folderpath(param_cfg["finance_folderpath"])
# Set method/compnay/time
    if param_cfg["config_from_filename"]:
        g_mgr.set_config_filename(param_cfg["config_from_filename"])
        g_mgr.set_scrapy_config_from_file()
    else:
        g_mgr.set_scrapy_config(param_cfg["method"], param_cfg["company"], param_cfg["time"])
    g_mgr.reserve_old_finance_folder(param_cfg["reserve_old"])
    g_mgr.set_append_before_mode(param_cfg["append_before"])
    g_mgr.enable_dry_run(param_cfg["dry_run"])


def update_global_variable():
    # import pdb; pdb.set_trace()
    GV.ENABLE_COMPANY_NOT_FOUND_EXCEPTION = param_cfg["enable_company_not_found_exception"]
    GV.GLOBAL_VARIABLE_UPDATED = True


def update_workday_calendar_and_exit():
    workday_calendar = LIBS.WC.WorkdayCanlendar.Instance()
    sys.exit(0)


def show_workday_calendar_range_and_exit():
    workday_calendar = LIBS.WC.WorkdayCanlendar.Instance()
    msg = "The time range of the workday calendar: %s - %s" % (workday_calendar.FirstWorkday, workday_calendar.LastWorkday)
    show_info(msg)
    sys.exit(0)


def update_csv_field_and_exit():
    show_info("*** Update the field descriptions to Dataset: %s ***" % g_mgr.FinanceRootFolderPath)
    g_mgr.update_csv_field()
    sys.exit(0)


def show_data_time_range_and_exit():
    show_company = False
    company_number_list = None
    if param_cfg["show_data_time_range_company_list"] is not None:
        show_company = True
        company_number_list = param_cfg["show_data_time_range_company_list"].split(",")
    # import pdb; pdb.set_trace()
    if param_cfg["finance_folderpath"] is None:
        param_cfg["finance_folderpath"] = GV.FINANCE_DATASET_DATA_FOLDERPATH
    g_mgr.set_finance_root_folderpath(param_cfg["finance_folderpath"])
    print "\n* Dataset: %s\n" % param_cfg["finance_folderpath"]
    csv_time_range_ret = g_mgr.get_csv_time_range(company_number_list)
    if not show_company:
# market
        print "==========  Market  =========="
        if csv_time_range_ret is None:
            print " No Data !!!"
        else:
            for method_index, time_duration_tuple in csv_time_range_ret.items():
                print "%s:  %s %s" % (CMN.DEF.SCRAPY_METHOD_DESCRIPTION[method_index], time_duration_tuple.time_duration_start, time_duration_tuple.time_duration_end)
        print ""
    else:
# stock
        company_number_list_len = len(company_number_list)
        for company_number in company_number_list:
            print "==========  Company %s[%s]  ==========" % (company_number, get_specific_company_profile_string(company_number))
            csv_time_duration_cfg_dict = csv_time_range_ret[company_number]
            if csv_time_duration_cfg_dict is None:
                print " No Data !!!"
            else:
                for method_index, time_duration_tuple in csv_time_duration_cfg_dict.items():
                    print "%s:  %s %s" % (CMN.DEF.SCRAPY_METHOD_DESCRIPTION[method_index], time_duration_tuple.time_duration_start, time_duration_tuple.time_duration_end)
            print ""
    sys.exit(0)


def remove_data_and_exit():
    show_company = False
    company_number_list = None
    if param_cfg["remove_data_company_list"] is not None:
        show_company = True
        company_number_list = param_cfg["remove_data_company_list"].split(",")
    # import pdb; pdb.set_trace()
    if param_cfg["finance_folderpath"] is None:
        param_cfg["finance_folderpath"] = GV.FINANCE_DATASET_DATA_FOLDERPATH
    g_mgr.set_finance_root_folderpath(param_cfg["finance_folderpath"])
    print "\n* Dataset: %s\n" % param_cfg["finance_folderpath"]
    remove_data_ret = g_mgr.remove_csv_data(company_number_list)
    if not show_company:
# market
        print "==========  Market  =========="
        print " Remove Successfully" if remove_data_ret else " No Data !!!"
        print ""
    else:
# stock
        company_number_list_len = len(company_number_list)
        for company_number in company_number_list:
            print "==========  Company %s[%s]  ==========" % (company_number, get_specific_company_profile_string(company_number))
            print " Remove Successfully" if remove_data_ret[company_number] else " No Data !!!"
            print ""
    sys.exit(0)


def show_scrapy_method_metadata_and_exit():
    scrapy_method_cnt = 0
    for scrapy_method_name, scrapy_method_cfg in CMN.DEF.SCRAPY_METHOD_CONSTANT_CFG.items():
        print "***  %s [%d]  ***" % (scrapy_method_name, scrapy_method_cnt)
        print "Description: %s" % scrapy_method_cfg["description"]
        print "Module Name/Class Name: %s/%s" % (scrapy_method_cfg["module_name"], scrapy_method_cfg["class_name"])
        scrapy_time_unit = scrapy_method_cfg.get("scrapy_time_unit", None)
        if scrapy_time_unit is None:
            scrapy_time_unit = scrapy_method_cfg["data_time_unit"]
        else:
            scrapy_time_unit = CMN.DEF.TIMESLICE_GENERATE_TO_TIME_UNIT_MAPPING[scrapy_method_cfg["scrapy_time_unit"]]

        print "Scrapy/Data Time Unit: %s/%s" % (CMN.DEF.DATA_TIME_UNIT_DESCRIPTION[scrapy_time_unit], CMN.DEF.DATA_TIME_UNIT_DESCRIPTION[scrapy_method_cfg["data_time_unit"]])
        print "Set Time Range: %s" % ("Yes" if scrapy_method_cfg["can_set_time_range"] else "No")
        print ""
        scrapy_method_cnt += 1
    sys.exit(0)


def get_specific_company_profile_string(company_number):
    global g_company_profile_obj
    if g_company_profile_obj is None:
        g_company_profile_obj = CompanyProfile.CompanyProfile.Instance()
    company_profile_element_list = g_company_profile_obj.lookup_company_profile(company_number)
    specific_company_profile_string = " ".join(
        [
            company_profile_element_list[CompanyProfile.COMPANY_PROFILE_ENTRY_FIELD_INDEX_COMPANY_NAME],
            company_profile_element_list[CompanyProfile.COMPANY_PROFILE_ENTRY_FIELD_INDEX_MARKET_TYPE],
            company_profile_element_list[CompanyProfile.COMPANY_PROFILE_ENTRY_FIELD_INDEX_INDUSTRY],
            company_profile_element_list[CompanyProfile.COMPANY_PROFILE_ENTRY_FIELD_INDEX_GROUP_NUMBER],
        ]
    )
    return specific_company_profile_string


def record_exe_time(action):
    def decorator(func):
        def wrapper(*args, **kwargs):
            time_lapse_msg = u"################### %s ###################" % action
            show_info(time_lapse_msg)
            time_range_start_second = int(time.time())
            result = func(*args, **kwargs)
            time_range_end_second = int(time.time())
            time_lapse_msg = u"######### Time Lapse: %d second(s) #########\n" % (time_range_end_second - time_range_start_second)
            show_info(time_lapse_msg)
            return result
        return wrapper
    return decorator


@record_exe_time("SCRAPE")
def do_scrapy():
    show_info("* Scrape the data from the website......")
    g_mgr.do_scrapy()
    show_info("* Scrape the data from the website...... DONE!!!")
    # if g_mgr.NoScrapyCSVFound:
    #     show_warn("No Web Data while scraping:")
    #     g_mgr.show_no_scrapy()


# @record_exe_time("UPDATE_CSV_FIELD")
# def do_csv_field_update():
#     show_info("* Update the CSV field from the website......")
#     g_mgr.update_csv_field()
#     show_info("* Update the CSV field from the website...... DONE!!!")


if __name__ == "__main__":
    # sys.exit(0)

# Parse the parameters and apply to manager class
    init_param()
    parse_param()
    update_global_variable()

    # import pdb; pdb.set_trace()
    update_cfg = {
        "reserve_old_finance_folder": param_cfg["reserve_old"],
        # "dry_run_only": param_cfg["dry_run"],
        # "finance_root_folderpath": param_cfg["finance_folderpath"],
        # "config_filename": param_cfg["config_from_filename"],
        "max_data_count": param_cfg["max_data_count"],
        "time_unit_filter": combination_param_cfg["update_dataset_time_unit_filter"],
    }
    g_mgr = MGR.ScrapyMgr(**update_cfg)
# Check the parameters for the manager
    check_param()
    if param_cfg["help"]:
        show_usage_and_exit(param_cfg["show_help_bit"])
    if param_cfg["update_workday_calendar"]:
        update_workday_calendar_and_exit()
    if param_cfg["show_workday_calendar_range"]:
        show_workday_calendar_range_and_exit()
    if param_cfg["show_data_time_range"]:
        show_data_time_range_and_exit()
    if param_cfg["remove_data"]:
        remove_data_and_exit()
    if param_cfg["show_scrapy_method_metadata"]:
        show_scrapy_method_metadata_and_exit()
    # import pdb; pdb.set_trace()
# Setup the parameters for the manager
    setup_param()
    # import pdb; pdb.set_trace()
    if param_cfg["update_csv_field"]:
        update_csv_field_and_exit()

    show_info("*** Update the Dataset: %s ***" % g_mgr.FinanceRootFolderPath)
# Try to scrap the web data
    if not param_cfg["no_scrapy"]:
        do_scrapy()
