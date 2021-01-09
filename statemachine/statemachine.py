from direct.showbase.ShowBase import ShowBase, DirectObject

from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel

import time

import threading

import numpy as np

import collections

from interactive_tools.events import Event, WaitEvent, PandaEvent, PandaEventMultipleTimes, PandaEventOnce, BoolEvent




def equal_states(obj1, obj2):
    """ compares e.g. a bound method (of an instance) (a 'state' of a SM)
        to a function """
    return obj1.__qualname__ == obj2.__qualname__

class StateMachineCallOrEventBundle:
    """ Actions are followed by events occuring or just by transition_into calls
        which are steered by a particular state machine (internal or external).
        Alongside an event or a transition_into call, a sm should be bundled, from which
        that event or transition_into call is triggered """

    def __init__(self, called_from_sm=None):
        """
        Args:
            controlling_sm: state machine which is controlling the call """
        self.called_from_sm = called_from_sm
        pass


class StateMachineTransitionIntoCallBundle(StateMachineCallOrEventBundle):
    """ A StateMachineCallOrEventBundle for transition_into calls """
    def __init__(self, transition_into_call, *args, **kwargs):
        """
        Args:
            transition_into_call: a TransitionIntoCall instance """
        StateMachineCallOrEventBundle.__init__(self, *args, **kwargs)
        self.transition_into_call = transition_into_call
        self.ran = False
        pass

    def run(self):
        """ """
        self.transition_into_call.run()
        self.ran = True


class TransitionIntoCall:
    """ """
    def __init__(self, next_state, next_state_args=(), next_state_kwargs=dict()):
        """ """
        self.next_state = next_state
        self.next_state_args = next_state_args
        self.next_state_kwargs = next_state_kwargs

    def run(self):
        """ """
        self.next_state(*self.next_state_args, **self.next_state_kwargs)

    def __repr__(self):
        """ """
        return self.next_state.__name__

class SMBatchEvents:
    """ """

    def __init__(self, state_list, event_lambdas_list):
        """
        Args:
            state_list : a list of states for which the events should be registered
                         in the same way
            event_lambdas_list : calls to the events
        """
        self.state_list = state_list
        self.event_lambdas_list = event_lambdas_list

    def register_batch_events(self, in_state):
        """ """
        for state in self.state_list:
            if equal_states(in_state, state):
                for func in self.event_lambdas_list:
                    func()

