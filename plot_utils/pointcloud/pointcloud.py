from composed_objects.composed_objects import Scatter

import numpy as np

def plot_xy_z(x_set, y_set, z_func):
    points_xyz = np.empty((0, 3))  # define empty array to stack onto
    for y_ in y_set:
        for x_ in x_set:
            points_xyz = np.append(points_xyz, np.array([[x_, y_, z_func(x_, y_)]]), axis=0)

    scat = Scatter(points_xyz[:,0], points_xyz[:,1], z=points_xyz[:,2])

# # -- plot surface using points
# from plot_utils.pointcloud.pointcloud import plot_xy_z
# x = np.linspace(0., 1., num=20, endpoint=True)
# y = np.linspace(0., 1., num=20, endpoint=True)
# plot_xy_z(x, y, lambda x, y: x**3. + y**3.)
