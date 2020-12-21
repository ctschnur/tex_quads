from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel
from simple_objects import primitives
from local_utils import math_utils

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3

from cameras.Orbiter import Orbiter
from sequence.sequence import Sequence


def draw_nbody_system(self):
    shade_of_gray = 0.1
    base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

    ob = Orbiter(base.cam, radius=3.)
    # ob.set_view_to_xy_plane()
    # ob.set_view_to_xz_plane()

    cs = CoordinateSystem(ob)

    from plot_utils.nbodysystem.calc import get_pos_as_func_of_time

    animation_length_factor = 10.
    stop_time = 5. * animation_length_factor
    num_points = int(1000 * math.floor(animation_length_factor))

    # make all bodies white
    nbodies_color = (1., 1., 1., 1.)

    d = 3
    # two bodies: two points
    num_of_bodies = 5

    def get_radius_from_mass_3d_sphere(mass):
        """ assume incompressibility
        Args:
            mass: a positive number
        Returns: radius """
        rho = 1.
        return (3. * mass / (4. * rho * np.pi))**(1./3.)

    import plot_utils.colors.colors as colors

    ps = []  # graphics: points
    vs = []  # velocity vectors
    paths = []  # paths (tracing out movement)

    vis = []
    xis = []
    ms = []
    ncs = []
    cols = []

    for n in range(num_of_bodies):
        vi = np.array([0.2 * np.random.rand(),
                       0.2 * np.random.rand(),
                       0.2 * np.random.rand()]) * (-1.)**math.floor(np.random.rand()*10) * 0.4  # consistent with d=3
        xi = np.array([np.random.rand(),
                       np.random.rand(),
                       np.random.rand()]) * (-1.)**math.floor(np.random.rand()*10) * 0.65
        vis.append(vi)
        xis.append(xi)

        # resolved error: nan's in result when mi and nc are n-dependent ...
        mi = (1. + n) * 5
        ms.append(mi)

        nc = (-1.)**math.floor(np.random.rand()*10)
        ncs.append(nc)

        color = colors.get_next_mpl_color()
        cols.append(color)

        p = Point3d(scale=get_radius_from_mass_3d_sphere(mi))
        p.setColor(color)
        p.setPos(math_utils.np_to_p3d_Vec3(xi))
        ps.append(p)

        v = Vector()
        v.setColor(color)
        vs.append(v)

        paths.append(primitives.SegmentedLinePrimitive(color=Vec4(*color)))

    vis = [vi * 0.1 for vi in vis]

    def render_nbodysystem(a, tup, ps, vs, paths):
        """
        Args:
            a: param between 0 and 1 -> time
            tup: tuple returned from solution function (t, vels, poss)
            ps: list of graphical points """

        t = np.array(tup[0])
        vels = tup[1]
        poss = tup[2]

        duration = max(t)
        assert duration == stop_time

        # display one out of the discrete calculated positions, the closest one to the time in the sequence
        i_to_display = np.where(t <= a * duration)[0][-1]

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        for n in range(num_of_bodies):
            # cut the vector down/extend the vector to a 3d vector, since you can't plot more or less than 3d

            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            pos_of_particle_np = math_utils.get_3d_vec_from_nd_vec(
                poss[n][i_to_display])
            pos_of_particle = math_utils.np_to_p3d_Vec3(pos_of_particle_np)
            vel_of_particle_np = math_utils.get_3d_vec_from_nd_vec(
                vels[n][i_to_display])
            vel_of_particle = math_utils.np_to_p3d_Vec3(vel_of_particle_np)

            ps[n].setPos(pos_of_particle)

            # plot the velocity vectors
            vs[n].setTailPoint(pos_of_particle)

            vel_vector_to_plot = pos_of_particle + vel_of_particle

            if np.linalg.norm(vel_of_particle_np) >= 1:
                vel_vector_to_plot = math_utils.np_to_p3d_Vec3(
                    pos_of_particle_np +
                    math_utils.normalize(vel_of_particle_np) * np.log(np.linalg.norm(vel_of_particle_np)))

            vs[n].setTipPoint(vel_vector_to_plot)

            # trace out the paths over time
            paths[n].extendCoords([pos_of_particle_np])

        pass

    myseq = Sequence(duration=stop_time,
                     extraArgs=[
                         # the solution vector including the times
                         get_pos_as_func_of_time(
                             ms, ncs,
                             vis, xis,
                             stoptime=stop_time, numpoints=num_points,
                             d=d, num_of_bodies=num_of_bodies),
                         ps,
                         vs,
                         paths
                     ],
                     update_function=render_nbodysystem)

    myseq.start()
