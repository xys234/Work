import pytest
import os

from services.sys_defs import *
from services.execution_service import Execution_Service


@pytest.mark.skip(reason="passed")
def test_missing_control_file():
    name = 'ConvertTrips'
    control_file = r'cases\ConvertTrips_Not_Exist.ctl'
    es = Execution_Service(name=name, control_file=control_file)
    with pytest.raises(FileNotFoundError):
        es.execute()


@pytest.mark.skip(reason="passed")
def test_missing_required_key():
    """
    Test missing required key; The program status should be ERROR
    :return:
    """
    name = 'ConvertTrips'
    control_file = r'cases\ConvertTrips_1.ctl'
    required_keys = ('TRIP_TABLE_FILE',)
    acceptable_keys = ('NUMBER_OF_STOPS',)
    es = Execution_Service(name=name, control_file=control_file,
                           required_keys=required_keys, acceptable_keys=acceptable_keys)
    es.execute()
    assert es.state == Codes_Execution_Status.ERROR


def test_comment_line():
    """
    test keys commented; should take default values
    :return:
    """
    name = 'ConvertTrips'
    control_file = r'cases\ConvertTrips_2.ctl'
    required_keys = ('TRIP_TABLE_FILE',)
    acceptable_keys = ('NUMBER_OF_STOPS','MATRIX_NAME','TIME_PERIOD_RANGE')
    comment_keys = ('MATRIX_NAME_1', 'TIME_PERIOD_RANGE_1')

    es = Execution_Service(name=name, control_file=control_file,
                           required_keys=required_keys, acceptable_keys=acceptable_keys)
    es.execute()
    for k in comment_keys:
        root_key = es.keys[k].root_key
        key_default = KEY_DB[root_key].value_default
        if key_default is None:
            assert es.keys[k].value is None
        else:
            assert es.keys[k].value == key_default