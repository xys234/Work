import pytest
from services.execution_service import Execution_Service


# @pytest.mark.skip(reason="passed")
def test_comment_line():
    """
    test keys commented; should take default values
    :return:
    """

    name = 'ConvertTrips'
    control_file = r'cases\ConvertTrips_2.ctl'

    required_keys = ('TRIP_TABLE_FILE',)
    acceptable_keys = ('NUMBER_OF_STOPS', 'MATRIX_NAME', 'TIME_PERIOD_RANGE')

    es = Execution_Service(name=name, control_file=control_file,
                           required_keys=required_keys, acceptable_keys=acceptable_keys)

    cases = [
        # ("1,2", {1,2}),
        ("1,3", {1,3}),
        ("1..3", {1,2,3}),
        ("1..3,6", {1,2,3,6}),
        ("1..3, 7, 4..6", {1,2,3,4,5,6,7}),
    ]

    for case in cases:
        assert es.parse_range_key(case[0]) == case[1]