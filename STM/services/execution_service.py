import random

from services.control_service import ControlService


class ExecutionService(ControlService):

    OUTPUT_BUFFER = 20_000_000
    INPUT_BUFFER = 10_000_000

    def __init__(self, name=None, control_file=None, required_keys=tuple(), optional_keys=tuple()):
        super().__init__(name, control_file)

        self.required_keys = required_keys
        self.optional_keys = optional_keys
        self.control_file = control_file
        self.seed = None

    def execute(self):
        super().execute()
        self.seed = self.keys['RANDOM_SEED'].value


