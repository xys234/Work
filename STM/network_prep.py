from services.execution_service import ExecutionService
from services.control_service import State
from services.file_service import *
from services.utility import Lookup

import sys
import time
import shutil
import os


class NetworkPrep(ExecutionService):
    required_keys = (
        'NETWORK_FILE',
        'NEW_NETWORK_FILE',
        'SCENARIO_PARAMETER_FILE',
        'CAPACITY_FACTOR_FILE',
        'TRAFFIC_FLOW_MODEL_FILE',
        'NEW_TRAFFIC_FLOW_MODEL_FILE',
    )

    acceptable_keys = (
        'AV_WEIGHT',
        'CV_WEIGHT',
    )

    file_keys = (
        'NETWORK_FILE',
        'NEW_NETWORK_FILE',
        'SCENARIO_PARAMETER_FILE',
        'CAPACITY_FACTOR_FILE',
        'TRAFFIC_FLOW_MODEL_FILE',
        'NEW_TRAFFIC_FLOW_MODEL_FILE',

    )

    CAPACITY_FACTOR_FILE_HEADER = ('CAV_PERCENTAGE', 'FREEWAY', 'ARTERIAL', 'ALPHA', 'BETA')
    FREEWAY_FT, ARTERIAL_FT = (1, 2, 3, 4, 7, 9, 10), (5, 6, 8)

    def __init__(self, name='NetworkPrep', input_control_file='NetworkPrep.ctl'):
        super().__init__(name, input_control_file, NetworkPrep.required_keys, NetworkPrep.acceptable_keys)

        self.network_file = None
        self.network_file_path = None
        self.new_network_file = None
        self.new_network_file_path = None
        self.capacity_factor_file_path = None
        self.traffic_flow_model_file = None
        self.traffic_flow_model_file_path = None
        self.new_traffic_flow_model_file_path = None
        self.scenario_parameters_file_path = None

        self.scenario_parameters = {}
        self.number_of_nodes = 0
        self.number_of_zones = 0
        self.number_of_links = 0
        self.av_percent = [0.0, 0.0, 0.0]
        self.cv_percent = 0
        self.cav_percent = 0.0
        self.lk_freeway_cap = None
        self.lk_arterial_cap = None
        self.lk_alpha = None
        self.lk_beta = None

        self.av_weight = [1.0, 1.0, 1.0]
        self.cv_weight = 1.0

    def initialize_internal_data(self):
        self.network_file_path = self.keys['NETWORK_FILE'].value
        self.new_network_file_path = self.keys['NEW_NETWORK_FILE'].value
        self.capacity_factor_file_path = self.keys['CAPACITY_FACTOR_FILE'].value
        self.traffic_flow_model_file_path = self.keys['TRAFFIC_FLOW_MODEL_FILE'].value
        self.new_traffic_flow_model_file_path = self.keys['NEW_TRAFFIC_FLOW_MODEL_FILE'].value
        self.scenario_parameters_file_path = self.keys['SCENARIO_PARAMETER_FILE'].value

        self.av_weight = self.keys['AV_WEIGHT'].value
        self.cv_weight = self.keys['CV_WEIGHT'].value

        # self.av_weight = [w / sum(self.av_weight) for w in self.av_weight]

    def read_network(self):
        self.network_file = File(name='Network')

        # Backup the existing network
        backup_network_file = os.path.join(os.path.dirname(self.network_file_path), 'network_Input.bak')
        if os.path.normcase(backup_network_file) != os.path.normcase(self.network_file_path):
            shutil.copy2(self.network_file_path, backup_network_file)

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
                    # sys.stdout.write("\n")

                elif number_of_nodes_read == self.number_of_nodes and number_of_links_read < self.number_of_links:
                    record = NetworkLinkRecord()
                    record.from_string(line)
                    self.network_file.append(record)
                    number_of_links_read += 1
                    sys.stdout.write("\rNumber of Link Records Read = {:,d}".format(number_of_links_read))

        sys.stdout.write("\n")
        self.logger.info("Number of Node-Zone Records Read = {:,d}".format(number_of_nodes_read))
        self.logger.info("Number of Link      Records Read = {:,d}".format(number_of_links_read))

    def modify_network(self):
        for record in self.network_file:
            if isinstance(record, NetworkLinkRecord):
                if record.ftype in self.FREEWAY_FT:
                    _, cap_factor = self.lk_freeway_cap.lookup(self.cav_percent, exact=False)
                else:
                    _, cap_factor = self.lk_arterial_cap.lookup(self.cav_percent, exact=False)

                record.service_rate = int(record.service_rate*cap_factor)

    def write_network(self):
        with open(self.new_network_file_path, mode='w', buffering=super().OUTPUT_BUFFER) as output_network:
            for record in self.network_file:
                output_network.write(record.to_string())

    def read_traffic_flow_models(self):
        self.traffic_flow_model_file = File(name='TrafficFlowModel')

        # Backup the existing traffic flow model
        backup_tfm_file = os.path.join(os.path.dirname(self.traffic_flow_model_file_path), 'TrafficFlowModel_Input.bak')
        if os.path.normcase(backup_tfm_file) != os.path.normcase(self.traffic_flow_model_file_path):
            shutil.copy2(self.traffic_flow_model_file_path, backup_tfm_file)

        with open(self.traffic_flow_model_file_path, mode='r', buffering=super().INPUT_BUFFER) as input_tfm:
            number_of_tfm = int(next(input_tfm).strip())

            number_of_tfm_read = 0
            while number_of_tfm_read < number_of_tfm:
                data = next(input_tfm).strip().split() + next(input_tfm).strip().split()
                record = TrafficFlowModelRecord()
                record.from_string(data)
                self.traffic_flow_model_file.append(record)
                number_of_tfm_read += 1
        self.logger.info("Number of Traffic Flow Models Read = {:,d}".format(number_of_tfm_read))

    def modify_traffic_flow_models(self):
        _, alpha_factor = self.lk_alpha.lookup(self.cav_percent, exact=False)
        # _, beta = self.lk_beta.lookup(self.cav_percent, exact=False)

        for record in self.traffic_flow_model_file:
            record.alpha = max(1.0, record.alpha * alpha_factor)
            # record.beta = beta

    def write_traffic_flow_models(self):
        number_of_tfm = len(self.traffic_flow_model_file)

        with open(self.new_traffic_flow_model_file_path, mode='w', buffering=super().OUTPUT_BUFFER) as output_tfm:
            output_tfm.write(str(number_of_tfm)+"\n")
            for record in self.traffic_flow_model_file:
                output_tfm.write(record.to_string())
        self.logger.info("Number of Traffic Flow Models Written = {:,d}".format(number_of_tfm))

    def read_capacity_factors(self):
        capacity_factors = []

        number_of_records = 0
        with open(self.capacity_factor_file_path, mode='r', buffering=super().INPUT_BUFFER) as input_cap:
            line = next(input_cap)
            header = line.strip().split(',')[:len(self.CAPACITY_FACTOR_FILE_HEADER)]
            header = tuple([f.upper() for f in header])
            if header != self.CAPACITY_FACTOR_FILE_HEADER:
                self.logger.error('Capacity factor file header error; Expect "%s" separated by commas' %
                                  " ".join(self.CAPACITY_FACTOR_FILE_HEADER))
                self.state = State.ERROR
            else:
                for line in input_cap:
                    number_of_records += 1
                    record = tuple([float(value) for value in line.strip().split(',')])
                    capacity_factors.append(record)
        self.logger.info("Number of Capacity Factor Records Read = {:,d}".format(number_of_records))

        # Create the lookup
        cav_percent = [record[0] for record in capacity_factors]
        freeway_factor = [record[1] for record in capacity_factors]
        arterial_factor = [record[2] for record in capacity_factors]
        alpha_factor = [record[3] for record in capacity_factors]
        beta_factor = [record[4] for record in capacity_factors]

        self.lk_freeway_cap = Lookup(cav_percent, freeway_factor, 'Freeway_Cap')
        self.lk_arterial_cap = Lookup(cav_percent, arterial_factor, 'Arterial_Cap')
        self.lk_alpha = Lookup(cav_percent, alpha_factor, 'Alpha')
        self.lk_beta = Lookup(cav_percent, beta_factor, 'Beta')

    def calculate_cav_percent(self):
        """
        Calculate the equivalent CAV percent
        :return:
        """

        av_percent = [w*p for w, p in zip(self.av_weight, self.av_percent)]
        return self.cv_weight*self.cv_percent*sum(av_percent)

    def read_scenario_parameter(self):
        with open(self.scenario_parameters_file_path, buffering=super().INPUT_BUFFER, mode='r') as input_parameter:
            for line in input_parameter:
                line = line.strip().split(',')
                if line[0].startswith('p_tech_cv_pct'):
                    self.cv_percent = float(line[1])
                    if self.cv_percent > 1.0:
                        self.cv_percent = self.cv_percent / 100.0
                elif line[0].startswith('p_tech_apv3_pct'):
                    self.av_percent[0] = float(line[1])
                    if self.av_percent[0] > 1.0:
                        self.av_percent[0] = self.av_percent[0] / 100.0
                elif line[0].startswith('p_tech_apv4_pct'):
                    self.av_percent[1] = float(line[1])
                    if self.av_percent[1] > 1.0:
                        self.av_percent[1] = self.av_percent[1] / 100.0
                elif line[0].startswith('p_tech_apv5_pct'):
                    self.av_percent[2] = float(line[1])
                    if self.av_percent[2] > 1.0:
                        self.av_percent[2] = self.av_percent[2] / 100.0
                else:
                    continue

        self.cav_percent = self.calculate_cav_percent()
        self.logger.info("CV Percent = {:.0f}%".format(self.cv_percent*100))
        self.logger.info("AV Percent (Level 3, 4, 5) = {:.0f}%, {:.0f}%, {:.0f}%".format(
            *[100*p for p in self.av_percent]))
        self.logger.info("Equivalent CAV Percent = {:.0f}%".format(self.cav_percent * 100))

    def execute(self):
        super().execute()
        start_time = time.time()

        if self.state == State.OK:
            self.initialize_internal_data()

        if self.state == State.OK:
            self.read_scenario_parameter()
            self.read_capacity_factors()

        if self.state == State.OK:
            self.read_network()
            self.modify_network()
            self.write_network()

        if self.state == State.OK:
            self.read_traffic_flow_models()
            self.modify_traffic_flow_models()
            self.write_traffic_flow_models()

        end_time = time.time()
        execution_time = (end_time - start_time) / 60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == State.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 0
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
