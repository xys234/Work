from tasks.task_status import TaskStatus


class Task(object):

    def __init__(self, previous_steps=None):
        self.state = TaskStatus.OK
        self.previous_steps = previous_steps

        if not self.family:
            self.family = "Task"
        if not self.step_id:
            self.step_id = "00"

    def prepare(self):
        if self.previous_steps:
            for step in self.previous_steps:
                if step.state != TaskStatus.OK:
                    self.state = TaskStatus.UPSTREAM_FAIL
        return self.state

    def require(self):
        pass

    def run(self):
        pass

    def complete(self):
        pass

    def execute(self):
        pass