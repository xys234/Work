import pytest
import os
import re
import sys

from plan_prep import PlanPrep


@pytest.fixture
def planprep_instance():
    """Returns a PlanPrep instance"""
    execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
    control_file = "PlanPrep_Test_Trajectory_Index.ctl"
    control_file = os.path.join(execution_path, control_file)
    exe = PlanPrep(control_file=control_file)
    super(PlanPrep, exe).execute()
    exe.update_keys()
    exe.initialize_internal_data()
    return exe


# @pytest.mark.skip(reason="passed")
def test_build_vehicle_trajectory_index(planprep_instance):
    vehicle_trajectory_text = r"C:\Projects\SWIFT\SWIFT_Project_Data\Outputs\VehTrajectory_Converted.txt"
    number_of_tests = -1

    veh_trajectory_index_text = planprep_instance.build_vehicle_trajectories_index_text(vehicle_trajectory_text)
    planprep_instance.build_vehicle_trajectories_index()
    assert len(planprep_instance.vehicle_trajectory_index) == len(veh_trajectory_index_text)
    test_cases_run = 0

    with open(vehicle_trajectory_text, mode='r') as input_trajectories_text:
        with open(planprep_instance.input_trajectory_file, mode='rb') as input_trajectories_binary:
            for vid, (pos, record_length, _) in veh_trajectory_index_text.items():

                input_trajectories_text.seek(pos)
                record = input_trajectories_text.read(record_length)
                data_text = planprep_instance.parse_record(record, binary=False)

                pos, record_length, _ = planprep_instance.vehicle_trajectory_index[vid]
                input_trajectories_binary.seek(pos)
                record = input_trajectories_binary.read(record_length)
                data_binary = planprep_instance.parse_record(record, binary=True)

                assert data_text[1] == data_binary[1]                       # tag
                assert data_text[2] == data_binary[2]                       # number of nodes
                assert data_text[3] == pytest.approx(data_binary[3], abs=0.1)        # toll

                assert data_text[5] == pytest.approx(data_binary[5])        # node sequence
                assert data_text[6] == pytest.approx(data_binary[6])
                assert data_text[7] == pytest.approx(data_binary[7])
                assert data_text[8] == pytest.approx(data_binary[8])

                if data_binary[9] and data_text[9]:
                    assert data_text[9] == pytest.approx(data_binary[9], abs=0.1)

                test_cases_run += 1
                sys.stdout.write("\rNumber of Cases Passed = {:,d}".format(test_cases_run))
                if test_cases_run == number_of_tests > 0:
                    break


# todo 12/20/2018: create a small trip file, trajectory file, and several adjustment instructions; PlanSelect
def create_test_files(vehicle_selection_file, vehicle_roster_file, vehicle_trajectory_file_binary,
                      new_vehicle_roster_file, new_vehicle_trajectory_file_binary):
    """
    Create a subset of roster, trajectory based on a subset of vehicle IDs
    :param vehicle_roster_file:
    :param vehicle_trajectory_file_binary:
    :return:
    """


