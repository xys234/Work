from services.report_service import ReportService
from services.control_service import State

import os
import sys


class CheckLocalNetwork(object):

    REQUIRED_NETWORK_FILES =(
        'system.dat',
        'movement.dat',
        'superzone.dat',
        'TAZ_mapping.dat',
    )

    def __init__(self, step_number=2):

        self.state = State.OK
        self.step_number = step_number
        self.logger = None

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.base_dir = None
        self.scen_dir = None