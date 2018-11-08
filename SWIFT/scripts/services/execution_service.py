
import os

from services.sys_defs import *
from services.key import Key
from services.report_service import Report_Service


class Execution_Service():

    def __init__(self, name=None, required_keys=None):
        self.name = name
        self.keys = []                                      # a list for all keys specified
        self.required_keys = required_keys                  # a tuple for all keys required
        self.highest_group = 1
        self.logger = Report_Service(self.name).get_logger()

    @staticmethod
    def is_comment(line):
        return line.startswith("##") | line.startswith("//")

    @staticmethod
    def strip_comment(line):
        """
        strip the comment
        :param line: a string with comments at the end. Comments symbols not at the beginning
        :return:
        """
        return line[:line.find("##")]

    def parse_control_file(self, control_file):
        """
        Parse the control file to update the keys
        :param control_file:
        :return:
        """
        if not os.path.exists(control_file):
            self.logger.error("Control file %s is not found" % control_file)
            raise FileNotFoundError("Control file %s is not found" % control_file)

        with open(control_file, mode='r') as control:
            for line in control:
                line = line.strip()
                if not self.is_comment(line):
                    key, value = self.strip_comment(line).split()
                    key_type = Control_Key_Types.REQUIRED
                    if key not in self.required_keys:
                        key_type = Control_Key_Types.OPTIONAL
                    key = Key(key=key, key_type=key_type, value=value)
                    if key.key_group > self.highest_group:
                        self.highest_group = key.key_group
                    self.keys.append(Key(key=key, key_type=key_type, value=value))

    def check_keys(self):
        """
        Check the integrity of the key specifications
        :return:
        """

        group_suffixes = ["_"+str(g) for g in range(1, self.highest_group+1)]
        check_key = None
        found = False
        for req_k in self.required_keys:
            for g in group_suffixes:
                check_key = req_k + g
                for k in self.keys:
                    if check_key == k.key:
                        found = True
                        self.logger.info("%s = %s" % (k.key, str(k.value)))
                        break

        if not found:
            self.logger.error("Required key %s not found" % check_key)
            raise ValueError("Required key %s not found" % check_key)



if __name__=='__main__':
    line = "## TRIP_TABLE_FILE_3    matrix_am.omx"
    print(Execution_Service.is_comment(line))

    line = "TRIP_TABLE_FILE_3    matrix_am.omx          ## AM working matrix "
    print(Execution_Service.strip_comment(line))