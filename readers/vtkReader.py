# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 10:40:35 2023

@author: grife
"""

from vtk import vtkUnstructuredGridReader
from os.path import exists


def readVtk(path,filename):
    fullFilename1 = path + filename + ".vtk"
    if (exists(fullFilename1)):
        print("##Reading: " + filename)
        
        # Set up poly data reader for result set 1
        reader = vtkUnstructuredGridReader()
        reader.SetFileName(fullFilename1)
        reader.ReadAllVectorsOn()
        reader.ReadAllScalarsOn()
        reader.Update()
        grid = reader.GetOutput()
        return grid
        
    return None