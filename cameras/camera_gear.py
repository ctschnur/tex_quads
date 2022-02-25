class CameraGear:
    """ """
    def __init__(self, *args, **kwargs):
        """ """
        # --- hooks for camera movement
        self.camera_move_hooks = []  # store function objects

        # --- hooks for window resize
        self.window_resize_hooks = []  # store function objects
        pass

    def add_camera_move_hook(self, func):
        """ func is the function to run when the camera moves;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.camera_move_hooks.append(func)

    def remove_camera_move_hook(self, func):
        """ remove the hook """
        self.camera_move_hooks.remove(func)

    def run_camera_move_hooks(self):
        for c_hook in self.camera_move_hooks:
            # run the function
            c_hook()

    def add_window_resize_hook(self, func):
        """ func is the function to run when the window resizes;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.window_resize_hooks.append(func)

    def remove_window_resize_hook(self, func):
        """ remove the hook """
        self.window_resize_hooks.remove(func)

    def run_window_resize_hooks(self):
        for c_hook in self.window_resize_hooks:
            # run the function
            c_hook()
