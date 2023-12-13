import numpy as np
from point_cloud import PointCloud
from scipy.spatial import Delaunay
from scipy import ndimage


def in_hull(p, hull):
    """
    Test if points in `p` are in `hull`

    `p` should be a `NxK` coordinates of `N` points in `K` dimensions
    `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the 
    coordinates of `M` points in `K`dimensions for which Delaunay triangulation
    will be computed
    """
    if not isinstance(hull, Delaunay):
        hull = Delaunay(hull)

    return hull.find_simplex(p) >= 0


class CSFFunctions:

    @staticmethod
    def add_full_csf(data, layers=1):

        current_dimensions = data.shape
        new_data = np.zeros(current_dimensions, int)

        xs, ys, zs = np.where(data == 3)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 3

        xs, ys, zs = np.where(data == 2)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 3

        xs, ys, zs = np.where(data == 25)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 3

        xs, ys, zs = np.where(data == 57)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 3

        # Create point cloud
        point_cloud = PointCloud.PointCloud()
        pc = point_cloud.create_point_cloud_from_voxel(new_data)

        xmin_tot, ymin_tot, zmin_tot = [int(p) for p in np.min(pc[:, :3], axis=0)]
        xmax_tot, ymax_tot, zmax_tot = [int(p) for p in np.max(pc[:, :3], axis=0)]

        # ymax_tot = 70

        print("Filling in CSF coronal plane")
        for z in range(zmin_tot, zmax_tot + 1):
            points = point_cloud.get_slice(2, z)
            points = points[:, :2]
            hull = Delaunay(points)

            xmin, ymin = np.min(points, axis=0)
            xmax, ymax_slice = np.max(points, axis=0)
            ymax = min([ymax_tot, ymax_slice])
            mid_y = int((int(ymin) + int(ymax + 1)) / 2)
            for x in range(int(xmin), int(xmax + 1)):
                for y in range(int(ymin), int(ymax + 1)):
                    if data[x, y, z] == 0 and (y < ymax_tot):
                        if in_hull([x, y], hull):
                            point_cloud.add_point_to_cloud([x, y, z, 24])
                            data[x, y, z] = 24
                            new_data[x, y, z] = 24

        ##### CSF is not filled for the sagital plane of the brain
        # print("Filling in CSF x-dim")
        # for x in range(xmin_tot, xmax_tot + 1):
        #     points = point_cloud.get_slice(0, x)
        #     points = points[:, 1:3]
        #     hull = Delaunay(points)
        #
        #     min1d, min2d = np.min(points, axis=0)
        #     max1d_slice, max2d = np.max(points, axis=0)
        #     max1d = min([ymax_tot, max1d_slice])
        #     mid_2d = int((int(min2d) + int(max2d + 1)) / 2)
        #     for y in range(int(min1d), int(max1d + 1)):
        #         for z in range(int(min2d), int(max2d + 1)):
        #             if (data[x, y, z] == 0) and (y < ymax_tot):
        #                 if in_hull([y, z], hull):
        #                     point_cloud.add_point_to_cloud([x, y, z, 24])
        #                     data[x, y, z] = 24
        #                     new_data[x, y, z] = 24

        print("Filling in CSF transverse plane")
        for y in range(ymin_tot, ymax_tot + 1):
            points = point_cloud.get_slice(1, y)
            points = points[:, [0, 2]]
            hull = Delaunay(points)

            min1d, min2d = np.min(points, axis=0)
            max1d, max2d = np.max(points, axis=0)
            mid_2d = int((int(min2d) + int(max2d + 1)) / 2)
            for x in range(int(min1d), int(max1d + 1)):
                for z in range(int(min2d), int(max2d + 1)):
                    if (data[x, y, z] == 0) and (y < ymax_tot):
                        if in_hull([x, z], hull):
                            point_cloud.add_point_to_cloud([x, y, z, 24])
                            data[x, y, z] = 24
                            new_data[x, y, z] = 24

        # if full:
        #     xs,ys,zs = np.where(data == 57)
        #     for [x,y,z] in np.column_stack((xs,ys,zs)):
        #         newData[x,y,z] = 3

        inflated_csf = ndimage.binary_dilation(data).astype(int)
        for i in range(layers - 1):
            inflated_csf = ndimage.binary_dilation(inflated_csf).astype(int)

        xs, ys, zs = np.where(inflated_csf == 1)
        current_dimensions = inflated_csf.shape
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            if data[x, y, z] == 0:
                data[x, y, z] = 24

    @staticmethod
    def add_partial_csf(data, layers=1):

        current_dimensions = data.shape
        new_data = np.zeros(current_dimensions, int)

        xs, ys, zs = np.where(data == 3)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 24

        xs, ys, zs = np.where(data == 2)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 24

        xs, ys, zs = np.where(data == 25)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 24

        xs, ys, zs = np.where(data == 57)
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            new_data[x, y, z] = 24

        # xs, ys, zs = np.where(new_data == 1)
        # current_dimensions = new_data.shape
        # for [x, y, z] in np.column_stack((xs, ys, zs)):
        #     if new_data[x, y, z] == 0:
        #         new_data[x, y, z] = 24

                # Create point cloud
        point_cloud = PointCloud.PointCloud()
        pc = point_cloud.create_point_cloud_from_voxel(new_data)

        xmin_tot, ymin_tot, zmin_tot = [int(p) for p in np.min(pc[:, :3], axis=0)]
        xmax_tot, ymax_tot, zmax_tot = [int(p) for p in np.max(pc[:, :3], axis=0)]

        print("Filling in CSF coronal plane")
        for z in range(zmin_tot, zmax_tot + 1):
            points = point_cloud.get_slice(2, z)
            points = points[:, :2]
            hull = Delaunay(points)

            xmin, ymin = np.min(points, axis=0)
            xmax, ymax_slice = np.max(points, axis=0)
            ymax = min([ymax_tot, ymax_slice])
            mid_y = int((int(ymin) + int(ymax + 1)) / 2)
            for x in range(int(xmin), int(xmax + 1)):
                for y in range(int(ymin), int(ymax + 1)):
                    if (data[x, y, z] == 0) and (y < ymax_tot):
                        if in_hull([x, y], hull):
                            new_data[x, y, z] = 24

        ##### CSF is not filled for the sagital plane of the brain
        # print("Filling in CSF x-dim")
        # for x in range(xmin_tot, xmax_tot + 1):
        #     points = point_cloud.get_slice(0, x)
        #     points = points[:, 1:3]
        #     hull = Delaunay(points)
        #
        #     min1d, min2d = np.min(points, axis=0)
        #     max1d_slice, max2d = np.max(points, axis=0)
        #     max1d = min([ymax_tot, max1d_slice])
        #     mid_2d = int((int(min2d) + int(max2d + 1)) / 2)
        #     for y in range(int(min1d), int(max1d + 1)):
        #         for z in range(int(min2d), int(max2d + 1)):
        #             if (data[x, y, z] == 0) and (y < ymax_tot):
        #                 if in_hull([y, z], hull):
        #                     new_data[x, y, z] = 24

        print("Filling in CSF trasverse plane")
        for y in range(ymin_tot, ymax_tot + 1):
            points = point_cloud.get_slice(1, y)
            points = points[:, [0, 2]]
            hull = Delaunay(points)

            min1d, min2d = np.min(points, axis=0)
            max1d, max2d = np.max(points, axis=0)
            mid_2d = int((int(min2d) + int(max2d + 1)) / 2)
            for x in range(int(min1d), int(max1d + 1)):
                for z in range(int(min2d), int(max2d + 1)):
                    if (data[x, y, z] == 0) and (y < ymax_tot):
                        if in_hull([x, z], hull):
                            new_data[x, y, z] = 24

        new_data = ndimage.binary_erosion(new_data).astype(int)
        # for i in range(1):
        #     new_data = ndimage.binary_erosion(new_data).astype(int)

        xs, ys, zs = np.where(new_data == 1)
        current_dimensions = new_data.shape
        for [x, y, z] in np.column_stack((xs, ys, zs)):
            if data[x, y, z] == 0:
                data[x, y, z] = 24

    @staticmethod
    def get_csf_function(csf_type):
        if csf_type == "full":
            return CSFFunctions.add_full_csf
        elif csf_type == "partial":
            return CSFFunctions.add_partial_csf
        else:
            return None
