//
// Copyright (C) Vincent Mazeas
// 
// File: pluginMain.cpp
//
// Author: Maya Plug-in Wizard 2.0
//

#include "vmSoftNormalConstraintNode.h"
#include <maya/MFnPlugin.h>

MStatus initializePlugin( MObject obj )
//
//	Description:
//		this method is called when the plug-in is loaded into Maya.  It 
//		registers all of the services that this plug-in provides with 
//		Maya.
//
//	Arguments:
//		obj - a handle to the plug-in object (use MFnPlugin to access it)
//
{ 
	MStatus   status;
	MFnPlugin plugin( obj, "Vincent Mazeas", "2016", "Any");

	status = plugin.registerNode(
		"vmSoftNormalConstraint",
		vmSoftNormalConstraint::id,
		vmSoftNormalConstraint::creator,
		vmSoftNormalConstraint::initialize
	);

	if (!status) {
		status.perror("registerNode");
		return status;
	}

	return status;
}

MStatus uninitializePlugin( MObject obj)
//
//	Description:
//		this method is called when the plug-in is unloaded from Maya. It 
//		deregisters all of the services that it was providing.
//
//	Arguments:
//		obj - a handle to the plug-in object (use MFnPlugin to access it)
//
{
	MStatus   status;
	MFnPlugin plugin( obj );

	status = plugin.deregisterNode( vmSoftNormalConstraint::id );
	if (!status) {
		status.perror("deregisterNode");
		return status;
	}

	return status;
}
