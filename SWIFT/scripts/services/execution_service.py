
import re
import time
import os
import itertools

from services.sys_defs import *
from services.key import Key
from services.data_service import parse_time_range
from services.report_service import Report_Service


class Execution_Service():

    common_keys = (
        'TITLE', 'REPORT_FILE', 'PROJECT_DIRECTORY', 'RANDOM_SEED'
    )

    def __init__(self, name=None, required_keys=None, acceptable_keys=None):
        self.name = name
        self.keys = {}                                      # a dictionary for all keys {'key_name': key_object}
        self.required_keys = required_keys                  # a tuple for all root-keys required
        self.acceptable_keys = self.common_keys + acceptable_keys              # a tuple for all root-keys acceptable
        self.acceptable_keys += self.required_keys
        self.highest_group = 1

        self.title = None
        self.report_file = None
        self.project_dir = None
        self.random_seed = None
        self.logger = None

        self.state = Codes_Execution_Status.OK      # todo: remove all raise errors

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

        if 'RANDOM_SEED' not in self.keys.keys():
            self.keys['RANDOM_SEED'] = Key('RANDOM_SEED', key_type=Control_Key_Types.OPTIONAL)

        self.random_seed = self.keys['RANDOM_SEED'].value
        self.logger = Report_Service(self.report_file).get_logger()

    def parse_control_file(self, control_file):
        """
        Parse the control file to update the keys
        :param control_file:
        :return:
        """
        if not os.path.exists(control_file):
            print("Control file %s is not found" % control_file)
            self.state = Codes_Execution_Status.ERROR

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

    def update_key_value(self, key):
        if key.value:
            if key.value_type == Key_Value_Types.TIME_RANGE:
                val = parse_time_range(key.value, self.logger)
                if val[0][0] >= 0:
                    key.value = val
                else:
                    self.state = Codes_Execution_Status.ERROR
            else:
                if key.value_type == Key_Value_Types.STRING:
                    converter = str
                elif key.value_type == Key_Value_Types.FLOAT:
                    converter = float
                else:
                    converter = int
                key.value = converter(key.value)

    def check_keys(self):
        """
        Populate all keys and check required key
        :return:
        """

        single_keys = [k for k in self.acceptable_keys if KEY_DB[k].group_type == Key_Group_Types.NOGROUP]
        group_suffixes = ["_"+str(g) for g in range(1, self.highest_group+1)]
        group_keys = [k for k in self.acceptable_keys if KEY_DB[k].group_type == Key_Group_Types.GROUP]
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

        # Update the key value to internal data structures
        for k in self.keys.values():
            self.update_key_value(k)

        # Check required keys for each group. if a value is None, raise an error
        check_key = None
        found = False
        for req_k in self.required_keys:
            found = False
            is_group_key = KEY_DB[req_k].group_type == Key_Group_Types.GROUP
            if is_group_key:
                for g in group_suffixes:
                    check_key = req_k + g
                    for name, k in self.keys.items():
                        if check_key == name and k.value is not None:
                            found = True
                            break
            else:
                check_key = req_k
                for name, k in self.keys.items():
                    if check_key == name and k.value is not None:
                        found = True
                        break
            if not found:
                self.logger.error("Required key %s not found" % check_key)
                self.state = Codes_Execution_Status.ERROR

    def print_keys(self):
        keys = [(k, v.value, v.key_order) for k, v in self.keys.items()]
        keys = sorted(keys, key=lambda k: k[2])
        for k, v, _ in keys:
            self.logger.info("%s = %s" % (k, v))

    def execute(self, control_file):
        self.parse_control_file(control_file)
        if self.state == Codes_Execution_Status.OK:
            self.check_keys()
        if self.state == Codes_Execution_Status.OK:
            self.initialize_execution()


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








