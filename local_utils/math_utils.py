from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4

import numpy as np
import math


# ---- active euler rotation matrices
def get_R_x(angle):
    return np.array([[1, 0, 0],
                     [0, math.cos(angle), -math.sin(angle)],
                     [0, math.sin(angle), math.cos(angle)]])

def get_R_y(angle):
    return np.array([[math.cos(angle), 0, math.sin(angle)],
                     [0, 1, 0],
                     [-math.sin(angle), 0, math.cos(angle)]])

def get_R_z(angle):
    return np.array([[math.cos(angle), -math.sin(angle), 0],
                     [math.sin(angle), math.cos(angle), 0],
                     [0, 0, 1]])


def get_R_x_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_x(angle)))

def get_R_y_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_y(angle)))

def get_R_z_forrowvecs(angle):
    return to_forrowvecs(make_3x3_matrix_affine(get_R_z(angle)))


def make_3x3_matrix_affine(m):
    """
    m is a 3x3 matrix
    just append the fourth column and row
    of the 4x4 identity matrix
    """

    return np.array(
        [[m[0][0], m[0][1], m[0][2], 0.],
         [m[1][0], m[1][1], m[1][2], 0.],
         [m[2][0], m[2][1], m[2][2], 0.],
         [0,       0,       0, 1.]])

def to_forrowvecs(m4x4):
    """
    p3d uses internally a different matrix multiplication style
    than is traditionally used in math. This function converts the
    traditional format of a matrix into the p3d format.

    Parameters:
    - m4x4 is a 4x4 matrix in the not-forrowvecs (normal) format
    """
    return Mat4(*tuple(np.transpose(m4x4).flatten()))

def getScalingMatrix3d_forrowvecs(vx, vy, vz):
    scaling = np.array([[vx,  0,  0, 0],
                        [0,  vy,  0, 0],
                        [0,   0, vz, 0],
                        [0,   0,  0, 1]])
    scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))
    return scaling_forrowvecs


def getTranslationMatrix3d_forrowvecs(bx, by, bz):
    # bx = 0.5
    # by = 0
    # bz = 0
    translation_to_xhat = np.array(
        [[1, 0, 0, bx],
         [0, 1, 0, by],
         [0, 0, 1, bz],
         [0, 0, 0,  1]])
    translation_forrowvecs = Mat4(
        *tuple(np.transpose(translation_to_xhat).flatten()))
    return translation_forrowvecs


def getNormFromP3dVector(p3dvec3):
    return np.linalg.norm([p3dvec3.getX(), p3dvec3.getY(), p3dvec3.getZ()])


def LinePlaneCollision(planeNormal, planePoint, rayDirection, rayPoint, epsilon=1e-6):
    """
    quickly taken from https://rosettacode.org/wiki/Find_the_intersection_of_a_line_with_a_plane#Python
    Returns the intersection point
    """

    ndotu = planeNormal.dot(rayDirection)
    if abs(ndotu) < epsilon:
            raise RuntimeError("no intersection or line is within plane")

    w = rayPoint - planePoint
    si = -planeNormal.dot(w) / ndotu
    Psi = w + si * rayDirection + planePoint
    return Psi

def p3d_to_np(p3d_3f):
    return np.array([p3d_3f[0], p3d_3f[1], p3d_3f[2]])
