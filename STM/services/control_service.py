import sys
import os
import re
from fnmatch import fnmatch
import itertools

from internals.key import Key
from internals.key_db import *
from services.report_service import ReportService


@unique
class State(IntEnum):
    OK = 0
    ERROR = 1


class ControlService(object):

    common_keys = (
        'TITLE', 'REPORT_FILE', 'PROJECT_DIRECTORY', 'RANDOM_SEED'
    )

    required_keys = ()
    optional_keys = ()

    def __init__(self, name=None, input_control_file=None):
        self.name = name
        self.title = None
        self.exec_dir = os.getcwd()
        self.control_file = input_control_file
        self.control_files = []
        self.keys = {}
        self.tokens = {}
        self.unused_keys = []
        self.highest_group = 0
        self.state = State.OK
        self.project_dir = None
        self.report_file = None
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
        loc_pound_sign = line.find("##")
        loc_slash_sign = line.find("//")

        if loc_pound_sign >= 0:
            return line[:loc_pound_sign]
        elif loc_slash_sign >= 0:
            return line[:loc_slash_sign]
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

    def read_control(self, control_file):
        if self.state == State.ERROR:
            return self.state
        elif not os.path.exists(control_file):
            self.state = State.ERROR
            sys.stderr.write("Control file %s is not found\n" % control_file)
            return self.state
        else:
            with open(control_file, mode='r') as control:
                for line in control:
                    line = line.strip()
                    if line and not self.is_comment(line):
                        key, value = self.split_key_value(self.strip_comment(line))
                        key, value = key.upper(), value.upper()
                        if key.startswith('CONTROL_KEY_FILE'):
                            if fnmatch(value, "@*@"):
                                value = self.tokens.get(value, None)  # for case: CONTROL_KEY_FILE  @SOME_FILE_NAME@
                            elif fnmatch(value, "%*%"):
                                value = self.tokens.get(value[1:-1], None)
                            value = os.path.join(self.exec_dir, value)   # CONTROL_KEY_FILE relative to exec_dir
                            self.read_control(value)
                        elif fnmatch(key, "@*@"):
                            self.tokens[key] = value
                        else:
                            root, _ = self.get_root_key(key)
                            if root not in KEYS_DATABASE:
                                self.unused_keys.append(key)
                            else:
                                if fnmatch(value, "%*%"):
                                    value = os.environ.get(value[1:-1])
                                self.keys[key] = Key(key=key, input_value=value)
                                if self.keys[key].group > self.highest_group:
                                    self.highest_group = self.keys[key].group

    def update_system_keys(self):
        """
        Update the system keys
        :return:
        """

        if 'TITLE' not in self.keys:
            self.keys['TITLE'] = Key('TITLE', input_value='')

        if self.keys['TITLE'].input_value:
            self.title = self.keys['TITLE'].input_value
        else:
            self.title = self.name
        self.keys['TITLE'].value = self.title

        if 'PROJECT_DIRECTORY' not in self.keys or self.keys['PROJECT_DIRECTORY'].input_value is None:
            self.keys['PROJECT_DIRECTORY'] = Key('PROJECT_DIRECTORY')
        self.project_dir = self.keys['PROJECT_DIRECTORY'].value

        if 'REPORT_FILE' not in self.keys or not self.keys['REPORT_FILE'].input_value:
            self.keys['REPORT_FILE'] = Key('REPORT_FILE', input_value=os.path.basename(self.control_file)[:-4] + '.prn')
        else:
            if self.keys['REPORT_FILE'].input_value.find('.prn') < 0:
                self.keys['REPORT_FILE'].value = self.keys['REPORT_FILE'].input_value + ".prn"
        self.report_file = os.path.join(self.project_dir, self.keys['REPORT_FILE'].value)

        if 'RANDOM_SEED' not in self.keys or not self.keys['RANDOM_SEED'].input_value:
            self.keys['RANDOM_SEED'] = Key('RANDOM_SEED')

        self.logger = ReportService(self.report_file).get_logger()

    @staticmethod
    def parse_integer_list_key(value):
        """
        Parse a range key
        :param value: a string like 1,2,4..5
        :return: a list with all individual values
        """

        res = []
        if ',' in value:
            value_split = value.strip().split(',')
            for v in value_split:
                v_split = v.split('..')
                if len(v_split) == 1:
                    res.append(int(v_split[0]))
                else:
                    lb, hb = int(v_split[0]), int(v_split[1])
                    for k in range(lb, hb+1):
                        res.append(k)
        else:
            v_split = value.split('..')
            lb, hb = int(v_split[0]), int(v_split[1])
            for k in range(lb, hb + 1):
                res.append(k)
        return res

    @staticmethod
    def parse_float_list_key(value):
        """

        :param value:
        :return:
        """

        res = []
        if ',' in value:
            value_split = value.strip().split(',')
            res = [float(v) for v in value_split]
        else:
            res.append(float(value))
        return res

    @staticmethod
    def parse_boolean_key(value):
        if str(value).upper().find('FALSE') >= 0 or str(value).upper() == '0':
            return False
        return True

    def parse_time_range(self, time_range):
        """
        parse the time range
        :param time_range: parse comma-separated ranges like "0..6, 15..19"
        :type  time_range: str
        :return: "0..6, 15..19" is parsed into [(0, 6), (15, 19)]
        """

        if not isinstance(time_range, str):
            self.logger.error("Time range must be a string")
            return [(-1, -1)]

        parts = time_range.split(",")
        ranges = []

        for part in parts:
            if part.find("..") < 0:
                self.logger.error("Time range must have both start and end times. Input is %s" % part)
                return [(-1, -1)]
            else:
                start_time, end_time = part.split("..")
                ranges.append((float(start_time), float(end_time)))
        return ranges

    @staticmethod
    def get_root_key(key_name):
        """
        get the root key name
        :param key_name:
        :type  key_name: str
        :return:
        """

        parts = key_name.split("_")
        if parts[-1].isdigit():
            return key_name[:len(key_name) - len(parts[-1]) - 1], int(parts[-1])
        else:
            return key_name, 0

    @staticmethod
    def is_output_file(key_name):
        if key_name.find('NEW') >= 0 and key_name.find('_FILE') >= 0:
            return True
        return False

    def update_key_value(self, key):
        if key.input_value is not None:
            while key.input_value is not None and fnmatch(key.input_value, "@*@"):
                key.input_value = self.tokens.get(key.input_value)
            while key.input_value is not None and fnmatch(key.input_value, "%*%"):
                key.input_value = self.tokens.get(key.input_value[1:-1])
            if key.value_type == KeyValueTypes.TIME_RANGE:
                val = self.parse_time_range(key.input_value)
                if val[0][0] >= 0:
                    key.value = val
                else:
                    self.state = State.ERROR
            elif key.value_type == KeyValueTypes.STRING:
                converter = str
                key.value = converter(key.input_value)
            elif key.value_type == KeyValueTypes.FLOAT:
                converter = float
                key.value = converter(key.input_value)
            elif key.value_type == KeyValueTypes.INTEGER:
                converter = int
                key.value = converter(key.input_value)
            elif key.value_type == KeyValueTypes.FILE:
                if key.order > Offset.NETWORK_KEYS_OFFSET and self.project_dir and key.input_value:
                    key.value = os.path.join(self.project_dir, key.input_value)
            elif key.value_type == KeyValueTypes.INTEGER_LIST:
                key.value = self.parse_integer_list_key(key.input_value)
            elif key.value_type == KeyValueTypes.FLOAT_LIST:
                key.value = self.parse_float_list_key(key.input_value)
            elif key.value_type == KeyValueTypes.BOOLEAN:
                key.value = self.parse_boolean_key(key.input_value)

    def check_keys(self):
        """
        Populate all keys and check required key;
        :return:

        The key dictionary has all the acceptable keys in fully suffixed notation; If the value is None, the key
        is not set by the user

        """

        acceptable_keys = self.required_keys + self.optional_keys
        single_keys = [k for k in acceptable_keys if KEYS_DATABASE[k].group == KeyGroupTypes.SINGLE]
        group_suffixes = ["_"+str(g) for g in range(1, self.highest_group+1)]
        group_keys = [k for k in acceptable_keys if KEYS_DATABASE[k].group == KeyGroupTypes.GROUP]
        full_key_list = single_keys + [k+s for k, s in itertools.product(group_keys, group_suffixes)]

        for k in full_key_list:
            if k not in self.keys:
                root_key_name, key_group = self.get_root_key(k)

                key_value = KEYS_DATABASE[root_key_name].default
                if key_group > 1:
                    # take the value of the first defined group if not specified; otherwise default value
                    prev_group = key_group - 1
                    while root_key_name+"_"+str(prev_group) not in self.keys:
                        prev_group -= 1
                    key_value = self.keys[root_key_name+"_"+str(prev_group)].input_value
                new_key = Key(key=k, input_value=key_value)
                self.keys.update({k: new_key})

        # Update the key value to internal data structures
        for k in self.keys.values():
            self.update_key_value(k)

        # Check required keys for each group. if a value is None, raise an error
        check_key = None
        # found = False
        for req_k in self.required_keys:
            found = False
            is_group_key = KEYS_DATABASE[req_k].group == KeyGroupTypes.GROUP
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
                self.state = State.ERROR

        # Check existence for files
        for k in self.keys.values():
            if k.key == 'PROJECT_DIRECTORY':
                if not os.path.exists(k.value):
                    self.state = State.ERROR
                    self.logger.error("Project Directory %s does not exist" % k.value)

            if k.value_type == KeyValueTypes.FILE:
                if self.is_output_file(k.key):
                    if k.value and not os.path.exists(os.path.dirname(k.value)):
                        self.state = State.ERROR
                        self.logger.error("Path %s for %s does not exist" % (os.path.dirname(k.value), k.key))
                elif k.key != 'REPORT_FILE':
                    if k.value and not os.path.exists(k.value):
                        self.state = State.ERROR
                        self.logger.error("File %s for %s does not exist" % (k.value, k.key))

    def print_keys(self):
        keys = [(k, v.value, v.order) for k, v in self.keys.items()]
        keys = sorted(keys, key=lambda k: k[2])
        for k, v, _ in keys:
            self.logger.info("%s = %s" % (k, v))
        for key in self.unused_keys:
            self.logger.warning("Unused key {:s}".format(key))
        self.logger.info("")
        self.logger.info("")

    def execute(self):
        self.read_control(self.control_file)
        self.update_system_keys()
        self.check_keys()
        self.print_keys()

        return self.state


if __name__ == '__main__':
    DEBUG = 1
    if DEBUG == 1:
        import os

        execution_path = r"C:\Projects\Repo\Work\STM\tests\Controls"
        control_file = "test_Control_Service_4.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = ControlService(input_control_file=control_file)
        # _environ = os.environ.copy()
        try:
            os.environ['ROSTER'] = "AM HR3 HBW.OMX"
            state = exe.execute()
        finally:
            os.environ.pop('ROSTER')
        exit(state)
    else:
        from sys import argv
        exe = ControlService(input_control_file=argv[1])
        state = exe.execute()
        exit(state)
