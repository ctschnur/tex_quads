from direct.showbase.ShowBase import ShowBase, DirectObject

class EdgePlayerGraphicsStateMachine:
    """ describes just the state of the graphics.
        after requesting play, it could be that there needs to be some setup/loading period for
        the graphics, as well as for the Audio.
        The object of this class is accessed and modified by 2 'threads' simultaneously:
        - the main rendering thread (and in the future a graphics calculation thread)
          loading and updating the graphics (may be delayed due to solving dynamics of the graphics layout)
        - the task-'thread' overseeing the requests to play/pause/... will
          - send the requests to setup the resources (audio loading/graphics calculations) to the Playbacker / GraphicsCalculator
          - receive back 'ready' messages from the thread ((build up a queue of done functions and actions to perform when done, then continually check the first element of that queue))
          then launch the actions corresponding to the last global change (EdgePlayerState) all at once
        """

    def __init__(self):
        """ """
        pass


class EdgePlayerStateMachine(StateMachine):
    """ """
    def stopped_at_beginning(self):
        """ """
        # establish the state -> i.e. set
        playbacker.stop_at_beginning()
        graphicker.stop_at_beginning()


        # establish the transitions the resulting state of which
        # is dependent on the state
        self.on_event("space", self., next_state_args=())

    def playing_at_beginning(self):
        """ """
        pass
