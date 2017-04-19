# -*- coding: utf8 -*-


class WebScrapyException(Exception):
    """Base-class for all web scrapy exceptions. 

    IMPORTANT: Critical exception, Can't be ignored
    """
    def __init__(self, message=None):
        self.message = message


    def __str__(self):
        return "[WSE] %s" % self.message


class WebScrapyNotFoundException(WebScrapyException):
    """Class for not found exceptions"""
    pass
    # def __init__(self):
    #     pass


class WebScrapyIncorrectFormatException(WebScrapyException):
    """Class for incorrect format exceptions"""
    pass


class WebScrapyServerBusyException(WebScrapyException):
    """Class for server busy exceptions"""
    pass