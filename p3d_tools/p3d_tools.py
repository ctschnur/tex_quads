from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

def findChildrenAndSetRenderModeRecursively(parentnode):
    children = parentnode.get_children_p3d()
    for child in children:
        findChildrenAndSetRenderModeRecursively(child)
        child.setRenderModeFilled()
