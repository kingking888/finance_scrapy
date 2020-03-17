# -*- coding: utf8 -*-
import getpass

# RE_TEMPLATE_DATE = "[\d]{6}"
# RE_TEMPLATE_PRICE = "[\d.]{,6}"
# RE_TEMPLATE_BOOL = "(True|False)"

# ANALYZE_DATASET_FIND_SUPPORT_RESISTANCE = 0
# ANALYZE_DATASET_FIND_JUMP_GAP = 1
# ANALYZE_DATASET_FIND_312_MONTHLY_YOY_REVENUE_GROWTH = 2
# ANALYZE_DATASET_LOOKUP_SR_PRICE = 2

ANALYZE_SHOW_VALUE_INVESTMENT_REPORT = 0
ANALYZE_EMAIL_VALUE_INVESTMENT_REPORT = 1
ANALYZE_SHOW_CHIP_ANALYSIS_REPORT = 2
ANALYZE_EMAIL_CHIP_ANALYSIS_REPORT = 3
ANALYZE_METHOD_SIZE = 4
ANALYZE_METHOD_DEFAULT = ANALYZE_SHOW_VALUE_INVESTMENT_REPORT

ANALYZE_METHOD_DESCRITPION = [
	"Show the value investment of the companies",
	"Email the value investment of the companies",
	"Show the chip analysis of the market",
	"Email the chip analysis of the market",
]

SHOW_MAIN_NO_KEY_SUPPORT_RESISTANCE = 0
SHOW_MAIN_KEY_SUPPORT_ONLY = 1
SHOW_MAIN_KEY_RESISTANCE_ONLY = 2
SHOW_MAIN_KEY_SUPPORT_RESISTANCE_BOTH = 3
SHOW_MAIN_KEY_SUPPORT_RESISTANCE_SIZE = 4

SHOW_ABNORMAL_VALUE_RESULT_NONE = 0
SHOW_ABNORMAL_VALUE_RESULT_OVER_THRES_ONLY = 1
SHOW_ABNORMAL_VALUE_RESULT_UNDER_THRES_ONLY = 2
SHOW_ABNORMAL_VALUE_RESULT_ALL = 3

VALUE_INVESTMENT_REPORT_TMP_FILENAME = "value_investment_report.tmp"
DATASET_FOLDERNAME = "dataset"
DATASET_CONF_FILENAME = ".dataset.conf"
DATESET_DATE_COLUMN_NAME = "date"
DATESET_DATE_COLUMN_INDEX = 0
DATESET_COLUMN_NAME_FORMAT = "%02d%02d"

DEF_SR_FOLDER_PATH = "/home/%s/finance_support_resistance" % getpass.getuser()

SR_PRICE_TYPE_OPEN = "O"
SR_PRICE_TYPE_HIGH = "H"
SR_PRICE_TYPE_LOW = "L"
SR_PRICE_TYPE_CLOSE = "C"
SR_VOLUME = "V"

DEF_KEY_SUPPORT_RESISTANCE_MARK = "HL"
DEF_KEY_SUPPORT_RESISTANCE_LEN = 6

DETECT_ABNORMAL_VALUE_NONE = 0
DETECT_ABNORMAL_VALUE_HIGH = 1
DETECT_ABNORMAL_VALUE_LOW = 2

SR_MARK_NONE = 0
SR_MARK_KEY = 0x1
SR_MARK_JUMP_GAP = (0x1 << 2)

SR_TEXT_COLOR_BLACK = 30
SR_TEXT_COLOR_RED = 31
SR_TEXT_COLOR_YELLOW = 33
SR_TEXT_COLOR_WHITE = 37

SR_BACKGROUND_COLOR_BLACK = 40
SR_BACKGROUND_COLOR_RED = 41
SR_BACKGROUND_COLOR_YELLOW = 43
SR_BACKGROUND_COLOR_WHITE = 47

SR_HTML_TEXT_COLOR_BLACK = "black"
SR_HTML_TEXT_COLOR_RED = "red"
SR_HTML_TEXT_COLOR_YELLOW = "yellow"
SR_HTML_TEXT_COLOR_WHITE = "white"