class StateMachine:
    """ """

    def __init__(self, taskmgr, directobject=None, internal_name="main_loop",
                 initial_state=None, initial_state_args=(),
                 controlling_sm=None):
        """
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

        self._last_transition_into_call = None

        self.t0 = time.time()

        self.events = []

        self._batch_events_list = []

        self.transition_into_calls_history_queue_length = 5
        self.transition_into_calls_history_queue = collections.deque([None] * self.transition_into_calls_history_queue_length,
                                                                     self.transition_into_calls_history_queue_length)


        initial_state_args = ()
        if initial_state is None:
            initial_state = self._idle


        initial_controlling_sm = self
        self.set_controlling_state_machine(initial_controlling_sm)
        self.transition_into(initial_state, next_state_args=initial_state_args)

        if controlling_sm is None:
           controlling_sm = initial_controlling_sm

        self._controlling_sm = None
        self.set_controlling_state_machine(controlling_sm)


    def set_controlling_state_machine(self, controlling_sm):
        """
        Args:
            controlling_sm: the state machine the transitions and events of
            which are being executed. This can be an external state machine. By default
            it is self. """

        self._controlling_sm = controlling_sm

    def get_controlling_state_machine(self):
        """ """
        return self._controlling_sm

    def add_batch_events_for_setup(self, batch_events):
        """ adds them to the list of batch events to be registered every time
            transition_into is called. It doesn't regsiter or unregister the events
            on it's own
        Args:
            batch_events: an instance of SMBatchEvents
        """
        self._batch_events_list.append(batch_events)

    def remove_batch_events_for_setup(self, batch_events):
        """ removes them from the list of batch events to be registered every time
            transition_into is called. It doesn't regsiter or unregister the events
            on it's own.
        Args:
            batch_events: an instance of SMBatchEvents
        """
        self._batch_events_list.remove(batch_events)

    def remove_all_batch_events_for_setup(self):
        """ removes all batch_events from the list of batch events to be
            registered every time
            transition_into is called. It doesn't regsiter or unregister the events
            on it's own.
         """
        self._batch_events_list = []

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

    def add_event(self, event, called_from_sm=None):
        """ """
        if called_from_sm is None: # if you want to control a subordinate sm, you always have to specify the called_from_sm parameter
            called_from_sm = self

        if called_from_sm is self.get_controlling_state_machine():
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
            return task.done

        # print(("outside state: \tsolver.t = {0:.2f} " +
        #        "conversion = {1:.2f} ").format(
        #     solver.t, X),
        #     tc_method_string,
        #     end='\r')

        # print(self.internal_name, ": t : ", time.time() - self.t0, end='\r')
        return task.cont

    def last_state_function_ran_p(self, last_state_function):
        """ """
        return self.transition_into_calls_history_queue[0].transition_into_call.next_state is last_state_function and self.transition_into_calls_history_queue[0].ran == True

    def transition_into(self, next_state, next_state_args=(), next_state_kwargs=dict(), called_from_sm=None):
        """ """

        transition_into_call = TransitionIntoCall(next_state,
                                                  next_state_args=next_state_args,
                                                  next_state_kwargs=next_state_kwargs)

        state_machine_transition_into_call_bundle = (
            StateMachineTransitionIntoCallBundle(transition_into_call,
                                                 self.get_controlling_state_machine())
        )

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

        if called_from_sm is None:
            called_from_sm = self

        if called_from_sm is self.get_controlling_state_machine():
            self.transition_into_calls_history_queue.appendleft(state_machine_transition_into_call_bundle)

            self._last_transition_into_call = transition_into_call  # this does not mean that the state was entered correctly!
            state_machine_transition_into_call_bundle.run()


            # TODO: add the controlling state machine to the event bundles and to the events
            # apply batch events in the order in which they are stored in the lists
            for batch_events in self._batch_events_list:
                batch_events.register_batch_events(next_state)

            self.finished_running_transition_into = state_machine_transition_into_call_bundle

            print("transition DID run --------- ", transition_into_call,
                  "self: ", self.__class__.__qualname__,
                  "; called_from_sm: ", called_from_sm.__class__.__qualname__,
                  "; self.get_controlling_state_machine() : ", self.get_controlling_state_machine().__class__.__qualname__)
        else:
            print("transition NOT run --------- ", transition_into_call,
                  "self: ", self.__class__.__qualname__,
                  "; called_from_sm: ", called_from_sm.__class__.__qualname__,
                  "; self.get_controlling_state_machine() : ", self.get_controlling_state_machine().__class__.__qualname__)


    def _idle(self, *opt_args):
        """ state of doing nothing, waiting for transition_into commands """
        pass

    def get_current_state(self):
        """ the current state is actually the last assigned state """
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        if self._last_transition_into_call is not None:
            return self._last_transition_into_call.next_state
        else:
            print("err: self._last_transition_into_call : ",
                  self._last_transition_into_call)
            exit(1)

    def on_key_event_once(self, event_str, next_state, next_state_args=(),
                          called_from_sm=None):
        """ """
        self.add_event(
            PandaEventOnce(
                event_str,
                lambda next_state=next_state, args=next_state_args: (
                    self.transition_into(
                        next_state,
                        next_state_args=next_state_args)),
                self.directobject),
            called_from_sm=called_from_sm)

    def on_key_event_func(self, event_str, func, func_args=(), func_kwargs=dict(),
                          called_from_sm=None):
        """
        this doesn't necessarily transition into a 'next state',
        but just runs an arbitrary function whenever a key is pressed.
        Then, after the SM transitions into a new state, the event
        is cleaned up.
        """
        self.add_event(
            PandaEventMultipleTimes(
                event_str,
                lambda func=func, args=func_args, kwargs=func_kwargs: func(
                    *args, **kwargs),
                self.directobject),
            called_from_sm=called_from_sm)

    def on_escape(self, *opt_args):
        """ """
        print("on_escape: ")
        print("self._last_transition_into_call : \n",
              self._last_transition_into_call)
        # go to an empty state (i.e. unregister all events, ...)
        self.transition_into(lambda *opt_args: None)

        self.quit_main_loop()

    def on_wait_event(self, seconds, next_state, next_state_args=(),
                      called_from_sm=None):
        """ """
        self.add_event(
            WaitEvent(seconds,
                      func_at_end=(
                          lambda next_state=next_state, args=next_state_args: (
                              self.transition_into(
                                  next_state,
                                  next_state_args=args))
                      )),
            called_from_sm=called_from_sm)

    def on_bool_event(self,
                      pfunc,
                      next_state,
                      pfunc_register_args_now=(),
                      next_state_args=(),
                      called_from_sm=None):
        """ """
        self.add_event(
            BoolEvent(pfunc,
                      self.taskmgr,
                      pfunc_register_args_now=pfunc_register_args_now,
                      func_at_do_now=(
                          lambda next_state=next_state, args=next_state_args: (
                              self.transition_into(
                                  next_state,
                                  next_state_args=args))
                          )),
        called_from_sm=called_from_sm)

# TODO: check if controlling_state_machines work

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

    def __init__(self, wave_file_path, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        self.dobj = base

        from playback.playback import PlaybackerSM
        from plot_utils.graphickersm import GraphickerSM

        from playback.audiofunctions import get_wave_file_duration

        self.durat = get_wave_file_duration(wave_file_path)

        self.pbsm = PlaybackerSM(wave_file_path, taskMgr, directobject=base,
                                 controlling_sm=self)
        # self.pbsm.transition_into(self.pbsm.state_load_wav)

        self.gcsm = GraphickerSM(self.durat, taskMgr, directobject=base,
                                 controlling_sm=self)

        # self.gcsm.transition_into(self.gcsm.state_load_graphics)

        # self.transition_into(self.state_load)

    def state_load(self, *opt_args):
        """ """
        self.pbsm.transition_into(self.pbsm.state_load_wav, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_load_graphics, called_from_sm=self)
        print("###: ", self.gcsm.get_current_state())

        self.on_bool_event(
            lambda: (
                not self.pbsm.load_thread.is_alive()), self.state_stopped_at_beginning)

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        self.pbsm.transition_into(self.pbsm.state_stopped_at_beginning, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_stopped_at_beginning, called_from_sm=self)

        self.on_key_event_once("space", self.state_play)

    def state_play(self, change_time_to=None):
        """ """
        self.pbsm.transition_into(self.pbsm.state_play, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_play, called_from_sm=self)

        self.on_key_event_once("space", self.state_pause)


    def state_pause(self, change_time_to=None):
        """ """
        self.pbsm.transition_into(self.pbsm.state_pause, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_pause, called_from_sm=self)

        self.on_key_event_once("space", self.state_play)


    # def play(self, fooplayer):
    #     """ """
    #     self.on_bool_event(lambda: equal_states(
    #         fooplayer.get_current_state(), FooPlayer.ended), ended)
    #     pass
