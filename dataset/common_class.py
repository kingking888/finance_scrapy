# -*- coding: utf8 -*-

from scrapy import common as CMN
import common_definition as DS_CMN_DEF
g_logger = CMN.LOG.get_logger()


class StockPrice(object):

    @classmethod
    def get_stock_price_tick(cls, stock_price, is_minus):
# price     unit
# 0.01~10   0.01 
# 10~50     0.05 
# 50~100    0.1 
# 100~500   0.5 
# 500~1000  1 
# 1000+     5
# To avlid the floating point precision.
# Multiple 100 to exploit the integer
        # if stock_price < 10.0:
        #     return 0.01
        # elif stock_price >= 10.0 and stock_price < 50.0:
        #     return 0.05
        # elif stock_price >= 50.0 and stock_price < 100.0:
        #     return 0.1
        # elif stock_price >= 100.0 and stock_price < 500.0:
        #     return 0.5
        # elif stock_price >= 100.0 and stock_price < 500.0:
        #     return 1
        # elif stock_price >= 1000.0:
        #     return 5
        stock_price_mul_100 = int((stock_price + 0.005) * 100)
        if is_minus:
            if stock_price_mul_100 > 100000:
                return -5
            elif stock_price_mul_100 <= 100000 and stock_price_mul_100 > 50000:
                return -1
            elif stock_price_mul_100 <= 50000 and stock_price_mul_100 > 10000:
                return -0.5
            elif stock_price_mul_100 <= 10000 and stock_price_mul_100 > 5000:
                return -0.1
            elif stock_price_mul_100 <= 5000 and stock_price_mul_100 > 1000:
                return -0.05
            elif stock_price_mul_100 <= 1000:
                return -0.01 
        else:       
            if stock_price_mul_100 < 1000:
                return 0.01
            elif stock_price_mul_100 >= 1000 and stock_price_mul_100 < 5000:
                return 0.05
            elif stock_price_mul_100 >= 5000 and stock_price_mul_100 < 10000:
                return 0.1
            elif stock_price_mul_100 >= 10000 and stock_price_mul_100 < 50000:
                return 0.5
            elif stock_price_mul_100 >= 50000 and stock_price_mul_100 < 100000:
                return 1
            elif stock_price_mul_100 >= 100000:
                return 5
        raise ValueError("The tick of the price [%.2f] is NOT defined", stock_price)


    @classmethod
    def get_new_stock_price_with_tick(cls, stock_price, tick_count):
        is_minus = True  if tick_count < 0 else False
        tick_count = abs(tick_count)
        new_stock_price = stock_price
        # import pdb; pdb.set_trace()
        for i in range(tick_count):
            new_stock_price += cls.get_stock_price_tick(new_stock_price, is_minus)
# To avlid the floating point precision after operation
            new_stock_price = int((new_stock_price + 0.005) * 100) / 100.0
        return new_stock_price


    @classmethod
    def get_stock_price_format_str(cls, stock_price):
# price     unit
# 0.01~10   0.01: 2 digits
# 10~50     0.05: 2 digits
# 50~100    0.1: 1 digits 
# 100~500   0.5: 1 digits 
# 500~1000  1: 0 digits 
# 1000+     5: 0 digits
# To avlid the floating point precision.
# Multiple 100 to exploit the integer
        # if stock_price < 50.0:
        #     return "%.2f" % float(stock_price)
        # elif stock_price >= 50.0 and stock_price < 500.0:
        #     return "%.1f" % float(stock_price)
        # elif stock_price >= 100.0 and stock_price < 500.0:
        #     return "%d" % int(stock_price)
        stock_price_mul_100 = int((stock_price + 0.005) * 100)
        if stock_price_mul_100 < 5000:
            return "%.2f" % float(stock_price)
        elif stock_price_mul_100 >= 5000 and stock_price_mul_100 < 50000:
            return "%.1f" % float(stock_price)
        elif stock_price_mul_100 >= 50000:
            return "%d" % int(stock_price)
        raise ValueError("The tick of the price [%.2f] is NOT defined", stock_price)


    def __init__(self, price):
        self.stock_price = price


    def __str__(self):
        return self.get_stock_price_format_str(self.stock_price)


    def __repr__(self):
        return self.get_stock_price_format_str(self.stock_price)


class HTMLReportBuilder(object):

    REPORT_HEAD = "<html><head><title>%s</title><style>%s%s%s</style></head><body>"
    REPORT_TAIL = "</p></body></html>"

    def __init__(self, company_number, save_figure, output_folder_path):
        self.company_number = company_number
        self.output_folder_path = output_folder_path
        self.buffer = self.REPORT_HEAD % (company_number, DS_CMN_DEF.DEF_SR_COLOR_HTML_STYLE_NONE, DS_CMN_DEF.DEF_SR_COLOR_HTML_STYLE_MARK, DS_CMN_DEF.DEF_SR_COLOR_HTML_STYLE_CUR)
        if save_figure:
            self.buffer += "<img src='%s.png'><br>" % company_number
        self.buffer += "<p>"


    def newline(self, count=1):
        while count > 0:
            self.buffer += "<br>"
            count -= 1
        return self


    def text(self, data_string, color_index=None, head_newline_count=0, tail_newline_count=1):        
        if head_newline_count > 0:
            self.newline(head_newline_count)
        if color_index is not None:
            html_color_tag = DS_CMN_DEF.COLOR_HTML_TAG_LIST[color_index]
            self.buffer += ("<{0}>{1}</{0}>".format(html_color_tag, data_string))
        else:
            self.buffer += data_string
        if tail_newline_count > 0:
            self.newline(tail_newline_count)
        return self


    def flush(self):
        self.buffer += self.REPORT_TAIL

        filepath = self.output_folder_path + "/%s.html" % self.company_number
        with open(filepath, "w") as fp:
            fp.write(self.buffer)
