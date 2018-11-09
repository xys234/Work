

from services.execution_service import Execution_Service


class ConvertTrips(Execution_Service):
    def __init__(self, name='ConvertTrips'):
        super().__init__(name)

        self.required_keys = (
            'TRIP_TABLE_FILE'
            'MATRIX_NAME',
            'TIME_PERIOD_RANGE',
            'DIURNAL_FILE',
            'TRIP_PURPOSE_CODE',
            'VALUE_OF_TIME',
            'VEHICLE_OCCUPANCY'
        )

        self.acceptable_keys = (
            'TITLE', 'REPORT_FILE', 'PROJECT_DIRECTORY',
            'VEHICLE_CLASS',
            'VEHICLE_TYPE',
            'VEHICLE_GENERATION_MODE',
            'INDIFFERENCE_BAND',
            'NUMBER_OF_STOPS',
            'ENROUTE_INFO',
            'COMPLIANCE_RATE',
            'EVACUATION_FLAG',
            'ACTIVITY_DURATION',
            'ARRIVAL_TIME',
            'WAIT_TIME',
            'INITIAL_GAS'
        )


if __name__ == '__main__':
    import os

    execution_path = "C:\Projects\Repo\Work\SWIFT\data"
    control_file = "ConvertTrips.ctl"
    control_file = os.path.join(execution_path, control_file)

    exe = ConvertTrips()
    exe.execute(control_file)
