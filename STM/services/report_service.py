import logging
import sys
from logging import FileHandler
import os


class ReportService(object):

    FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    def __init__(self, report_name):
        self._report_name = report_name

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler

    def get_file_handler(self):
        if os.path.exists(os.path.dirname(self._report_name)):
            file_handler = FileHandler(self._report_name, mode='w')
            file_handler.setFormatter(self.FORMATTER)
            return file_handler
        else:
            return None

    def get_logger(self):
        logger = logging.getLogger('logger')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.get_console_handler())
        fh = self.get_file_handler()
        if fh is not None:
            logger.addHandler(fh)
        logger.propagate = False
        return logger
