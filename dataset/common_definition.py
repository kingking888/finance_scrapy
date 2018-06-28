# -*- coding: utf8 -*-
import getpass

# RE_TEMPLATE_DATE = "[\d]{6}"
# RE_TEMPLATE_PRICE = "[\d.]{,6}"
# RE_TEMPLATE_BOOL = "(True|False)"

ANALYZE_DATASET_FIND_SUPPORT_RESISTANCE = 0
ANALYZE_DATASET_FIND_JUMP_GAP = 1
# ANALYZE_DATASET_LOOKUP_SUPPORT_RESISTANCE_PRICE = 2
ANALYZE_DATASET_SIZE = 2
ANALYZE_DATASET_DEFAULT = ANALYZE_DATASET_FIND_SUPPORT_RESISTANCE

SHOW_MAIN_NO_KEY_SUPPORT_RESISTANCE = 0
SHOW_MAIN_KEY_SUPPORT_ONLY = 1
SHOW_MAIN_KEY_RESISTANCE_ONLY = 2
SHOW_MAIN_KEY_SUPPORT_RESISTANCE_BOTH = 3
SHOW_MAIN_KEY_SUPPORT_RESISTANCE_SIZE = 4
SHOW_MAIN_KEY_SUPPORT_RESISTANCE_DEFAULT = SHOW_MAIN_KEY_SUPPORT_ONLY

DATASET_FOLDERNAME = "dataset"
DATASET_CONF_FILENAME = ".dataset.conf"
DATASET_COLUMN_DESCRIPTION_CONF_FILENAME_POSTFIX = "_column_description.conf"
DATESET_DATE_COLUMN_NAME = "date"
DATESET_DATE_COLUMN_INDEX = 0
DATESET_COLUMN_NAME_FORMAT = "%02d%02d"

DEF_SUPPORT_RESISTANCE_FOLDER_PATH = "/home/%s/finance_support_resistance" % getpass.getuser()

SUPPORT_RESISTANCE_PRICE_TYPE_OPEN = "O"
SUPPORT_RESISTANCE_PRICE_TYPE_HIGH = "H"
SUPPORT_RESISTANCE_PRICE_TYPE_LOW = "L"
SUPPORT_RESISTANCE_PRICE_TYPE_CLOSE = "C"
SUPPORT_RESISTANCE_VOLUME = "V"

DEF_KEY_SUPPORT_RESISTANCE_MARK = "HL"
DEF_KEY_SUPPORT_RESISTANCE_LEN = 6

SUPPORT_RESISTANCE_MARK_NONE = 0
SUPPORT_RESISTANCE_MARK_KEY = 0x1
SUPPORT_RESISTANCE_MARK_JUMP_GAP = (0x1 << 2)

SUPPORT_RESISTANCE_TEXT_COLOR_BLACK = 30
SUPPORT_RESISTANCE_TEXT_COLOR_RED = 31
SUPPORT_RESISTANCE_TEXT_COLOR_YELLOW = 33
SUPPORT_RESISTANCE_TEXT_COLOR_WHITE = 37

SUPPORT_RESISTANCE_TEXT_COLOR_BLACK = 30
SUPPORT_RESISTANCE_TEXT_COLOR_RED = 31
SUPPORT_RESISTANCE_TEXT_COLOR_YELLOW = 33
SUPPORT_RESISTANCE_TEXT_COLOR_WHITE = 37

SUPPORT_RESISTANCE_BACKGROUND_COLOR_BLACK = 40
SUPPORT_RESISTANCE_BACKGROUND_COLOR_RED = 41
SUPPORT_RESISTANCE_BACKGROUND_COLOR_YELLOW = 43
SUPPORT_RESISTANCE_BACKGROUND_COLOR_WHITE = 47

DEF_SUPPORT_RESISTANCE_COLOR_STR_NONE = "\033[1;%d;%dm" % (SUPPORT_RESISTANCE_TEXT_COLOR_WHITE, SUPPORT_RESISTANCE_BACKGROUND_COLOR_BLACK)
DEF_SUPPORT_RESISTANCE_COLOR_STR_MARK = "\033[1;%d;%dm" % (SUPPORT_RESISTANCE_TEXT_COLOR_RED, SUPPORT_RESISTANCE_BACKGROUND_COLOR_WHITE)
DEF_SUPPORT_RESISTANCE_COLOR_STR_CUR = "\033[1;%d;%dm" % (SUPPORT_RESISTANCE_TEXT_COLOR_YELLOW, SUPPORT_RESISTANCE_BACKGROUND_COLOR_BLACK)

