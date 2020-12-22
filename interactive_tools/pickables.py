from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, Point3d

from interactive_tools.event_managers import DragDropEventManager

class PickablePointDragger(DragDropEventManager):
    """ a dragger object gets assigned a pickable object, and
    dragger objects are managed by DragAndDropObjetsManager.
    it bundles the relevant information about a drag's state """
    def __init__(self, pickablepoint, camera):
        self.pickablepoint = pickablepoint
        self.camera = camera

        # FIXME: figure out a better way than passing the nodePath in here
        self._dragger_nodePath_handle = pickablepoint.nodePath  # this should only be used after the picking event and when the draggers are searched for the nodepath that was picked

        self.position_before_dragging = None

        self.add_on_state_change_function(self.update)

        DragDropEventManager.__init__(self, *args)

    def get_nodepath_handle_for_dragger(self):
        return self._dragger_nodePath_handle

    def init_dragging(self):
        """ save original position """

        r0_obj = math_utils.p3d_to_np(self.pickablepoint.getPos())

        self.position_before_dragging = Vec3(*r0_obj)

        DragDropEventManager.init_dragging(self)

    def update(self):
        """ """
        # print("counter: ", self.counter)
        # self.counter += 1
        r0_obj = math_utils.p3d_to_np(self.pickablepoint.getPos())

        v_cam_forward = math_utils.p3d_to_np(render.getRelativeVector(self.camera, self.camera.node().getLens().getViewVector()))
        v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
        # self.camera.node().getLens().getViewVector()

        v_cam_up = math_utils.p3d_to_np(render.getRelativeVector(self.camera, self.camera.node().getLens().getUpVector()))
        v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

        r_cam = math_utils.p3d_to_np(self.camera.getPos())

        e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

        e_cross = math_utils.p3d_to_np(np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

        # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
        r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

        print("r0_obj", r0_obj)
        print("v_cam_forward", v_cam_forward)
        print("v_cam_up", v_cam_up)
        print("r_cam", r_cam)
        print("e_up", e_up)
        print("e_cross", e_cross)
        print("r0_middle_origin", r0_middle_origin)

        # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y

        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        # print("p_xy_offset: ", self.p_xy_offset)

        p_x, p_y = conventions.getFilmSizeCoordinates(mouse_pos[0], mouse_pos[1], self.p_xy_offset[0], self.p_xy_offset[1])
        # p_x, p_y = conventions.getFilmSizeCoordinates(mouse_pos[0], mouse_pos[1], 0., 0.)

        drag_vec = p_x * e_cross + p_y * e_up

        # print("drag_vec", drag_vec)

        # set the position while dragging
        self.this_frame_drag_pos = self.position_before_dragging + Vec3(*drag_vec)
        self.pickablepoint.setPos(self.this_frame_drag_pos)

        if self.last_frame_drag_pos is None:
            self.state_changed = True
        elif self.last_frame_drag_pos == self.this_frame_drag_pos:
            self.state_changed = False  # TODO: in the future, a state change on drag will probably not only be the position
        else:
            self.state_changed = True

        # update the state between frames
        self.last_frame_drag_pos = self.this_frame_drag_pos


    def end_dragging(self):
        self.position_before_dragging = None

        DragDropEventManager.end_dragging(self)

class PickablePoint(Point3d):
    """ a flat point (2d box) parented by render """
    def __init__(self, pickableObjectManager, **kwargs):
        Point3d.__init__(self, **kwargs)

        self.nodePath.setColor(1., 0., 0., 1.)
        pickableObjectManager.tag(self.nodePath)