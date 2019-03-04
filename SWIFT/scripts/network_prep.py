from services.sys_defs import *
from services.execution_service import Execution_Service
from services.file_service import NetworkHeaderRecord, NetworkNodeZoneRecord, NetworkLinkRecord, File
import sys
import time


class NetworkPrep(Execution_Service):
    required_keys = (
        'NETWORK_FILE',
        'NEW_NETWORK_FILE',
        'SCENARIO_PARAMETER_FILE',
    )

    acceptable_keys = (
        'CAPACITY_FACTOR_FILE',
    )

    file_keys = (
        'NETWORK_FILE',
        'NEW_NETWORK_FILE',
        'SCENARIO_PARAMETER_FILE',
        'CAPACITY_FACTOR_FILE',

    )

    def __init__(self, name='NetworkPrep', input_control_file='NetworkPrep.ctl'):
        super().__init__(name, input_control_file, NetworkPrep.required_keys, NetworkPrep.acceptable_keys)

        self.network_file = None
        self.network_file_path = None
        self.new_network_file = None
        self.new_network_file_path = None
        self.capacity_factor_file_path = None

        self.scenario_parameters = {}
        self.number_of_nodes = 0
        self.number_of_zones = 0
        self.number_of_links = 0

    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        if self.project_dir is not None:
            for k in self.file_keys:
                if KEY_DB[k].group_type == Key_Group_Types.GROUP:
                    for g in range(1, self.highest_group+1):
                        if self.keys[k+"_"+str(g)].value:
                            self.keys[k+"_"+str(g)].value = \
                                os.path.join(self.project_dir, self.keys[k+"_"+str(g)].value)
                else:
                    if self.keys[k].value:
                        self.keys[k].value = os.path.join(self.project_dir, self.keys[k].value)

    def initialize_internal_data(self):
        self.network_file_path = self.keys['NETWORK_FILE'].value
        self.new_network_file_path = self.keys['NEW_NETWORK_FILE'].value
        self.capacity_factor_file_path = self.keys['CAPACITY_FACTOR_FILE'].value

    def read_network(self):
        self.network_file = File(name='Network_INPUT', file_path=self.network_file_path)

        with open(self.network_file_path, buffering=super().INPUT_BUFFER, mode='r') as input_network:
            data = next(input_network)
            record = NetworkHeaderRecord()
            record.from_string(data.strip().split())
            self.number_of_zones, self.number_of_links, self.number_of_nodes = \
                record.number_of_zones, record.number_of_links, record.number_of_nodes
            self.network_file.append(record)

            self.logger.info("Input Network File -- %d Nodes, %d Zones, %d Links" %
                             (self.number_of_nodes, self.number_of_zones, self.number_of_links))

            number_of_nodes_read, number_of_links_read = 0, 0
            for line in input_network:
                line = line.strip().split()
                if number_of_nodes_read < self.number_of_nodes:
                    record = NetworkNodeZoneRecord()
                    record.from_string(line)
                    self.network_file.append(record)
                    number_of_nodes_read += 1
                    sys.stdout.write("\rNumber of Node-Zone Records Read = {:,d}".format(number_of_nodes_read))

                elif number_of_nodes_read == self.number_of_nodes and number_of_links_read < self.number_of_links:
                    record = NetworkLinkRecord()
                    record.from_string(line)
                    self.network_file.append(record)
                    number_of_links_read += 1
                    sys.stdout.write("\rNumber of Link Records Read = {:,d}".format(number_of_links_read))
        sys.stdout.write("\n")

    def write_network(self):
        with open(self.new_network_file_path, mode='w', buffering=super().OUTPUT_BUFFER) as output_network:
            for record in self.network_file:
                output_network.write(record.to_string())

    def execute(self):
        super().execute()

        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.update_keys()
            self.print_keys()

        if self.state == Codes_Execution_Status.OK:
            self.initialize_internal_data()

        if self.state == Codes_Execution_Status.OK:
            self.read_network()
            self.write_network()

        end_time = time.time()
        execution_time = (end_time - start_time) / 60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 1
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        control_file = "NetPrep_UpdateNetwork.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = NetworkPrep(input_control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = NetworkPrep(input_control_file=argv[1])
        exe.execute()