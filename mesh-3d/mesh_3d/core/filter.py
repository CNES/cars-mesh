#!/usr/bin/env python
# coding: utf8
#
# Copyright (C) 2022 Chloe Thenoz (Magellium), Lisa Vo Thanh (Magellium).
#
# This file is part of mesh_3d
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Filtering methods aiming at removing outliers or groups of outliers from the point cloud.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import open3d as o3d
import laspy
from scipy.spatial import KDTree
from loguru import logger

# from cars.steps import points_cloud
from ..tools import point_cloud_handling


def radius_filtering_outliers_o3(df_pcd: pd.DataFrame, radius: float, nb_points: int,
                                 serialize: bool = False) -> pd.DataFrame:
    """
    This method removes points that have few neighbors in a given sphere around them
    For each point, it computes the number of neighbors contained in a sphere of choosen radius,
    if this number is lower than nb_point, this point is deleted

    Parameters
    ----------
    df_pcd: pd.DataFrame
        Point cloud data
    radius: float
        Defines the radius of the sphere that will be used for counting the neighbors
    nb_points: int
        Defines the minimum amount of points that the sphere should contain

    Returns
    -------
    df_pcd: pd.DataFrame
        Filtered point cloud data
    """

    if isinstance(df_pcd, pd.DataFrame):
        data = df_pcd[["x", "y", "z"]]
        data = data.to_numpy()

    # Numpy option removed
    # elif isinstance(cloud, np.ndarray):
    #     data = cloud
    #
    #     if len(data.shape) != 2:
    #         raise ValueError(f"Data dimension is incorrect. It should be 2 dimensional. "
    #                          f"Found {len(data.shape)} dimensions.")
    #     if data.shape[1] != 3:
    #         raise ValueError("Data should be expressed as points along the rows and coordinates along the columns.")

    else:
        raise TypeError(f"Cloud is of an unknown type {type(df_pcd)}. It should either be a pandas DataFrame.")

    o3d_pcd = o3d.geometry.PointCloud()
    o3d_pcd.points = o3d.utility.Vector3dVector(data)

    new_o3d_pcd, ind_valid_pts = o3d_pcd.remove_radius_outlier(nb_points, radius)
    
    # Get the point cloud filtered of the outlier points
    df_pcd = df_pcd.loc[ind_valid_pts]

    # Check if output point cloud is empty (and thus cannot suffer other processing)
    if df_pcd.empty:
        logger.error("Point cloud output by the outlier filtering step is empty.")
        raise

    ################################################################################################################
    # Serialize cloud in las
    # DEBUG
    if serialize:
        # ~ serializeDataFrameToLAS(new_cloud, "/home/data/radiuso3dpyramidedekmin_04.las")
        point_cloud_handling.serialize_point_cloud("/home/data/radiuso3dpyramidedekmin_04.las", df_pcd)
    ################################################################################################################

    return df_pcd


# def small_components_filtering_outliers_cars(cloud, radius, nb_points, serialize=True):
#     """
#     This method removes small components that have not enough points inside
#     For each point not yet processed, it computes the neighbors contained in a sphere of choosen radius, and the neighbors of neighbors ..
#     until there are none left around. Those points are considered as processed and the identified cluster is added to a list
#     For each cluster, if the number of points inside is lower than nb_point, this cluster is deleted
#
#     :param cloud: cloud point, it should be a pandas DataFrame or a numpy
#     :param radius: defines the radius of the sphere that will be used for counting the neighbors
#     :param nb_points: defines the minimm amount of points that the sphere should contain
#     :return cloud: filtered pandas dataFrame cloud
#     """
#     if not (isinstance(cloud, pd.DataFrame) or isinstance(cloud, np.ndarray)):
#         raise TypeError(f"Cloud is of an unknown type {type(cloud)}. It should either be a pandas DataFrame or a numpy "
#                         f"ndarray.")
#     pos,_ = points_cloud.small_components_filtering(cloud,radius,nb_points)
#
#     # serialize cloud in las
#     if (serialize):
#         # ~ serializeDataFrameToLAS(pos, "/home/data/radiuscarstoulouuse.las")
#         point_cloud_handling.serialize_point_cloud( "/home/data/radiuscarstoulouuse.las", pos)
#
#     return pos


