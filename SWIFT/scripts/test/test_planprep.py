import pytest
import os

from plan_prep import PlanPrep

# TODO: Complete tests


@pytest.fixture
def planprep_instance():
    """Returns a PlanPrep instance"""
    execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
    control_file = "PlanPrep_Test_Trajectory_Index.ctl"
    control_file = os.path.join(execution_path, control_file)
    exe = PlanPrep(control_file=control_file)
    super(PlanPrep, exe).execute()
    exe.update_keys()
    exe.initialize_execution()
    return exe


# @pytest.mark.skip(reason="passed")
def test_build_vehicle_trajectory_index(planprep_instance):
    vehicle_trajectory_text = 0
    number_of_tests = 10

    planprep_instance.build_trip_index()
    with open(vehicle_trajectory_text, mode='r') as trajectory_text_file:
        pass
