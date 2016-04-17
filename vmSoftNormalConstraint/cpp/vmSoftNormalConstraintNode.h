#ifndef _vmSoftNormalConstraintNode
#define _vmSoftNormalConstraintNode
//
// Copyright (C) Vincent Mazeas
// 
// File: vmSoftNormalConstraintNode.h
//
// Dependency Graph Node: vmSoftNormalConstraint
//
// Author: Maya Plug-in Wizard 2.0
//

#include <vector>

#include <assert.h> 

#include <maya/MPxNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MTypeId.h> 

#include <maya/MItMeshPolygon.h>
#include <maya/MMatrix.h>
#include <maya/MQuaternion.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnMesh.h>

class vmSoftNormalConstraint : public MPxNode
{
private:

    static  MVector     getMedianVector(
                            std::vector<MVector> const& vectorList
                        );

    static std::string  getDoubleAsString(
                            double input
                        );

    virtual void        getFacesInRadius(
                            MObject meshObject,
                            MPoint referencePosition,
                            int faceIndex,
                            double radius,
                            std::vector<int> & indexList,
                            std::vector<MVector> & normalList
                        );

public:
    vmSoftNormalConstraint();
    virtual             ~vmSoftNormalConstraint();

    virtual MStatus     compute(const MPlug& plug, MDataBlock& data);

    static  void*       creator();
    static  MStatus     initialize();

public:

    // There needs to be a MObject handle declared for each attribute that
    // the node will have.  These handles are needed for getting and setting
    // the values later.
    static  MObject     inputMesh;
    static  MObject     inputMatrix;
    static  MObject     radius;
    static  MObject     outPolyNumber;
    static  MObject     outRotateX;
    static  MObject     outRotateY;
    static  MObject     outRotateZ;
    static  MObject     outRotate;


    // The typeid is a unique 32bit indentifier that describes this node.
    // It is used to save and retrieve nodes of this type from the binary
    // file format.  If it is not unique, it will cause file IO problems.
    //
    static  MTypeId     id;
};

#endif