# def statistical_filtering_outliers_cars(cloud, nb_neighbors, std_factor, serialize=True):
#     """
#     This methode removes points which have mean distances with their k nearest neighbors
#     that are greater than a distance threshold (dist_thresh).
#
#     This threshold is computed from the mean (mean_distances) and
#     standard deviation (stddev_distances) of all the points mean distances
#     with their k nearest neighbors:
#
#         dist_thresh = mean_distances + std_factor * stddev_distances
#
#     :param cloud: cloud point, it should be a pandas DataFrame or a numpy
#     :param nb_neighbors: number of neighbors
#     :param std_factor: multiplication factor to use to compute the distance threshold
#     :return: filtered pandas dataFrame cloud
#     """
#     if not (isinstance(cloud, pd.DataFrame) or isinstance(cloud, np.ndarray)):
#         raise TypeError(f"Cloud is of an unknown type {type(cloud)}. It should either be a pandas DataFrame or a numpy "
#                         f"ndarray.")
#
#     pos,_ = points_cloud.statistical_outliers_filtering(cloud,nb_neighbors,std_factor)
#
#     # serialize cloud in las
#     if (serialize):
#         # ~ serializeDataFrameToLAS(pos, "/home/data/statscarspyramide50_0_1.las")
#         point_cloud_handling.serialize_point_cloud( "/home/data/statscarspyramide50_0_1.las", pos)
#
#     return pos


def statistical_filtering_outliers_o3d(df_pcd: pd.DataFrame, nb_neighbors: int, std_factor: float,
                                       serialize: bool = False) -> pd.DataFrame:
    """
    This method removes points which have mean distances with their k nearest neighbors
    that are greater than a distance threshold (dist_thresh).

    This threshold is computed from the mean (mean_distances) and
    standard deviation (stddev_distances) of all the points mean distances
    with their k nearest neighbors:

        dist_thresh = mean_distances + std_factor * stddev_distances

    Parameters
    ----------
    df_pcd: pd.DataFrame
        Point cloud data
    nb_neighbors: int
        Number of neighbors
    std_factor: float
        Multiplication factor to use to compute the distance threshold

    Returns
    -------
    df_pcd: pd.DataFrame
        Filtered point cloud data
    """

    if isinstance(df_pcd, pd.DataFrame):
        data = df_pcd[["x", "y", "z"]]
        data = data.to_numpy()

    # Numpy option removed
    # elif isinstance(cloud, np.ndarray):
    #     data = cloud
    #
    #     if len(data.shape) != 2:
    #         raise ValueError(f"Data dimension is incorrect. It should be 2 dimensional. "
    #                          f"Found {len(data.shape)} dimensions.")
    #     if data.shape[1] != 3:
    #         raise ValueError("Data should be expressed as points along the rows and coordinates along the columns.")

    else:
        raise TypeError(f"Cloud is of an unknown type {type(df_pcd)}. It should either be a pandas DataFrame.")

    o3d_pcd = o3d.geometry.PointCloud()
    o3d_pcd.points = o3d.utility.Vector3dVector(data)

    new_o3d_pcd, ind_valid_pts = o3d_pcd.remove_statistical_outlier(nb_neighbors, std_ratio=std_factor)

    # Get the point cloud filtered of the outlier points
    df_pcd = df_pcd.loc[ind_valid_pts]

    # Check if output point cloud is empty (and thus cannot suffer other processing)
    if df_pcd.empty:
        logger.error("Point cloud output by the outlier filtering step is empty.")
        raise

    ################################################################################################################
    # serialize cloud in las
    # DEBUG
    if (serialize):
        # ~ serializeDataFrameToLAS(new_cloud, "/home/data/statso3dpyramide.las")
        point_cloud_handling.serialize_point_cloud("/home/data/statso3dpyramide.las", df_pcd)
    ################################################################################################################

    return df_pcd


