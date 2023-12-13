# -*- coding: utf-8 -*-
"""
Created on Wed May 24 14:02:00 2023

@author: grife
"""
import numpy as np
import pyvista as pv


class PointCloud:

    def create_point_cloud_from_voxel(self, data):
        current_data = data
        current_dimensions = current_data.shape
        pointCloudData = np.zeros((np.prod(current_dimensions), 4))
        count = 0
        for x in range(current_dimensions[0]):
            if np.sum(current_data[x, :, :]) > 0:
                for y in range(current_dimensions[1]):
                    if np.sum(current_data[x, y, :]) > 0:
                        for z in range(current_dimensions[2]):
                            if current_data[x, y, z] != 0:
                                pointCloudData[count, :] = [x, y, z, current_data[
                                    x, y, z]]  # co-ordinate data and material type (used in colouring point_cloud)
                                count += 1
        self.pcd = pointCloudData[0:count, :]
        return self.pcd

    def create_point_cloud_from_mesh(self, elements, nodes):
        pointCloudData = np.zeros((len(elements) + 1, 4))
        for e in elements.items():
            m = e.properties['mat'][0]
            ica = e.ica
            [x, y, z] = e.calculate_element_centroid(ica, nodes)
            pointCloudData[e.num, :] = [x, y, z, m]
        self.pcd = pointCloudData
        return self.pcd

    def view_point_cloud(self, *args, **kwargs):
        if len(args) > 0:
            pointCloudData = args[0]
        else:
            if hasattr(self, "pcd"):
                pointCloudData = self.pcd
            else:
                print("No point cloud data has been created")
                return -1
        point_cloud = pv.PolyData(pointCloudData[:, 0:3])
        point_cloud["material_type"] = pointCloudData[:, 3:]
        point_cloud.plot(eye_dome_lighting=True)
        return 0

    def add_point_to_cloud(self, p):
        self.pcd = np.append(self.pcd, [p], axis=0)

    def view_slice(self, axis, location):
        if (location > 1) and (axis < self.pcd.shape[1]):
            arr = self.pcd[:, axis]
            if location <= max(arr):
                indices, = np.where(location == arr)
                points = self.pcd[indices, :]
                point_cloud = pv.PolyData(points[:, 0:3])
                point_cloud["material_type"] = points[:, 3:]
                point_cloud.plot(render_points_as_spheres=True)

    def get_slice(self, axis, location):
        points = None
        if (location > 1) and (axis < self.pcd.shape[1]):
            arr = self.pcd[:, axis]
            if (location <= max(arr)):
                indices, = np.where(location == arr)
                points = self.pcd[indices, :]
        return points
