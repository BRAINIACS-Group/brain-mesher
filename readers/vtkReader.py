# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 10:40:35 2023

@author: grife
"""


from vtk import vtkIdList,vtkUnstructuredGridReader
from os.path import exists 
from mesh import Node, Element, Mesh;
from writers.Writers import Writer;


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

def readData():
    # inputPath = "C:\\Users\grife\OneDrive\Documents\PostDoc\BrainModels\Tumor_growth\\"
    inputPath = "C:\\Users\grife\OneDrive\Documents\PostDoc\BrainModels\Atrophy_Results\OAS1_0004\\"
    for t in range(0,35,2):
        f = "Slice_" + str(t)
        dataMap = {}
        grid = readVtk(inputPath, f)

        mesh = Mesh();
        mesh.dataToWrite = ["displacement"]
        mesh.cellData = ["displacement_centroid", "von_mises"]
        displacementArray = grid.GetPointData().GetArray("displacement")
        materialsArray = grid.GetPointData().GetArray("material_ids")
        vonMisesArray = grid.GetPointData().GetArray("von_mises")

        disp_data = {} # Key = starting position, displacement
        point_position_to_nodes = {} # Key= point position, value  = node value
        cell_point_to_nodes = {} # Key= cell pointId, value  = node value
        nodeMap = {}
        elementsMap = {}
        elementToMaterial = {}
        for k in range(grid.GetNumberOfCells()):
            cellIds = vtkIdList()
            grid.GetCellPoints(k, cellIds)
            ica = []
            mat = 0
            displacement_tot = [0,0,0];
            von_Mises = 0
            for i in range(8):
                pointId = cellIds.GetId(i)
                pointPosition = grid.GetPoint(pointId)
                mat += materialsArray.GetValue(pointId)
                position_key = "-".join([str(x) for x in pointPosition])
                nodeValue = point_position_to_nodes.get(position_key,-1)
                if nodeValue != -1:
                    cell_point_to_nodes[pointId] = nodeValue
                    node = nodeMap[int(nodeValue)]
                    displacement = disp_data[nodeValue];
                    assert [disp_data.get(nodeValue,-1) != -1]
                else:
                   nodeValue = pointId
                   cell_point_to_nodes[pointId] = nodeValue
                   point_position_to_nodes[position_key] = pointId
                   displacement = [round(y,6) for y in displacementArray.GetTuple(pointId)]
                   von_Mises += round(vonMisesArray.GetTuple(pointId)[0],6)
                   disp_data[pointId] = displacement
                   newPosition = [round(y,6) for y in pointPosition]
                   for d in range(len(displacement)):
                        newPosition[d] = pointPosition[d]+displacement[d]
                        if d == 2:
                            newPosition[d] += 4
                   node = Node(int(nodeValue),newPosition)
                   node.addData("displacement", displacement)
                   nodeMap[int(nodeValue)] = node;
                for d in range(3):
                    displacement_tot[d] += displacement[d];
                ica.append(node)
            element = Element(k,ica)
            element.setMaterial((mat/8))
            element.properties['displacement_centroid'] = [d/8. for d in displacement_tot]
            element.properties['von_mises'] = [von_Mises/8.]
            elementsMap[k] = element

        mesh.nodes = nodeMap
        mesh.elements = elementsMap

        ## Write deformed mesh to new vtk
        path = inputPath
        filename = f + "_output_deformed"
        writer = Writer()
        writer.openWriter("vtk", filename, path)
        writer.writeMeshData(mesh)
        writer.closeWriter()



# from vtk.util.numpy_support import vtk_to_numpy
# from vtkmodules.vtkCommonDataModel import (
#     vtkCellTypes,
#     vtkGenericCell
# )
# from ABQ_UCD_handling import writeVTK


# Read points.
# vtk_points = grid.GetPoints()
# xyz3d = vtk_to_numpy( vtk_points.GetData() )

# Read cells.
# cell_locations = grid.GetCellLocationsArray()
# cells = grid.GetCells().GetData()
# pointData = grid.GetPointData()
# numArraysInData = pointData.GetNumberOfArrays()
# for i in range(numArraysInData):
#     arr = grid.GetPointData().GetArray(i)
#     print(arr.GetName())
# von_mises = grid.GetPointData().GetArray(1)

# numPoints = grid.GetNumberOfPoints()
# avg_min_strain = np.zeros(numPoints)
        # if disp_data.get(pointId,False):
        #     print("a")
        # else:
        #     disp_data[pointId] = displacement.GetTuple(pointId)
        # avgValue += min_strain.GetValue(pointId)
        # print(grid.GetPoint(cellIds.GetId(i)))   
        # print(pointId)  
        # print("min strain: ",min_strain.GetValue(pointId))
        # print("von mises: ",von_mises.GetValue(pointId))
    # for i in range(8):
    #     pointId = cellIds.GetId(i)
        # avg_min_strain[pointId] = avgValue/8.;
        
# Create new unstrauctured grid
# output = vtk.vtkUnstructuredGridReader()
# output.SetFileName("C:\\Users\\grife\\OneDrive\\Documents\\PostDoc\\BrainModels\\Data\\Results\\template.vtk")
# output.ReadAllVectorsOn()
# output.ReadAllScalarsOn()
# output.Update()
# output_data = grid
# output_pointData = output_data.GetPointData()

# newArray = vtk.vtkFloatArray();
# newArray.SetName("averaged_min_strain")
# newArray.SetNumberOfValues(numPoints)
# for x in range(numPoints):
#     newArray.SetValue(x,avg_min_strain[x])
# output_pointData.AddArray(newArray)

# writer = vtk.vtkUnstructuredGridWriter()
# writer.SetInputData(output_data)
# outputFullFilename = inputPath + "incision_full_phere_averaged.vtk"
# writer.SetFileName(outputFullFilename)
# writer.Update()
# writer.Write()

    # print(grid.GetPointData(cellIds.GetId(i)))
# for idx in range(0,numArraysInData):
#     arr_1 = pointData.GetArray(idx)
#     print(arr_1)

# it = grid.NewCellIterator()
# it.InitTraversal()
# count = 0
# while ((not it.IsDoneWithTraversal()) and (count <100)):
#     count += 1
#     cell = vtkGenericCell()
#     it.GetCell(cell)
#     id_list = vtk.vtkIdList() 
#     print(cell.GetPointIds())
    # for i in range(8):
        # print(cell.GetPoints())
    
#     cellName = vtkCellTypes.GetClassNameFromTypeId(cell.GetCellType())
#     # print(cellName, 'NumberOfPoints:', cell.GetNumberOfPoints(), 'CellDimension:', cell.GetCellDimension())
#     # legendValues.InsertNextValue(cellName)
#     it.GoToNextCell()