//
// Copyright (C) Vincent Mazeas
// 
// File: vmSoftNormalConstraintNode.cpp
//
// Dependency Graph Node: vmSoftNormalConstraint
//
// Author: Maya Plug-in Wizard 2.0
//

#include "vmSoftNormalConstraintNode.h"

// Debug stream to print doubles
// #include <sstream>

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MGlobal.h>


// MTypeId
MTypeId	   vmSoftNormalConstraint::id(0x00122600, 50);

// Attributes
MObject    vmSoftNormalConstraint::inputMesh;
MObject    vmSoftNormalConstraint::inputMatrix;
MObject    vmSoftNormalConstraint::radius;
MObject    vmSoftNormalConstraint::outPolyNumber;
MObject    vmSoftNormalConstraint::outRotate;
MObject    vmSoftNormalConstraint::outRotateX;
MObject    vmSoftNormalConstraint::outRotateY;
MObject    vmSoftNormalConstraint::outRotateZ;

// Constructors / Destructors
vmSoftNormalConstraint::vmSoftNormalConstraint() {}
vmSoftNormalConstraint::~vmSoftNormalConstraint() {}


void vmSoftNormalConstraint::getFacesInRadius(MObject meshObject,
											  MPoint referencePosition,
											  int faceIndex,
											  double radius,
											  std::vector<int> & indexList,
											  std::vector<MVector> & normalList)
{

	int       prevPtr;
	MVector   normalPtr;
	MIntArray connectedFacesPtr;
	MItMeshPolygon meshIterator(meshObject);

	meshIterator.setIndex(faceIndex, prevPtr);
	meshIterator.getNormal(normalPtr);
	meshIterator.getConnectedFaces(connectedFacesPtr);

	// Add face index and face normal to lists
	indexList.push_back(faceIndex);
	normalList.push_back(normalPtr);

	// Process connected faces
	for (unsigned int i = 0; i < connectedFacesPtr.length(); i++)
	{
		int  face = connectedFacesPtr[i];
		bool isfaceinlist = (std::find(indexList.begin(), indexList.end(), face) != indexList.end());

		if (!isfaceinlist)
		{
			int       prevPtr2; // is that really necessary ?
			meshIterator.setIndex(face, prevPtr2);

			double distance = referencePosition.distanceTo(meshIterator.center());

			if (distance < radius)
			{
				this->getFacesInRadius(meshObject, referencePosition, face, radius, indexList, normalList);
			}
			/*
			else
			{
				MGlobal::displayInfo("getFacesInRadius : Compute Mark 4 : False");

				std::ostringstream strs;
				strs << faceIndex << " / " << face << "  ::  " << distance ;
				std::string str = strs.str();
				MGlobal::displayInfo(str.c_str());

				MGlobal::displayInfo("");
			}
			*/
		}
	}
}


MVector vmSoftNormalConstraint::getMedianVector(std::vector<MVector> const& vectorList)
{
	MVector baseVector(0.0, 0.0, 0.0);
	for (int i = 0; i < vectorList.size(); i++)
	{
		baseVector += vectorList[i];
	}
	return baseVector.normal();
}


MStatus vmSoftNormalConstraint::compute(const MPlug& plug, MDataBlock& data)
//
//	Description:
//		This method computes the value of the given output plug based
//		on the values of the input attributes.
//
//	Arguments:
//		plug - the plug to compute
//		data - object that provides access to the attributes for this node
//
{
	MStatus returnStatus;

	// Check which output attribute we have been asked to compute.  If this 
	// node doesn't know how to compute it, we must return MS::kUnknownParameter.
	// 
	if (plug == outRotate)
	{
		// Get a handle to the input attribute that we will need for the
		// computation.  If the value is being supplied via a connection 
		// in the dependency graph, then this call will cause all upstream  
		// connections to be evaluated so that the correct value is supplied.
		// 
		MDataHandle inputMeshHandle   = data.inputValue(inputMesh,   &returnStatus);
		MDataHandle inputMatrixHandle = data.inputValue(inputMatrix, &returnStatus);
		MDataHandle inputRadiusHandle = data.inputValue(radius,      &returnStatus);

		if (returnStatus != MS::kSuccess)
		{
			MGlobal::displayError("Node vmSoftNormalConstraint cannot get value.");
		}
		else
		{

			// Get a input values as objects
			MObject					inputMsh = inputMeshHandle.asMesh();
			MTransformationMatrix   inputMtx = inputMatrixHandle.asMatrix();
			double					inputRad = inputRadiusHandle.asDouble();

			// Get closest face index and position from input matrix.
			int			closestIndex;
			MPoint		refpos(inputMtx.getTranslation(MSpace::kWorld));
			MPoint		closestPos;
			MFnMesh		inputMeshFn(inputMsh);
			inputMeshFn.getClosestPoint(refpos, closestPos, MSpace::kWorld, &closestIndex);

			// Recursively get all faces within radius of the closest face to position.
			std::vector<int>	    list_indexes;
			std::vector<MVector>	list_normals;
			MItMeshPolygon			iterator(inputMsh);
			this->getFacesInRadius(inputMsh, closestPos, closestIndex, inputRad, list_indexes, list_normals);

			// Computes output angle
			MVector			baseVector(0.0, 1.0, 0.0);
			MVector			outVector = this->getMedianVector(list_normals);
			MQuaternion		outQuat = baseVector.rotateTo(outVector);
			MEulerRotation	outEuler = outQuat.asEulerRotation();

			// This just copies the input value through to the output.
			MDataHandle outputHandleX = data.outputValue(vmSoftNormalConstraint::outRotateX);
			outputHandleX.set(outEuler.x);
			MDataHandle outputHandleY = data.outputValue(vmSoftNormalConstraint::outRotateY);
			outputHandleY.set(outEuler.y);
			MDataHandle outputHandleZ = data.outputValue(vmSoftNormalConstraint::outRotateZ);
			outputHandleZ.set(outEuler.z);
			MDataHandle outputHandleN = data.outputValue(vmSoftNormalConstraint::outPolyNumber);
			outputHandleN.set((int)(list_normals.size()));

			// Mark the destination plug as being clean.  This will prevent the
			// dependency graph from repeating this calculation until an input 
			// of this node changes.
			data.setClean(plug);
		}
	}
	else {
		return MS::kUnknownParameter;
	}

	return MS::kSuccess;
}


