from tasks.task_status import TaskStatus


class Task(object):

    def __init__(self, previous_steps=None, step_id='00'):
        self.state = TaskStatus.OK
        self.previous_steps = previous_steps

        if not self.family:
            self.family = "Task"
        self.step_id = step_id

    def __str__(self):
        return '_'.join((self.family, self.step_id, self.__class__.__name__))

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