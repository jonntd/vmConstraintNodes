#!/usr/bin/python
# -*- coding: utf8 -*-

"""
vmMultiGeometryConstraint
Vincent 'Kotch' Mazeas // vincent.mazeas@gmail.com // www.vincentmazeas.com
"""

from maya import OpenMaya, OpenMayaMPx

node_name = 'vmMultiGeometryConstraint'
node_id = OpenMaya.MTypeId(0x00122600, 51)


class vmMultiGeometryConstraint(OpenMayaMPx.MPxNode):

    def __init__(self):
        # Mother class init
        OpenMayaMPx.MPxNode.__init__(self)

        # MIntArray for Array Plug indices
        self.prev_pos = OpenMaya.MPoint()
        self.max_distance = 1e7
        self.indices_list = OpenMaya.MIntArray()

    def compute(self, plug, data):

        # Input plug filter
        if plug != vmMultiGeometryConstraint.outTranslate_attr:
            return OpenMaya.kUnknownParameter

        # GET : meshes
        in_meshes = OpenMaya.MArrayDataHandle(
            data.inputValue(vmMultiGeometryConstraint.inputMeshes)
        )
        meshes = [in_meshes.inputValue().asMesh()]
        for i in xrange(in_meshes.elementCount()-1):
            in_meshes.next()
            meshes.append(in_meshes.inputValue().asMesh())

        # GET : Matrices
        in_matrices = OpenMaya.MArrayDataHandle(
            data.inputValue(vmMultiGeometryConstraint.inputMatrices)
        )
        matrices = [in_matrices.inputValue().asMatrix()]
        for i in xrange(in_matrices.elementCount()-1):
            in_matrices.next()
            matrices.append(in_matrices.inputValue().asMatrix())

        # GET : Input position
        mtx = data.inputValue(vmMultiGeometryConstraint.inputMatrix_attr).asMatrix()
        this_position = OpenMaya.MPoint(mtx(3, 0), mtx(3, 1), mtx(3, 2))

        closest_delta = self.max_distance
        closest_point = OpenMaya.MFloatPoint()

        # Get input meshes count
        # mesh_plug.getExistingArrayAttributeIndices(self.indices_list)

        # Main loop
        for m, mat in zip(meshes, matrices):

            # # Get Mesh and closestPoint
            # mfnmesh = OpenMaya.MFnMesh(m)
            # this_closest_point = OpenMaya.MPoint()
            # mfnmesh.getClosestPoint(this_position, this_closest_point)

            # # Compare with before
            # this_delta = this_closest_point.distanceTo(this_position)
            # if this_delta < closest_delta:
            #     closest_point = this_closest_point
            #     closest_delta = this_delta

            # Get Mesh and closestPoint
            intersector = OpenMaya.MMeshIntersector()
            intersector.create(m, mat)
            this_closest_point = OpenMaya.MPointOnMesh()
            intersector.getClosestPoint(this_position, this_closest_point)
            this_closest_point = OpenMaya.MPoint(
                this_closest_point.getPoint()
            )

            # Compare with before
            this_delta = this_closest_point.distanceTo(this_position)
            if this_delta < closest_delta:
                closest_point = this_closest_point
                closest_delta = this_delta

        # Remember, remember, the fifth of November
        self.prev_pos = closest_point

        # for k in xrange(self.indices_list.length()):
        #     mesh_handle.jumpToArrayElement(k)
        #     temp_msh = OpenMaya.MFnMesh(mesh_handle.inputValue().asMesh())

        # Set output rotate
        out_translate_dh = data.outputValue(vmMultiGeometryConstraint.outTranslate_attr)
        out_translate_dh.set3Float(closest_point.x, closest_point.y, closest_point.z)
        data.setClean(plug)


def nodeInit():

    # Init class and OpenMaya vars
    cls = vmMultiGeometryConstraint
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()

    kMesh = OpenMaya.MFnData.kMesh
    kDouble = OpenMaya.MFnMatrixAttribute.kDouble

    # Input Meshes
    cls.inputMeshes = tAttr.create("inputMeshes", "inMesh", kMesh)
    tAttr.setArray(True)
    tAttr.setReadable(False)
    tAttr.setStorable(False)
    cls.addAttribute(cls.inputMeshes)

    # Input Matrices
    cls.inputMatrices = mAttr.create("inputMatrices", "inMatr", kDouble)
    mAttr.setArray(True)
    mAttr.setReadable(False)
    mAttr.setStorable(False)
    cls.addAttribute(cls.inputMatrices)

    # Input Position Matrix
    cls.inputMatrix_attr = mAttr.create("inputMatrix", "inMtx", kDouble)
    cls.addAttribute(cls.inputMatrix_attr)

    # Output Translate
    cls.outTranslate_attr = nAttr.createPoint("outTranslate", "oT")
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    nAttr.setKeyable(False)
    nAttr.setDefault(0.0, 0.0, 0.0)
    cls.addAttribute(cls.outTranslate_attr)

    # Set the attribute dependencies
    cls.attributeAffects(cls.inputMeshes, cls.outTranslate_attr)
    cls.attributeAffects(cls.inputMatrices, cls.outTranslate_attr)
    cls.attributeAffects(cls.inputMatrix_attr, cls.outTranslate_attr)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(vmMultiGeometryConstraint())


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, 'Vincent Mazeas', '1.0', 'Any')
    try:
        mplugin.registerNode(
            node_name, node_id, nodeCreator, nodeInit
        )
    except:
        raise Exception('Unable to register node: {}'.format(node_name))


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(node_id)
    except:
        raise Exception('Failed to deregister node: {}'.format(node_name))
