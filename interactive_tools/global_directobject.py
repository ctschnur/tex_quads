from direct.showbase.ShowBase import ShowBase, DirectObject

global_directobject = None  # this is the global direct object (replaces base), with a bit more functionality

class GlobalDirectObject(DirectObject.DirectObject):
    """ """
    def __init__(self):
        """ """
        DirectObject.DirectObject.__init__(self)

        self.accepted_events_strs = []


    def accept(self, *args, **kwargs):
        """ """

        # construct a function that before running the function first checks if there are other events with higher precedence already engaged currently

        DirectObject.DirectObject.accept(self, )

        self.accepted_events_strs = args[0]


    # def are_top_events_already_engaged(self):
    #     """ """
