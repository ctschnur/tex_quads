from direct.showbase.ShowBase import ShowBase, DirectObject
from direct.interval.IntervalGlobal import Wait, Sequence, Func

class Event:
    """ """

    def __init__(self):
        """ """
        pass


class WaitEvent:
    """ """

    def __init__(self, delay_in_seconds, func_at_end=lambda *args: None, func_at_end_args=()):
        """ """
        self.p3d_sequence = None
        self.delay = delay_in_seconds
        self.func_at_end = func_at_end
        self.func_at_end_args = func_at_end_args
        self.p3d_sequence = Sequence(Wait(delay_in_seconds),
                                     Func(self.func_at_end, *func_at_end_args))

    def add(self):
        """ """
        self.p3d_sequence.start()

    def remove(self):
        """ remove the event from being checked
            and thus the end function from being executed """
        if self.p3d_sequence:
            self.p3d_sequence.pause()  # removes it from the interval manager

        self.p3d_sequence = None  # remove the reference


class PandaEvent:
    """ base class only """

    def __init__(self, event_str, event_func, directobject):
        """ """
        self.event_str = event_str
        self.event_func = event_func
        self.directobject = directobject
        pass

    # def add(self):
    #     """ """
    #     self.directobject.accept(self.event_str, self.event_func)

    def remove(self):
        """ """
        self.directobject.ignore(self.event_str)


class PandaEventMultipleTimes(PandaEvent):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        PandaEvent.__init__(self, *args, **kwargs)

    def add(self):
        """ """
        self.directobject.accept(self.event_str, self.event_func)


class PandaEventOnce(PandaEvent):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        PandaEvent.__init__(self, *args, **kwargs)

    def add(self):
        """ """
        self.directobject.acceptOnce(self.event_str, self.event_func)


class BoolEvent:
    """ a task is registered and querys a testing function for a bool value.
        once the testing function returns True, the func_at_do_now is executed
        and the task is removed """

    def __init__(self, pfunc, taskmgr, pfunc_register_args_now=(),
                 func_at_do_now=lambda *args: None, func_at_do_now_args=()):
        """
        Args:
            pfunc: testing function (loading sth in another
                   thread for example) """
        self.pfunc_effective = (
            lambda args=pfunc_register_args_now: pfunc(*args))
        self.taskmgr = taskmgr
        self.taskobj = None

        self.func_at_do_now = func_at_do_now
        self.func_at_do_now_args = func_at_do_now_args

    def add(self):
        """ """
        self.taskobj = self.taskmgr.add(
            self._task
            # uponDeath: func is called even if it's removed and not just if it's 'task.done'
        )

    def taskDoneAndExecuteAndRemove(self, *args):
        """ """
        self.func_at_do_now(*self.func_at_do_now_args)
        self.remove(call_p3d_internal_remove=False)

    def remove(self, call_p3d_internal_remove=True):
        """ """
        if call_p3d_internal_remove == True:
            all_tasks = self.taskmgr.getAllTasks()
            for task in all_tasks:
                # assert type(task) == type(self.taskobj)
                if task == self.taskobj:
                    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                    self.taskmgr.remove(self.taskobj)

    def _task(self, task, *extraArgs):
        """ """
        res = self.pfunc_effective()
        if res == True:
            # this task is removed from within this function, so that it's return
            self.taskDoneAndExecuteAndRemove()
            return task.done        # does this return value matter ?

        return task.cont
