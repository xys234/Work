from tasks.config import ConfigureExecution
from tasks.initialize import InitializeEnvironment


def main(base, scen, mode, local):

    # Step 1
    task_configure_execution = ConfigureExecution(baseline, scenario, execution_mode)
    task_configure_execution.execute()


    # Step 2
    task_initialize_environment = InitializeEnvironment()
    task_initialize_environment.execute(task_configure_execution)

    if local:
        # local network


if __name__ == '__main__':
    from sys import argv
    baseline, scenario, execution_mode, local_network = argv[1], argv[2], argv[3], argv[4]
    # baseline, scenario, execution_mode = "S01_Base", "S01_Quick", "FULL"
    main(baseline, scenario, execution_mode, local_network)


