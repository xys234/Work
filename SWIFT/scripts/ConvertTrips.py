

from services.execution_service import Execution_Service


class ConvertTrips(Execution_Service):
    def __init__(self, name='ConvertTrips', required_keys=None):
        super().__init__(name, required_keys)

        self.required_keys = (
            'TRIP_TABLE_FILE'
            'MATRIX_NAME',
            'TIME_PERIOD_RANGE',
            'DIURNAL_FILE',
            ''
        )

