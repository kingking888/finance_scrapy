import re
import threading
from datetime import datetime, timedelta
import common as CMN


class WebSrapyThread(threading.Thread):

	def __init__(self, delegation_obj):
		self.delegation_obj = delegation_obj
# 		self.datetime_range_start = datetime_range_start
# 		self.datetime_range_end = datetime_range_end
# # Check Input
#         if self.datetime_range_start is None and self.datetime_range_end is None:
#         	raise ValueError("The start and end time should NOT be NULL simultaneously")
#         if not isinstance(self.delegation_obj, WebSracpyBase):
#         	raise ValueError("delegation_obj should be inheritated from the WebSracpyBase class")

	def run(self):
		self.delegation_obj.scrap_web_to_csv()