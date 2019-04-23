from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os
import subprocess


class ConvertTrips(Task):

    family = 'DynusT'
    step_id = '02'

    def __init__(self, previous_steps):
        super().__init__(previous_steps=previous_steps)

    def require(self):
        pass

    def run(self):
        pass

    def complete(self):
        pass

    def execute(self):
        pass
