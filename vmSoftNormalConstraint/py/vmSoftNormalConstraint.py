#!/usr/bin/python
# -*- coding: utf8 -*-

"""
vmSoftNormalConstraint Maya Plug-in
Vincent 'Kotch' Mazeas // vincent.mazeas@gmail.com // www.vincentmazeas.com
"""

# Maya API
from maya import OpenMaya, OpenMayaMPx

# Plug-in vars
node_name = 'vmSoftNormalConstraint'
node_id = OpenMaya.MTypeId(0x00122600, 50)


class vmSoftNormalConstraint(OpenMayaMPx.MPxNode):

    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

        # MScriptUtil and base vector
        self.MSUtil = OpenMaya.MScriptUtil()
        self.base_vector = OpenMaya.MVector(0, 1, 0)

    def get_closest_f_data(self, meshfn, mtx):
        # Init out vars
        face_i = self.MSUtil.asIntPtr()
        face_p = OpenMaya.MPoint()

        # Init MFnMesh and getClosestPoint
        pos = mtx.getTranslation(OpenMaya.MSpace.kWorld)
        meshfn.getClosestPoint(
            OpenMaya.MPoint(pos), face_p, OpenMaya.MSpace.kWorld, face_i
        )

        # Return pos, index
        return face_p, OpenMaya.MScriptUtil(face_i).asInt()

    def get_faces_in_radius(self, iterator, li_id, li_nr, face, pos, radius):

        # Init pointers // previd_ptr is useless
        previd_ptr = self.MSUtil.asIntPtr()
        normal_ptr = OpenMaya.MVector()
        cfaces_ptr = OpenMaya.MIntArray()

        # Set current, get normals and connected faces
        iterator.setIndex(face, previd_ptr)
        iterator.getNormal(normal_ptr)
        iterator.getConnectedFaces(cfaces_ptr)

        # Append index and normal
        li_id.append(face)
        li_nr.append(normal_ptr)

        # Process connected faces
        for f in cfaces_ptr:
            if f not in li_id:
                previd2_ptr = self.MSUtil.asIntPtr()
                iterator.setIndex(f, previd2_ptr)

                if pos.distanceTo(iterator.center()) < radius:
                    self.get_faces_in_radius(
                        iterator, li_id, li_nr, f, pos, radius
                    )

    def get_median_vector(self, vector_list):
        base_v = OpenMaya.MVector()
        for v in vector_list:
            base_v += v
        return base_v.normal()

    def compute(self, plug, data):

        # Clean plug
        data.setClean(plug)

        # Get vars : Mesh, Matrix, Radius (need top vector too)
        input_msh = data.inputValue(vmSoftNormalConstraint.inputMesh_attr).asMesh()
        input_mtx = data.inputValue(vmSoftNormalConstraint.inputMatrix_attr).asMatrix()
        input_rad = data.inputValue(vmSoftNormalConstraint.radius_attr).asFloat()

        # Main Process
        liID, liNormal = [], []
        c_pos, c_index = self.get_closest_f_data(
            OpenMaya.MFnMesh(input_msh),
            OpenMaya.MTransformationMatrix(input_mtx)
        )

        # Create Iterator, get all faces
        iterator = OpenMaya.MItMeshPolygon(input_msh)
        self.get_faces_in_radius(
            iterator, liID, liNormal, c_index, c_pos, input_rad
        )

        # Compute output angles
        out_vector = self.get_median_vector(liNormal)
        out_quat = self.base_vector.rotateTo(out_vector)
        out_euler = [OpenMaya.MAngle(x) for x in out_quat.asEulerRotation()]

        # Set output debug
        out_debug_polycount = data.outputValue(vmSoftNormalConstraint.outPoly_attr)
        out_debug_polycount.setFloat(len(liID))
        out_debug_polycount.setClean()

        # Set output rotate
        out_rotate_x_dh = data.outputValue(vmSoftNormalConstraint.outRotateX_attr)
        out_rotate_x_dh.setMAngle(out_euler[0])
        out_rotate_x_dh.setClean()
        out_rotate_y_dh = data.outputValue(vmSoftNormalConstraint.outRotateY_attr)
        out_rotate_y_dh.setMAngle(out_euler[1])
        out_rotate_y_dh.setClean()
        out_rotate_z_dh = data.outputValue(vmSoftNormalConstraint.outRotateZ_attr)
        out_rotate_z_dh.setMAngle(out_euler[2])
        out_rotate_z_dh.setClean()


def nodeInit():

    # Init class and OpenMaya vars
    cls = vmSoftNormalConstraint
    nAttr = OpenMaya.MFnNumericAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()

    # Setup input attributes
    cls.inputMesh_attr = tAttr.create( "inputMesh", "inMsh", OpenMaya.MFnData.kMesh )
    tAttr.setReadable(False)
    cls.addAttribute(cls.inputMesh_attr )

    cls.inputMatrix_attr = mAttr.create("inputMatrix", "inMtx", OpenMaya.MFnMatrixAttribute.kDouble)
    cls.addAttribute(cls.inputMatrix_attr )

    # Radius
    cls.radius_attr = nAttr.create("radius", "r", OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.)
    nAttr.setMax(5.)
    nAttr.setDefault(1.)
    cls.addAttribute(cls.radius_attr)

    # Debug Poly len
    cls.outPoly_attr = nAttr.create("outPolyNumber", "oPn", OpenMaya.MFnNumericData.kFloat, 1.0)
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    cls.addAttribute(cls.outPoly_attr)

    # outRotateX
    cls.outRotateX_attr = uAttr.create("outRotateX", "oRx", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setWritable(False)
    uAttr.setStorable(False)
    cls.addAttribute(cls.outRotateX_attr)

    # outRotateY
    cls.outRotateY_attr = uAttr.create("outRotateY", "oRy", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setWritable(False)
    uAttr.setStorable(False)
    cls.addAttribute(cls.outRotateY_attr)

    # outRotateZ
    cls.outRotateZ_attr = uAttr.create("outRotateZ", "oRz", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
    uAttr.setWritable(False)
    uAttr.setStorable(False)
    cls.addAttribute(cls.outRotateZ_attr)

    # outRotate
    cls.outRotate_attr = nAttr.create(
        "outRotate", "oR",
        cls.outRotateX_attr, cls.outRotateY_attr, cls.outRotateZ_attr
    )
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    cls.addAttribute(cls.outRotate_attr)

    # Set the attribute dependencies
    cls.attributeAffects(cls.inputMesh_attr, cls.outRotate_attr)
    cls.attributeAffects(cls.inputMesh_attr, cls.outPoly_attr)
    cls.attributeAffects(cls.inputMatrix_attr, cls.outRotate_attr)
    cls.attributeAffects(cls.inputMatrix_attr, cls.outPoly_attr)
    cls.attributeAffects(cls.radius_attr, cls.outRotate_attr)
    cls.attributeAffects(cls.radius_attr, cls.outPoly_attr)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(vmSoftNormalConstraint())


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Vincent Mazeas", "1.0", "Any")
    try:
        mplugin.registerNode(
            node_name, node_id, nodeCreator, nodeInit
        )
    except:
        raise Exception("Unable to register node: {}".format(node_name))


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(node_id)
    except:
        raise Exception("Failed to deregister node: {}".format(node_name))
