from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath, Mat4, Vec3, OrthographicLens, MatrixLens, loadPrcFileData

from local_utils import math_utils
import numpy as np
import math

from direct.task import Task
from panda3d.core import GeomNode, LineSegs

def to_forrowvecs(m4x4):
    """
    p3d uses internally a different matrix multiplication style
    than is traditionally used in math. This function converts the
    traditional format of a matrix into the p3d format.

    Parameters:
    - m4x4 is a 4x4 matrix in the not-forrowvecs format
    """
    return Mat4(*tuple(np.transpose(m4x4).flatten()))

def from_forrowvecs(p3d_forrowvecs):
    """ """
    return np.ravel(np.array(list(p3d_forrowvecs))).reshape((4, 4)).T

def get_ortho_projection_matrix(right, left, up, bottom, near, far):
    """ according to http://learnwebgl.brown37.net/08_projections/projections_ortho.html,
        a projection matrix projects all vertices in a scene into the cube between
        (-1, -1, -1), (+1, +1, +1) of the viewing frustum.
        In panda3d, I'm not sure how to set a basic projection matrix like this, without
        using setFilmSize or getFilmSize, lenses, etc. .
        I think, the Lens corresponds to the projection matrix """
    mid_x = (left + right) / 2.
    mid_y = (bottom + up) / 2.
    mid_z = (-near + -far) / 2.

    centerAboutOrigin = np.array([[1., 0., 0., -mid_x],
                                  [0., 1., 0., -mid_y],
                                  [0., 0., 1., -mid_z],
                                  [0., 0., 0., 1.    ]])

    scale_x = 2.0 / (right - left)
    scale_y = 2.0 / (up - bottom)
    scale_z = 2.0 / (far - near)

    scaleViewingVolume = np.array([[scale_x, 0.      , 0.,      0.],
                                   [0.,      scale_y,  0.,      0.],
                                   [0.,      0.      , scale_z, 0.],
                                   [0.,      0.      , 0.,      1.]])

    convertToLeftHanded = np.array([[1., 0.,  0., 0.],
                                    [0., 1.,  0., 0.],
                                    [0., 0., -1., 0.],
                                    [0., 0.,  0., 1.]])

    return np.linalg.multi_dot([centerAboutOrigin, scaleViewingVolume, convertToLeftHanded])


# p3d window
winsizex_0 = 700
winsizey_0 = 700
loadPrcFileData('', 'win-size ' + str(winsizex_0) + ' ' + str(winsizey_0))

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setBackgroundColor(0.2, 0.2, 0.2)

        # -------- plot coordinate system
        ls = LineSegs()
        ls.setThickness(1)

        # X axis
        ls.setColor(1.0, 0.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(1.0, 0.0, 0.0)

        # Y axis
        ls.setColor(0.0, 1.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 1.0, 0.0)

        # Z axis
        ls.setColor(0.0, 0.0, 1.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 0.0, 1.0)

        geomnode = ls.create()
        nodepath = NodePath(geomnode)
        nodepath.setLightOff(1)
        nodepath.reparentTo(render)

        # -------- experiments with projection matrix

        # # -----------
        lens = OrthographicLens()
        far = 1.
        near = -1.
        lens.setNearFar(near, far)

        # x_filmsize = 3 * 1.
        # y_filmsize = 3 * 1.
        # x_filmsize = 1.
        # y_filmsize = 1.
        # lens.setFilmSize(x_filmsize, y_filmsize)
        # lens.setFilmMat()

        print(base.cam.node().getLens().getFilmMat())
        # base.cam.node().getLens().setFilmMat(
        #     to_forrowvecs(Mat4(*tuple(np.flatten(np.eye(4))))))
        # print(base.cam.node().getLens().getUserMat())
        print(base.cam.node().getLens().getLensMat())

        base.cam.node().getLens().setFilmSize(2, 2)

        print(base.cam.node().getLens().getFilmMat())
        # print(base.cam.node().getLens().user_mat)
        print(base.cam.node().getLens().getLensMat())

        lensMat = base.cam.node().getLens().getLensMat()
        filmMat = from_forrowvecs(base.cam.node().getLens().getFilmMat())

        proj_mat = get_ortho_projection_matrix(right, left, up, bottom, near, far)

        completeProjMat = np.linalg.multi_dot(
            [np.linalg.inv(lensMat),
             np.eye(4),
             filmMat
            ])

        print("to_forrowvecs(completeProjMat)")
        print(to_forrowvecs(completeProjMat))

        base.cam.node().setLens(lens)

        print("proj mat (1): ")
        print("projection mat: ")
        print(base.cam.node().getLens().getProjectionMat())
        print("film mat: ")
        print(base.cam.node().getLens().getFilmMat())
        # print("user mat: ")
        # print(base.cam.node().getLens().getUserMat())
        # # -----------

        # # -----------
        # lens = MatrixLens()
        # # lens.setNearFar(-500., 500.)
        # # x_filmsize = 2 * 1.
        # # y_filmsize = x_filmsize * 9./16.
        # # lens.setFilmSize(x_filmsize, y_filmsize)

        # far = 100.
        # near = -100.

        # # x_filmsize = 2 * 1.5
        # # y_filmsize = x_filmsize * 9./16.

        # right = x_filmsize/2.
        # left = -right
        # up = y_filmsize/2.
        # bottom = -up

        # proj_mat = get_ortho_projection_matrix(right, left, up, bottom, near, far)

        # print(to_forrowvecs(proj_mat))
        # lens.setUserMat(to_forrowvecs(proj_mat))
        # base.cam.node().setLens(lens)

        # print("proj mat (2): ")
        # print(base.cam.node().getLens().getProjectionMat())
        # print(base.cam.node().getLens().getFilmSize())
        # print("film mat: ")
        # print(base.cam.node().getLens().getFilmMat())

app = MyApp()
app.run()
