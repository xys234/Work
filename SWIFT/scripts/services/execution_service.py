
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

    OUTPUT_BUFFER = 20_000_000
    INPUT_BUFFER = 10_000_000

    def __init__(self, name=None, control_file=None, required_keys=tuple(), acceptable_keys=tuple()):
        self.name = name
        self.keys = {}                                      # a dictionary for all keys {'key_name': key_object}
        self.invalid_keys = []
        self.required_keys = required_keys                  # a tuple for all root-keys required
        self.acceptable_keys = self.common_keys + acceptable_keys              # a tuple for all root-keys acceptable
        self.acceptable_keys += self.required_keys
        self.highest_group = 1

        self.control_file = control_file
        self.execution_dir = None
        self.title = None
        self.report_file = None
        self.project_dir = None
        self.random_seed = None
        self.logger = None

        self.state = Codes_Execution_Status.OK      # todo: remove all raise errors

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

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

    @staticmethod
    def is_output_file(keyname):
        if keyname.find('NEW') >= 0 and keyname.find('_FILE') >= 0:
            return True
        return False

    def initialize_execution(self):
        """
        Update the program properties based on key values
        :param key:
        :param value:
        :param default_value:
        :return:
        """

        # Populate the program properties
        for ck in self.common_keys:
            if ck not in self.keys:
                self.keys[ck] = Key(key=ck)

        if self.keys['TITLE'].input_value:
            self.title = self.keys['TITLE'].input_value
        else:
            self.title = self.name
        self.keys['TITLE'].value = self.title

        # project directory only applies to non-common keys
        if self.keys['PROJECT_DIRECTORY'].input_value:
            self.project_dir = self.keys['PROJECT_DIRECTORY'].input_value
        else:
            self.project_dir = ''
        self.keys['PROJECT_DIRECTORY'].value = self.project_dir

        if self.keys['REPORT_FILE'].input_value:
            if self.keys['REPORT_FILE'].input_value.find('.prn') < 0:
                self.report_file = self.keys['REPORT_FILE'].input_value + ".prn"
        else:
            self.keys['REPORT_FILE'].input_value = os.path.basename(self.control_file)[:-4] + '.prn'
            self.report_file = self.keys['REPORT_FILE'].input_value
        self.report_file = os.path.join(self.execution_dir, self.report_file)
        self.keys['REPORT_FILE'].value = self.report_file

        if 'RANDOM_SEED' not in self.keys.keys():
            self.keys['RANDOM_SEED'] = Key('RANDOM_SEED', key_type=Control_Key_Types.OPTIONAL)
        self.random_seed = self.keys['RANDOM_SEED'].input_value
        self.keys['RANDOM_SEED'].value = self.random_seed

        self.logger = Report_Service(self.report_file).get_logger()

    def parse_control_file(self):
        """
        Parse the control file to update the keys
        :param control_file:
        :return:
        """

        if not os.path.exists(self.control_file):
            self.state = Codes_Execution_Status.ERROR
            raise FileNotFoundError("Control file %s is not found" % self.control_file)
        else:
            self.execution_dir = os.path.dirname(self.control_file)
            with open(self.control_file, mode='r') as control:
                for line in control:
                    line = line.strip()
                    if line and not self.is_comment(line):
                        key, value = self.split_key_value(self.strip_comment(line))
                        key_type = Control_Key_Types.REQUIRED
                        root_key, _ = Key.get_root(key)
                        if root_key not in KEY_DB:
                            self.invalid_keys.append(key)
                        else:
                            if root_key not in self.required_keys:
                                key_type = Control_Key_Types.OPTIONAL
                            key = Key(key=key, key_type=key_type, input_value=value)
                            self.keys.update({key.key: key})
                            if key.key_group > self.highest_group:
                                self.highest_group = key.key_group

    def update_key_value(self, key):
        if key.input_value is not None and key.key != 'INVALID_KEY':
            if key.value_type == Key_Value_Types.TIME_RANGE:
                val = parse_time_range(key.input_value, self.logger)
                if val[0][0] >= 0:
                    key.value = val
                else:
                    self.state = Codes_Execution_Status.ERROR
            elif key.value_type == Key_Value_Types.STRING:
                converter = str
                key.value = converter(key.input_value)
            elif key.value_type == Key_Value_Types.FLOAT:
                converter = float
                key.value = converter(key.input_value)
            elif key.value_type == Key_Value_Types.INTEGER:
                converter = int
                key.value = converter(key.input_value)
            elif key.value_type == Key_Value_Types.FILE:
                if key.key_order > Codes_Key_Thresholds.COMMON_KEY:
                    key.value = os.path.join(self.project_dir, key.input_value)


    def check_keys(self):
        """
        Populate all keys and check required key
        :return:
        """

        # Print out invalid keys
        for k in self.invalid_keys:
            self.logger.warning('Invalid key found: %s' % k)

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

                # take the value of the first defined group if not specified; otherwise default value
                key_value = KEY_DB[root_key_name].value_default
                if key_group > 1:
                    prev_group = key_group-1
                    while root_key_name+"_"+str(prev_group) not in self.keys:
                        prev_group -= 1
                    key_value = self.keys[root_key_name+"_"+str(prev_group)].input_value
                new_key = Key(key=k, key_type=key_type, input_value=key_value)
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

        # Check existence for files
        for k in self.keys.values():
            if k.value_type == Key_Value_Types.FILE and k.key_type == Control_Key_Types.REQUIRED:
                if self.is_output_file(k.key):
                    if k.value and not os.path.exists(os.path.dirname(k.value)):
                        self.state = Codes_Execution_Status.ERROR
                        self.logger.error("Path %s for %s does not exist" % (os.path.dirname(k.value), k.key))
                else:
                    if k.value and not os.path.exists(k.value):
                        self.state = Codes_Execution_Status.ERROR
                        self.logger.error("File %s for %s does not exist" % (k.value, k.key))

    def print_keys(self):
        keys = [(k, v.input_value, v.key_order) for k, v in self.keys.items()]
        keys = sorted(keys, key=lambda k: k[2])
        for k, v, _ in keys:
            self.logger.info("%s = %s" % (k, v))

    def execute(self):
        self.parse_control_file()
        self.initialize_execution()
        if self.state == Codes_Execution_Status.OK:
            self.logger.info("%s Execution Starts" % self.title)
            self.check_keys()


if __name__ == '__main__':
    import os

    program_name = "ConvertTrips"
    required_keys = ('TRIP_TABLE_FILE',)
    acceptable_keys = ('NUMBER_OF_STOPS',)

    execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
    control_file = "ConvertTrips_1.ctl"
    control_file = os.path.join(execution_path, control_file)

    exe = Execution_Service(name=program_name, control_file=control_file,
                            required_keys=required_keys, acceptable_keys=acceptable_keys)
    exe.execute()