def local_density_analysis(df_pcd: pd.DataFrame, nb_neighbors: int, serialize: bool = False):
    """
    TO COMPLETE

    Parameters
    ----------
    df_pcd: pd.DataFrame
        Point cloud data
    nb_neighbors: int
        Number of neighbors

    Returns
    -------
    df_pcd: pd.DataFrame
        Filtered point cloud data
    """

    if not isinstance(df_pcd, pd.DataFrame):
        raise TypeError(f"Cloud is of an unknown type {type(df_pcd)}. It should either be a pandas DataFrame.")

    cloud_xyz = df_pcd.loc[:, ["x", "y", "z"]].values
    cloud_tree = KDTree(cloud_xyz)
    remove_pts = []
    moy = []
    deltas = []

    for idx, _ in enumerate(cloud_xyz):
        # ~ if idx == 1:
        distances, pts = cloud_tree.query(cloud_xyz[idx], nb_neighbors)
        # ~ print(len(pts))
        # ~ print(pts)
        # ~ print(distances)
        mean_neighbors_distances = np.sum(distances) / nb_neighbors
        # ~ print(mean_neighbors_distances)
        density = (1 / nb_neighbors) * np.sum(np.exp(-distances / mean_neighbors_distances))
        # ~ print(density)
        proba = 1 - density
        # ~ print(proba)
        moy.append(proba)
        delta = 0.1 * mean_neighbors_distances
        deltas.append(delta)
        # ~ print(delta)
        if proba > 0.6:
            remove_pts.append(idx)

    # ~ print(len(cloud))
    # ~ print(len(remove_pts))
    df_pcd = df_pcd.drop(index=df_pcd.index.values[remove_pts])
    print(sum(moy)/len(moy))
    print('delta', sum(deltas)/len(deltas))
    # ~ print(len(cloud))p

    ################################################################################################################
    if (serialize):
        # ~ serializeDataFrameToLAS(cloud, "/home/data/localdensity.las")
        point_cloud_handling.serialize_point_cloud("/home/data/localdensity4.las", df_pcd)
    ################################################################################################################


# ~ def serializeDataFrameToLAS(cloud, pathout):
    # ~ """
    # ~ This method serializes a pandas DataFrame in .las
    # ~ A METTRE DANS TOOLS

    # ~ :param cloud: pandas DataFrame cloud
    # ~ :param pathout: which folder to write the file
    # ~ """
    # ~ header = laspy.LasHeader(point_format=8, version="1.4")
    # ~ print(dir(header))
    # ~ header.x_scale=1
    # ~ header.y_scale=1
    # ~ header.z_scale=1

    # ~ las = laspy.LasData(header)
    # ~ las.X = cloud["x"]
    # ~ las.Y = cloud["y"]
    # ~ las.Z = cloud["z"]
    # ~ las.red = cloud["clr0"]
    # ~ las.green = cloud["clr1"]
    # ~ las.blue = cloud["clr2"]
    # ~ las.nir = cloud["clr3"]

    # ~ las.write(pathout)
    
    
def main(df):
    xy = df[["x","y"]]
    densite = len(xy) / (xy.min()-xy.max()).prod()
    # radius and nb_points for cars method
    print(densite)
    r=5
    alpha=0.4
    kmoy = np.pi*densite*(r**2)
    print(kmoy)
    kmin=alpha*kmoy
    radius = np.sqrt(densite)
    nb_pts = densite*np.pi*((radius*3)**2)
    print(int(kmin))
    print(nb_pts)
    print(radius)

    print("tot", len(df))
    # ~ cloudo3 = radius_filtering_outliers_o3(df, 5, int(kmin))
    # ~ cloudcars = small_components_filtering_outliers_cars(df, radius, nb_pts)
    # ~ cloudcarstat = statistical_filtering_outliers_cars(df, 50, 0.1)
    # ~ cloudo3stat = statistical_filtering_outliers_o3d(df, 3, 10)
    local_density_analysis(df, 100, serialize=True)
    # ~ print(len(cloudo3))
    # ~ print(len(cloudcars))
    # ~ print(len(cloudcarstat))
    # ~ print(len(cloudo3stat))


if __name__ == "__main__":
    fileName ='/home/code/stage/pyramide-points_color.pkl'
    df = pd.read_pickle(fileName)
    main(df)