DEF_SUPPORT_RESISTANCE_SHOW_MARKED_ONLY = True
DEF_SUPPORT_RESISTANCE_GROUP_SIZE_THRES = 5
DEF_SUPPORT_RESISTANCE_AUTO_DETECT_JUMP_GAP = False
DEF_SUPPORT_RESISTANCE_DRAW_SUPPORT_RESISTANCE_DATE = True
DEF_SUPPORT_RESISTANCE_DRAW_SUPPORT_RESISTANCE_PRICE = True
DEF_SUPPORT_RESISTANCE_SAVE_FIGURE = True
DEF_SUPPORT_RESISTANCE_SAVE_FIGURE_FOLDER_PATH = DEF_SUPPORT_RESISTANCE_FOLDER_PATH

DEF_TICK_FOR_JUMP_GAP = 2

SUPPORT_RESISTANCE_CONF_FIELD_START_DATE = "start_date"
SUPPORT_RESISTANCE_CONF_FIELD_KEY_SUPPORT_RESISTANCE = "key_support_resistance"
SUPPORT_RESISTANCE_CONF_FIELD_AUTO_DETECT_JUMP_GAP = "auto_detect_jump_gap"
SUPPORT_RESISTANCE_CONF_FIELD_JUMP_GAP = "jump_gap"
SUPPORT_RESISTANCE_CONF_FIELD_TREND_LINE = "trend_line"
SUPPORT_RESISTANCE_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE = "show_main_key_support_resistance"
SUPPORT_RESISTANCE_CONF_FIELD_OVERWRITE_DATASET = "overwrite_dataset"
SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE = "draw_key_support_resistance_date"
SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE = "draw_key_support_resistance_price"
SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE = "save_figure"
SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE_FOLDER_PATH = "save_figure_folder_path"

SUPPORT_RESISTANCE_CONF_FIELD_LIST = [
	SUPPORT_RESISTANCE_CONF_FIELD_START_DATE,
	SUPPORT_RESISTANCE_CONF_FIELD_KEY_SUPPORT_RESISTANCE,
	SUPPORT_RESISTANCE_CONF_FIELD_AUTO_DETECT_JUMP_GAP,
	SUPPORT_RESISTANCE_CONF_FIELD_JUMP_GAP,
	SUPPORT_RESISTANCE_CONF_FIELD_TREND_LINE,
	SUPPORT_RESISTANCE_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE,
	SUPPORT_RESISTANCE_CONF_FIELD_OVERWRITE_DATASET,
	SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE,
	SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE,
	SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE,
	SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE_FOLDER_PATH,
]

SUPPORT_RESISTANCE_CONF_FIELD_START_DATE_INDEX = 0
SUPPORT_RESISTANCE_CONF_FIELD_KEY_SUPPORT_RESISTANCE_INDEX = 1
SUPPORT_RESISTANCE_CONF_FIELD_AUTO_DETECT_JUMP_GAP_INDEX = 2
SUPPORT_RESISTANCE_CONF_FIELD_JUMP_GAP_INDEX = 3
SUPPORT_RESISTANCE_CONF_FIELD_TREND_LINE_INDEX = 4
SUPPORT_RESISTANCE_CONF_FIELD_SHOW_MAIN_KEY_SUPPORT_RESISTANCE_INDEX = 5
SUPPORT_RESISTANCE_CONF_FIELD_OVERWRITE_DATASET_INDEX = 6
SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_DATE_INDEX = 7
SUPPORT_RESISTANCE_CONF_FIELD_DRAW_SUPPORT_RESISTANCE_PRICE_INDEX = 8
SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE_INDEX = 9
SUPPORT_RESISTANCE_CONF_FIELD_SAVE_FIGURE_FOLDER_PATH_INDEX = 10

# Config NOT defined in config file
SUPPORT_RESISTANCE_CONF_MAIN_KEY_SUPPORT_RESISTANCE = "main_key_support_resistance"