DEF_SR_COLOR_STR_NONE = "\033[1;%d;%dm" % (SR_TEXT_COLOR_WHITE, SR_BACKGROUND_COLOR_BLACK)
DEF_SR_COLOR_STR_MARK = "\033[1;%d;%dm" % (SR_TEXT_COLOR_RED, SR_BACKGROUND_COLOR_WHITE)
DEF_SR_COLOR_STR_CUR = "\033[1;%d;%dm" % (SR_TEXT_COLOR_YELLOW, SR_BACKGROUND_COLOR_BLACK)
DEF_SR_COLOR_STR_LIST = [
	DEF_SR_COLOR_STR_NONE,
	DEF_SR_COLOR_STR_MARK,
	DEF_SR_COLOR_STR_CUR,
]

COLOR_HTML_TAG_NONE = "text_color_none"
COLOR_HTML_TAG_MARK = "text_color_mark"
COLOR_HTML_TAG_CUR = "text_color_cur"
COLOR_HTML_TAG_LIST = [
	COLOR_HTML_TAG_NONE,
	COLOR_HTML_TAG_MARK,
	COLOR_HTML_TAG_CUR,
]

DEF_SR_COLOR_HTML_STYLE_NONE = "%s {color: %s; background-color: %s;}" % (COLOR_HTML_TAG_NONE, SR_HTML_TEXT_COLOR_BLACK, SR_HTML_TEXT_COLOR_WHITE)
DEF_SR_COLOR_HTML_STYLE_MARK = "%s {color: %s; background-color: %s;}" % (COLOR_HTML_TAG_MARK, SR_HTML_TEXT_COLOR_WHITE, SR_HTML_TEXT_COLOR_RED)
DEF_SR_COLOR_HTML_STYLE_CUR = "%s {color: %s; background-color: %s;}" % (COLOR_HTML_TAG_CUR , SR_HTML_TEXT_COLOR_BLACK, SR_HTML_TEXT_COLOR_YELLOW)
DEF_SR_COLOR_HTML_STYLE_LIST = [
	DEF_SR_COLOR_HTML_STYLE_NONE,
	DEF_SR_COLOR_HTML_STYLE_MARK,
	DEF_SR_COLOR_HTML_STYLE_CUR,
]

SR_COLOR_NONE_INDEX = 0
SR_COLOR_MARK_INDEX = 1
SR_COLOR_CUR_INDEX = 2

DEF_SHOW_MAIN_KEY_SUPPORT_RESISTANCE = SHOW_MAIN_KEY_SUPPORT_ONLY
DEF_SR_SHOW_MARKED_ONLY = True
DEF_SR_GROUP_SIZE_THRES = 5
DEF_SR_AUTO_DETECT_JUMP_GAP = False
DEF_SR_DRAW_SUPPORT_RESISTANCE_DATE = True
DEF_SR_DRAW_SUPPORT_RESISTANCE_PRICE = True
DEF_SR_SAVE_FIGURE = True
DEF_SR_GENERATE_REPORT = True
DEF_SR_OUTPUT_FOLDER_PATH = DEF_SR_FOLDER_PATH
DEF_SR_CONF_DETECT_ABNORMAL_VOLUME_ENABLE = True
DEF_SR_CONF_DETECT_ABNORMAL_VOLUME_TIME_PERIOD = 20
DEF_SR_CONF_DETECT_ABNORMAL_VOLUME_THRESHOLD_RATIO_HIGH = 1.0
DEF_SR_CONF_DETECT_ABNORMAL_VOLUME_THRESHOLD_RATIO_LOW = 0.3
DEF_SR_CONF_DETECT_ABNORMAL_VOLUME_SHOW_RESULT = SHOW_ABNORMAL_VALUE_RESULT_OVER_THRES_ONLY

DEF_TICK_FOR_JUMP_GAP = 2

