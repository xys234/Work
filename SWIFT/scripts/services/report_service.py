import logging
import sys
from logging import FileHandler


class Report_Service():

    FORMATTER = logging.Formatter("%(asctime)s — %(levelname)s: %(message)s")

    def __init__(self, report_name):
        self._report_name = report_name

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler

    def get_file_handler(self):
        file_handler = FileHandler(self._report_name, mode='w')
        file_handler.setFormatter(self.FORMATTER)
        return file_handler

    def get_logger(self):
        logger = logging.getLogger(self._report_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False
        return logger