
import re
import time
import os
import itertools

from services.sys_defs import *
from services.key import Key
from services.report_service import Report_Service


class Execution_Service():

    def __init__(self, name=None, required_keys=None, acceptable_keys=None):
        self.name = name
        self.keys = {}                                      # a dictionary for all keys {'key_name': key_object}
        self.required_keys = required_keys                  # a tuple for all root-keys required
        self.acceptable_keys = acceptable_keys              # a tuple for all root-keys acceptable
        self.highest_group = 1

        self.title = None
        self.report_file = None
        self.project_dir = None
        self.logger = None

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

        if line.find("##") >= 0:
            return line[:line.find("##")]
        else:
            return line

    @staticmethod
    def split_key_value(line):
        """
        Replace all tabs with 4 spaces
        :param line:
        :return:
        """

        key_value_pair = re.split(r"[\s]{2,}", line.replace('\t', '    '))
        if len(key_value_pair) > 1:
            return key_value_pair[0], key_value_pair[1]
        else:
            return key_value_pair[0], None

    def initialize_execution(self):
        """
        Update the program properties based on key values
        :param key:
        :param value:
        :param default_value:
        :return:
        """

        # Populate the program properties
        if self.keys['TITLE'].value:
            self.title = self.keys['TITLE'].value
        else:
            self.title = self.name
        self.keys['TITLE'].value = self.title

        if self.keys['PROJECT_DIRECTORY'].value:
            self.project_dir = self.keys['PROJECT_DIRECTORY'].value
        self.keys['PROJECT_DIRECTORY'].value = self.project_dir

        if self.keys['REPORT_FILE'].value:
            self.report_file = self.keys['REPORT_FILE'].value
        else:
            self.report_file = self.name + ".prn"
        self.report_file = os.path.join(self.project_dir, self.report_file)
        self.keys['REPORT_FILE'].value = self.report_file

        self.logger = Report_Service(self.report_file).get_logger()

    def parse_control_file(self, control_file):
        """
        Parse the control file to update the keys
        :param control_file:
        :return:
        """
        if not os.path.exists(control_file):
            raise FileNotFoundError("Control file %s is not found" % control_file)

        with open(control_file, mode='r') as control:
            for line in control:
                line = line.strip()
                if line and not self.is_comment(line):
                    key, value = self.split_key_value(self.strip_comment(line))
                    key_type = Control_Key_Types.REQUIRED
                    if key not in self.required_keys:
                        key_type = Control_Key_Types.OPTIONAL
                    key = Key(key=key, key_type=key_type, value=value)
                    if key.key_group > self.highest_group:
                        self.highest_group = key.key_group
                    self.keys.update({key.key: key})


    def check_keys(self):
        """
        Populate all keys and check required key
        :return:
        """

        single_keys = [k for k in self.acceptable_keys if KEY_DB[k][2] == Key_Group_Types.NOGROUP]
        group_suffixes = ["_"+str(g) for g in range(1, self.highest_group+1)]
        group_keys = [k for k in self.acceptable_keys if KEY_DB[k][2] == Key_Group_Types.GROUP]
        full_key_list = single_keys + [k+s for k, s in itertools.product(group_keys, group_suffixes)]

        for k in full_key_list:
            if k not in self.keys:
                root_key_name, key_group = Key.get_root(k)
                key_type = Control_Key_Types.OPTIONAL
                if root_key_name in self.required_keys:
                    key_type = Control_Key_Types.REQUIRED

                # take previous group's value if not specified; otherwise default value
                key_value = KEY_DB[root_key_name].value_default
                if key_group > 1:
                    key_value = self.keys[root_key_name+"_"+str(key_group-1)].value
                new_key = Key(key=k, key_type=key_type, value=key_value)
                self.keys.update({k: new_key})

        # Check required keys for each group. if a value is None, raise an error
        check_key = None
        found = False
        for req_k in self.required_keys:
            for g in group_suffixes:
                check_key = req_k + g
                for name, k in self.keys.items():
                    if check_key == name and k.value is not None:
                        found = True
                        break

        if not found:
            self.logger.error("Required key %s not found" % check_key)
            raise ValueError("Required key %s not found" % check_key)

    def print_keys(self):
        keys = [(k, v.value, v.key_order) for k, v in self.keys.items()]
        keys = sorted(keys, key=lambda k: k[2])
        for k, v, _ in keys:
            self.logger.info("%s = %s" % (k, v))

    def execute(self, control_file, main=None):
        start_time = time.time()
        self.parse_control_file(control_file)
        self.initialize_execution()
        self.check_keys()
        self.logger.info("%s Execution Starts" % self.title)
        self.print_keys()
        if main:
            main()
        end_time = time.time()
        execution_time = (end_time-start_time)/60.0
        self.logger.info("Execution finished in %.2f minutes" % execution_time)

if __name__=='__main__':
    import os

    program_name = "ConvertTrips"
    acceptable_keys = ('TITLE', 'REPORT_FILE', 'PROJECT_DIRECTORY', 'VEHICLE_CLASS')
    required_keys = ('TRIP_TABLE_FILE', 'DIURNAL_FILE', 'VALUE_OF_TIME')
    acceptable_keys = acceptable_keys + required_keys

    execution_path = "C:\Projects\Repo\Work\SWIFT\data"
    control_file = "ConvertTrips.ctl"
    control_file = os.path.join(execution_path, control_file)

    exe = Execution_Service(name=program_name, required_keys=required_keys, acceptable_keys=acceptable_keys)
    exe.execute(control_file)








