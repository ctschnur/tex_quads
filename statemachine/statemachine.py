from direct.showbase.ShowBase import ShowBase, DirectObject

from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel

import time

import threading

import numpy as np


def equal_states(obj1, obj2):
    """ compares e.g. a bound method (of an instance) (a 'state' of a SM)
        to a function """
    return obj1.__qualname__ == obj2.__qualname__


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
    """ """

    def __init__(self, event_str, event_func, directobject):
        """ """
        self.event_str = event_str
        self.event_func = event_func
        self.directobject = directobject
        pass

    def add(self):
        """ """
        self.directobject.acceptOnce(self.event_str, self.event_func)

    def remove(self):
        """ """
        self.directobject.ignore(self.event_str)


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


class StateMachine:
    """ """

    def __init__(self, taskmgr, directobject=None, internal_name="main_loop", initial_state=None, initial_state_args=()):
        """ the async_func is the function that represents the main loop of the
            state machine, e.g. a panda3d task, or a function that is called in
            a while loop in a thread.

            Args:
                initial_state: SM's loop is started right away, with initial_state
        """

        # -- registering events
        if directobject is None:
            directobject = base

        self.directobject = directobject
        self.directobject.accept("escape", self.on_escape)

        self.taskmgr = taskmgr
        self.main_loop_running = False
        self._quit_loop = False

        self.internal_name = internal_name

        self._last_assigned_state_with_args = None

        self.t0 = time.time()

        self.events = []

        if initial_state is not None:
            self.transition_into(
                initial_state, next_state_args=initial_state_args)
        else:
            self.transition_into(self._idle)

    def quit_main_loop(self):
        """ i.e. die """
        if self.main_loop_running == True:
            self._quit_loop = True
            self.remove_all_events()
        else:
            print("WARNING: quit_main_loop: self.main_loop_running ==",
                  self.main_loop_running)

    def launch_main_loop(self):
        """ the main loop runs for now in the graphics thread """
        if self.main_loop_running == False:
            self.taskmgr.add(self.main_loop_task, self.internal_name)
            self.main_loop_running = True
        else:
            print("WARNING: launch_main_loop: self.main_loop_running ==",
                  self.main_loop_running)

    def add_event(self, event):
        """ """
        self.events.append(event)
        event.add()

    def remove_event(self, event):
        """ """
        self.events.remove(event)
        event.remove()

    def remove_all_events(self):
        """ """
        for event in self.events:
            self.remove_event(event)

    def main_loop_task(self, task):
        """ """
        if self._quit_loop == True:
            self.quit_main_loop()
            return task.doene

        # print(("outside state: \tsolver.t = {0:.2f} " +
        #        "conversion = {1:.2f} ").format(
        #     solver.t, X),
        #     tc_method_string,
        #     end='\r')

        # print(self.internal_name, ": t : ", time.time() - self.t0, end='\r')
        return task.cont

    def transition_into(self, next_state, next_state_args=()):
        """ """
        # destroy events from potential last state
        for i, event in enumerate(self.events):
            event.remove()

        # start the new state
        if self.main_loop_running == False:
            self.launch_main_loop()

        # print("\r", flush=True)
        if next_state.__name__ != "_idle":
            print(self.__class__.__name__, ": "
                  "\tentering state: ", next_state.__name__,
                  "\twith arguments: ", next_state_args)

        self._last_assigned_state_with_args = (next_state, next_state_args)
        next_state(*next_state_args)

    def _idle(self, *opt_args):
        """ state of doing nothing, waiting for transition_into commands """
        pass

    def get_current_state(self):
        """ the current state is actually the last assigned state """
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        if self._last_assigned_state_with_args is not None:
            return self._last_assigned_state_with_args[0]
        else:
            print("err: self._last_assigned_state_with_args : ",
                  self._last_assigned_state_with_args)
            exit(1)

    def on_key_event(self, event_str, next_state, next_state_args=()):
        """ """
        self.add_event(
            PandaEvent(
                event_str,
                lambda next_state=next_state, args=next_state_args: (
                    self.transition_into(
                        next_state,
                        next_state_args=next_state_args)),
                self.directobject))

    def on_escape(self, *opt_args):
        """ """
        print("on_escape: ")
        print("self._last_assigned_state_with_args : \n",
              self._last_assigned_state_with_args)
        # go to an empty state (i.e. unregister all events, ...)
        self.transition_into(lambda *opt_args: None)
        self.quit_main_loop()

    def on_wait_event(self, seconds, next_state, next_state_args=()):
        """ """
        self.add_event(
            WaitEvent(seconds,
                      func_at_end=(
                          lambda next_state=next_state, args=next_state_args: (
                              self.transition_into(
                                  next_state,
                                  next_state_args=args)))))

    def on_bool_event(self,
                      pfunc,
                      next_state,
                      pfunc_register_args_now=(),
                      next_state_args=()):
        """ """
        self.add_event(
            BoolEvent(pfunc,
                      self.taskmgr,
                      pfunc_register_args_now=pfunc_register_args_now,
                      func_at_do_now=(
                          lambda next_state=next_state, args=next_state_args: (
                              self.transition_into(
                                  next_state,
                                  next_state_args=args)))))