# The start date of the data
SR_CONF_FIELD_START_DATE = "start_date"
# The start date of finding the main key support and resistance
# Default: the start date
SR_CONF_FIELD_MAIN_KEY_SUPPORT_RESISTANCE_START_DATE = "main_key_support_resistance_start_date"
SR_CONF_FIELD_KEY_SUPPORT_RESISTANCE = "key_support_resistance"
SR_CONF_FIELD_AUTO_DETECT_JUMP_GAP = "auto_detect_jump_gap"
SR_CONF_FIELD_JUMP_GAP = "jump_gap"
SR_CONF_FIELD_TREND_LINE = "trend_line"
SR_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE = "show_main_key_support_resistance"
SR_CONF_FIELD_OVERWRITE_DATASET = "overwrite_dataset"
SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE = "draw_key_support_resistance_date"
SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE = "draw_key_support_resistance_price"
SR_CONF_FIELD_SAVE_FIGURE = "save_figure"
SR_CONF_FIELD_GENERATE_REPORT = "generate_report"
SR_CONF_FIELD_OUTPUT_FOLDER_PATH = "output_folder_path"
SR_CONF_FIELD_DETECT_ABNORMAL_VOLUME = "detect_abnormal_volume"

SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_ENABLE = "enable"
SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_TIME_PERIOD = "time_period"
SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_THRESHOLD_RATIO_HIGH = "threshold_ratio_high"
SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_THRESHOLD_RATIO_LOW = "threshold_ratio_low"
SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_SHOW_RESULT = "show_result"

SR_CONF_FIELD_LIST = [
	SR_CONF_FIELD_START_DATE,
	SR_CONF_FIELD_MAIN_KEY_SUPPORT_RESISTANCE_START_DATE,
	SR_CONF_FIELD_KEY_SUPPORT_RESISTANCE,
	SR_CONF_FIELD_AUTO_DETECT_JUMP_GAP,
	SR_CONF_FIELD_JUMP_GAP,
	SR_CONF_FIELD_TREND_LINE,
	SR_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE,
	SR_CONF_FIELD_OVERWRITE_DATASET,
	SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE,
	SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE,
	SR_CONF_FIELD_SAVE_FIGURE,
	SR_CONF_FIELD_GENERATE_REPORT,
	SR_CONF_FIELD_OUTPUT_FOLDER_PATH,
	SR_CONF_FIELD_DETECT_ABNORMAL_VOLUME,
]

SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_LIST = [
	SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_ENABLE,
	SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_TIME_PERIOD,
	SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_THRESHOLD_RATIO_HIGH,
	SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_THRESHOLD_RATIO_LOW,
	SR_CONF_DETECT_ABNORMAL_VOLUME_SUB_FIELD_SHOW_RESULT,
]

SR_CONF_FIELD_START_DATE_INDEX = 0
SR_CONF_FIELD_MAIN_KEY_SUPPORT_RESISTANCE_START_DATE_INDEX = 1
SR_CONF_FIELD_KEY_SUPPORT_RESISTANCE_INDEX = 2
SR_CONF_FIELD_AUTO_DETECT_JUMP_GAP_INDEX = 3
SR_CONF_FIELD_JUMP_GAP_INDEX = 4
SR_CONF_FIELD_TREND_LINE_INDEX = 5
SR_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE_INDEX = 6
SR_CONF_FIELD_OVERWRITE_DATASET_INDEX = 7
SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE_INDEX = 8
SR_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE_INDEX = 9
SR_CONF_FIELD_SAVE_FIGURE_INDEX = 10
SR_CONF_FIELD_GENERATE_REPORT_INDEX = 11
SR_CONF_FIELD_OUTPUT_FOLDER_PATH_INDEX = 12
SR_CONF_FIELD_DETECT_ABNORMAL_VOLUME_INDEX = 13

# Config NOT defined in config file
SR_CONF_MAIN_KEY_SUPPORT_RESISTANCE = "main_key_support_resistance"
SR_CONF_OVER_THRES_DATE_LIST = "over_thres_date_list"
SR_CONF_UNDER_THRES_DATE_LIST = "under_thres_date_list"
