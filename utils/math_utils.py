from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4

import numpy as np

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
    translation_forrowvecs = Mat4(*tuple(np.transpose(translation_to_xhat).flatten()))
    return translation_forrowvecs