class FooPlayer(StateMachine):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

    def loading(self, *opt_args):
        """ """
        print("loading ...")
        time.sleep(2)
        print("loaded.")
        self.transition_into(self.loaded)

    def loaded(self, *opt_args):
        """ it just resides in here, until playing is pressed """
        # self.on_bool_event(lambda: equal_states(self.get_current_state(), FooPlayer.loaded), self.playing)
        pass

    def playing(self, *opt_args):
        """ """
        print("playing ...")
        time.sleep(2)
        print("played.")
        self.transition_into(self.ended)

    def ended(self, *opt_args):
        """ """
        print("done playing")
        pass


t0 = time.time()


def checking(a, b):
    """ """
    t = time.time()

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    if t0 + 2 < t:
        print("yes")
        print(a, b)
        return True
    else:
        # print("not yet")
        return False


class Foo:
    def __init__(self, val):
        self.val = val

    def __repr__(self):
        return str(self.val)


class EdgePlayerStateMachine(StateMachine):
    """ """

    def __init__(self, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        fooplayer = None

    def state1(self, *opt_args):
        """ """
        # register events to go to state 2
        # self.transition_into(self.state2)
        self.on_key_event("p", self.wait_for_loading)

        # a = ["a"]
        # b = ["b"]
        a = Foo(1)
        b = Foo(2)

        self.on_bool_event(  # lambda: equal_states(fooplayer.get_current_state(), FooPlayer.loaded)
            lambda: checking(a, b),
            self.state3,  # pfunc_register_args_now=(a, b)
        )

        a.val = 4
        # a = ["aa"]

        self.transition_into(self.statefoo, next_state_args=(a, b))

    def statefoo(self, a, b):
        """ """
        a.val = 5

    def state2(self, *opt_args):
        """ """
        self.on_key_event("t", self.state3)
        self.on_key_event("z", self.state4)
        # self.on_panda_event("t", self.state3)
        # self.on_panda_event("z", self.state4)
        self.on_wait_event(1, self.state4)
        # self.on_wait_event(3, self.state5)

        # register events to go back to state 1

    def state3(self, *opt_args):
        """ """
        pass

    def state4(self, *opt_args):
        """ """

        # as soon as func evaluates to True, go to state5
        # self.on_bool_event(func, self.state5, next_state_args=("myaudio.wav"))
        # self.on_key_event("p")
        pass

    def wait_for_loading(self, filename):
        """ """
        # start the audio loading/playing state machine in a new thread
        fooplayer = FooPlayer(self.taskmgr)

        playbacker_thread = threading.Thread(
            target=lambda: fooplayer.transition_into(fooplayer.loading), daemon=True)
        playbacker_thread.start()

        # the condition for carrying on to play it
        self.on_bool_event(lambda fooplayer: equal_states(fooplayer.get_current_state(), FooPlayer.loaded),
                           self.play, next_state_args=(fooplayer,), pfunc_register_args_now=(fooplayer,))

    def play(self, fooplayer):
        """ """
        # self.on_bool_event(lambda: equal_states(fooplayer.get_current_state(), FooPlayer.ended), ended)
        pass

    def ended(self, *opt_args):
        """ """
        pass
