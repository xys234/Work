import pytest
import os

from plan_prep import PlanPrep

# TODO: Complete tests

def parse_trajectory_text_header(header, field):
    pos = header.find(field)


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
    vehicle_trajectory_text = 0
    number_of_tests = 10

    veh_count = 0
    veh_id_pos_index = {}
    with open(vehicle_trajectory_text, mode='r') as trajectory_text_file:
        pos = 0
        for line in trajectory_text_file:
            if line.startswith("Veh #"):
                items = line.strip().split()

                if veh_count == 0:
                    prev_pos = pos
                else:
                    offset = pos - prev_pos - (i - prev_line)
                    veh_id_pos_index[veh_id] = (prev_pos, offset)
                    prev_pos = pos
                prev_line = i
                veh_count += 1
                veh_id = int(line[:15].split()[2])
            else:
                pos += len(line)
            pos += len(line) + 1

    planprep_instance.build_vehicle_id_index()
    assert len(planprep_instance.vehicle_trajectory_index) == veh_count
    test_cases_run = 0
            assert 0 = 0