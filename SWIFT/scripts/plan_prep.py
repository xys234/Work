import time

from services.sys_defs import *
from services.execution_service import Execution_Service


class PlanPrep(Execution_Service):
    required_keys = (
        'TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FILE',
        'TRIP_FACTOR_FILE'
    )

    acceptable_keys = (
        'TRIP_PURPOSE_FIELD',
    )

    def __init__(self, name='PlanPrep', control_file='PlanPrep.ctl'):
        super().__init__(name, control_file, PlanPrep.required_keys, PlanPrep.acceptable_keys)

        self.input_trajectory_file = None
        self.trajectory_file = None
        self.trip_purpose_field = None
        self.trip_map = None
        self.trip_count = 0