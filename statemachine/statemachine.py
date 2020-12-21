from direct.showbase.ShowBase import ShowBase, DirectObject

import time


class StateMachine:
    """ """
    def __init__(self, taskmgr, directobject=None, internal_name="main_loop"):
        """ the async_func is the function that represents the main loop of the
            state machine, e.g. a panda3d task, or a function that is called in
            a while loop in a thread
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

        self.last_assigned_state_with_args = None

        self.t0 = time.time()

        self.panda_events = []  # tuples (event_str, event_func)

    def quit_main_loop(self):
        """ """
        if self.main_loop_running == True:
            self._quit_loop = True
        else:
            print("WARNING: quit_main_loop: self.main_loop_running ==",
                  self.main_loop_running)

    def launch_main_loop(self, initial_state, initial_state_args=()):
        """ the main loop runs for now in the graphics thread """
        if self.main_loop_running == False:
            self.taskmgr.add(self.main_loop_task, self.internal_name)
            self.main_loop_running = True
        else:
            print("WARNING: launch_main_loop: self.main_loop_running ==",
                  self.main_loop_running)


    def main_loop_task(self, task):
        """ """
        if self._quit_loop == True:
            self.quit_main_loop()
            return task.done

        # print(("outside state: \tsolver.t = {0:.2f} " +
        #        "conversion = {1:.2f} ").format(
        #     solver.t, X),
        #     tc_method_string,
        #     end='\r')

        print(self.internal_name, ": t : ", time.time() - self.t0, end='\r')
        return task.cont

    def transition_into(self, next_state, next_state_args=()):
        """ """
        # destroy events from potential last state
        for i, (c_event_str, c_event_func) in enumerate(self.panda_events):
            self.directobject.ignore(c_event_str)

        # start the new state
        if self.main_loop_running == False:
            self.launch_main_loop(next_state, initial_state_args=next_state_args)

        print("\r", flush=True)
        print("entering state: ", next_state.__name__,
              "\twith arguments: ", next_state_args)
        next_state(self, *next_state_args)
        self.last_assigned_state_with_args = (next_state, next_state_args)


    def on_panda_event(self, event_str, next_state, next_state_args=()):
        """ """
        self.add_panda_event_current_state(
            event_str,
            lambda next_state=next_state, args=next_state_args: (
                self.transition_into(next_state, next_state_args=next_state_args)))

    def on_escape(self, *opt_args):
        """ """
        print("on_escape: ")
        print("self.last_assigned_state_with_args : \n", self.last_assigned_state_with_args)
        self.quit_main_loop()

    def add_panda_event_current_state(self, event_str, event_func):
        """ """
        self.directobject.acceptOnce(event_str, event_func)
        self.panda_events.append((event_str, event_func))

    def ignore_panda_event_current_state(self, event_str):
        """ """
        ignored = False
        for i, (c_event_str, c_event_func) in enumerate(self.panda_events):
            if c_event_str == event_str:
                self.panda_events[i] = None
                self.directobject.ignore(event_str)
                ignored = True

        if ignored == False:
            print("Warning: event", event_str, "was not ignored")

        self.panda_events = list(filter(lambda el: el != None, self.panda_events))


class ExampleStateMachine(StateMachine):
    """ """
    def __init__(self, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)


    def state1(self, *opt_args):
        """ """
        # register events to go to state 2
        self.transition_into(self.state2)

    def state2(self, *opt_args):
        """ """
        self.on_panda_event("t", self.state3)
        self.on_panda_event("z", self.state4)

        # register events to go back to state 1

    def state3(self, *opt_args):
        """ """
        pass

    def state4(self, *opt_args):
        """ """
        pass
