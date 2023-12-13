# -*- coding: utf-8 -*-
"""
Created on Wed May 24 09:31:31 2023

@author: grife
"""
from voxel_data.void_filler.Vertex import Vertex
from voxel_data.GridBox import GridBox
from collections import deque
import numpy as np

class Maze_Solver():
    
    def __init__(self, maze):
        self.maze = maze;
        self.data = maze.grid;
        self.verticies = {};    
    
    
    def fill_voids(self,locations):
        # Cycle through void points, create 3-3 structures and calculate number non-zero entries
        # Processes i decreasing by num non-zero entries and replace void with mode of structure values
        print("Filling in found voids in the data")
        self.location_to_box = {}  
        num_non_zeros_to_boxes = {}
        for n in range(28):
            num_non_zeros_to_boxes[n] = []
        for location in locations:
            location_int = [int(d) for d in location.split(Vertex.splitter)]
            box = GridBox(self.data, location_int)
            num_non_zeros = box.get_number_non_zeros()
            self.location_to_box[box.get_location_key()] = box
            if num_non_zeros == 26:
                self.update_grid_boxes(box)
            else:
                num_non_zeros_to_boxes[num_non_zeros].append(box)
        for boxes in num_non_zeros_to_boxes.values():
            for b in boxes:
                self.update_grid_boxes(b)
        # return self.data
            
        
    def update_grid_boxes(self,box):
        mode_value = box.mode()
        [x,y,z] = box.location
        key = box.get_location_key()
        self.data[x,y,z] = mode_value
        bounds = box.bounds
        for x in range(bounds[0],bounds[1]):
            for y in range(bounds[2],bounds[3]):
                for z in range(bounds[4],bounds[5]):
                    affected_location = GridBox.create_location_key([x,y,z])
                    if affected_location != key:
                        if (self.location_to_box.get(affected_location,False)):
                            # print("Box affected by " + key + " found at " + affected_location)
                            box_affected = self.location_to_box[affected_location];
                            box_affected.create_box_from_grid(self.data,[x,y,z]);  
        self.location_to_box.pop(key)
           
    
    def find_voids(self):
        print("Finding voids in the data")
        current_data = self.data
        current_dimensions = self.data.shape
        num_points = 0;
        self.openPoints = {}
        self.enclosedPoints = {}
        for x in range(1,current_dimensions[0]-1):
            if (np.sum(current_data[x,:,:]) > 0):
                for y in range(1,current_dimensions[1]-1):
                    if (np.sum(current_data[x,y,:]) > 0):
                        for z in range(1,current_dimensions[2]-1):
                            if (current_data[x,y,z] == 0):
                                    if not (self.maze.isExit(x,y,z)):   # Checking these point are obviously open points i.e. a line of zeros on the boundary or something similar
                                        num_points += 1;
                                        vertexKey = Vertex.create_a_key(x,y,z);
                                        if not (self.openPoints.get(vertexKey,False) or self.enclosedPoints.get(vertexKey,False)): # Check it hasn't already been checked
                                                                                        
                                            isEnclosedPoint = self.breath_first_search([x,y,z]);
                                            
                                            if (isEnclosedPoint):
                                                pointsInEnclosure = self.visited.keys();
                                                for point in pointsInEnclosure:
                                                    self.enclosedPoints[point] = point
                                            elif not isEnclosedPoint:
                                                pointsNotEnclosed = self.visited.keys();
                                                for point in pointsNotEnclosed:
                                                    self.openPoints[point] = point
                                                
                                                
        print("Total number of points queried")
        print(num_points)
        print("enclosedPoints")
        print(len(self.enclosedPoints.keys()))
        print("number of openPoints")
        print(len(self.openPoints))
        return self.enclosedPoints
        
    
    def add_new_vertex(self, x,y,z):
        newVert = Vertex(x,y,z)
        self.verticies[newVert.key] = newVert
        return newVert
    
    def add_connection(self, vert1, vert2):
        vertA = self.verticies[vert1.key]    
        vertB = self.verticies[vert2.key]
        
        vertA.addNeighbour(vertB)
        vertB.addNeighbour(vertA)
    
    def add_neighbours(self, currentVertex: Vertex):
        [x,y,z] = currentVertex.get_location();
        neighbours = self.maze.find_zero_neighbours(x,y,z);
        for v in neighbours:
            if (self.verticies.get(v.key,False)):
                v = self.verticies[v.key]
            else:
                self.verticies[v.key] = v
            currentVertex.addNeighbour(v)
            self.add_connection(currentVertex, v);
    
    def breath_first_search(self,start):
        end = self.maze.get_end_point(start[0], start[1], start[2]);
        self.visited = {};
        q = deque();
        
        startVertex = self.add_new_vertex(start[0], start[1], start[2])
        self.add_neighbours(startVertex);
        
        endVertex = self.add_new_vertex(end[0], end[1], end[2])
        self.add_neighbours(endVertex);
        
        self.visited[startVertex.key] = startVertex
        
        currentVertex = startVertex
        loop_count = 0
        while (not (currentVertex.isEqual(endVertex))) and loop_count<8000:
            loop_count += 1
            [x,y,z] = currentVertex.get_location();
            vertexKey = currentVertex.key;
            if (self.openPoints.get(vertexKey,False)):
                return False;
            elif (self.enclosedPoints.get(vertexKey,False)):
                return True;
            elif not (self.maze.isExit(x,y,z)):
                neighbours = currentVertex.adjacentNodes;
                for neighbourKey,neighbourVertex in neighbours.items():
                    if not (self.visited.get(neighbourKey,False)):
                        self.add_neighbours(neighbourVertex);
                        self.visited[neighbourKey] = neighbourVertex
                        q.append(neighbourVertex)
                
                if (len(q)<1):
                    return True;
                currentVertex = q.popleft();
            else:
                neighbours = currentVertex.adjacentNodes;
                for neighbourKey,neighbourVertex in neighbours.items():
                    if not (self.visited.get(neighbourKey,False)):
                        self.visited[neighbourKey] = neighbourVertex
                return False;
        print("Error")
        print("currentVertex.isEqual(endVertex)" + ": " + str(currentVertex.isEqual(endVertex)))
        print("loop_count" + ": " + str(loop_count))
        return False
                
                
                
                
                
                
                
                
                
                
                
                
                
        
        