void* vmSoftNormalConstraint::creator()
//
//	Description:
//		this method exists to give Maya a way to create new objects
//      of this type. 
//
//	Return Value:
//		a new object of this type
//
{
	return new vmSoftNormalConstraint();
}


MStatus vmSoftNormalConstraint::initialize()
//
//	Description:
//		This method is called to create and initialize all of the attributes
//      and attribute dependencies for this node type.  This is only called 
//		once when the node type is registered with Maya.
//
//	Return Values:
//		MS::kSuccess
//		MS::kFailure
//		
{

	MFnNumericAttribute nAttr;
	MFnUnitAttribute    uAttr;
	MFnMatrixAttribute  mAttr;
	MFnTypedAttribute   tAttr;
	MStatus				stat;

	inputMesh = tAttr.create("inputMesh", "inMsh", MFnData::kMesh);
	tAttr.setStorable(false);
	tAttr.setReadable(false);

	inputMatrix = mAttr.create("inputMatrix", "inMtx", MFnMatrixAttribute::kDouble);
	mAttr.setStorable(false);

	radius = nAttr.create("radius", "r", MFnNumericData::kDouble, 1.0);
	nAttr.setKeyable(true);
	nAttr.setMin(0.1);
	nAttr.setMax(10.);
	nAttr.setDefault(1.);

	outPolyNumber = nAttr.create("outPolyNumber", "oPn", MFnNumericData::kInt, 1.0);
	nAttr.setWritable(false);
	nAttr.setStorable(false);

	outRotateX = uAttr.create("outRotateX", "oRx", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(false);
	uAttr.setStorable(false);

	outRotateY = uAttr.create("outRotateY", "oRy", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(false);
	uAttr.setStorable(false);

	outRotateZ = uAttr.create("outRotateZ", "oRz", MFnUnitAttribute::kAngle, 0.0);
	uAttr.setWritable(false);
	uAttr.setStorable(false);

	outRotate = nAttr.create("outRotate", "oR", outRotateX, outRotateY, outRotateZ);
	nAttr.setWritable(false);
	nAttr.setStorable(false);

	// Add the attributes we have created to the node
	stat = addAttribute(inputMesh);
	if (!stat) { stat.perror("addAttribute inMesh"); return stat; }
	stat = addAttribute(inputMatrix);
	if (!stat) { stat.perror("addAttribute inMatrix"); return stat; }
	stat = addAttribute(radius);
	if (!stat) { stat.perror("addAttribute Radius"); return stat; }
	stat = addAttribute(outPolyNumber);
	if (!stat) { stat.perror("addAttribute outPolyNumber"); return stat; }
	stat = addAttribute(outRotate);
	if (!stat) { stat.perror("addAttribute OutRotate"); return stat; }

	// Set up a dependency between the input and the output.  This will cause
	// the output to be marked dirty when the input changes.  The output will
	// then be recomputed the next time the value of the output is requested.
	//
	stat = attributeAffects(inputMesh, outRotate);
	if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inputMatrix, outRotate);
	if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(radius, outRotate);
	if (!stat) { stat.perror("attributeAffects"); return stat; }

	// Redundant but important, otherwise it's calculated but the plug isn't marked
	// as dirty and will therefore not propagate to any other node.
	stat = attributeAffects(inputMesh, outPolyNumber);
	if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(inputMatrix, outPolyNumber);
	if (!stat) { stat.perror("attributeAffects"); return stat; }
	stat = attributeAffects(radius, outPolyNumber);
	if (!stat) { stat.perror("attributeAffects"); return stat; }

	return MS::kSuccess;

}
