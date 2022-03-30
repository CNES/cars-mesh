"""
Denoising methods aiming at smoothing surfaces without losing genuine high-frequency information.
"""

import multiprocessing as mp

from pathos.multiprocessing import ProcessingPool as Pool
import pandas as pd
import numpy as np
from scipy.spatial import KDTree
import open3d as o3d
from tqdm import tqdm


def compute_normal_o3d(cloud, weights=None):
    if isinstance(cloud, pd.DataFrame):
        data = cloud.loc[["x", "y", "z"]]
        data = data.to_numpy()

    elif isinstance(cloud, np.ndarray):
        data = cloud

        if len(data.shape) != 2:
            raise ValueError(f"Data dimension is incorrect. It should be 2 dimensional. "
                             f"Found {len(data.shape)} dimensions.")
        if data.shape[1] != 3:
            raise ValueError("Data should be expressed as points along the rows and coordinates along the columns.")

    else:
        raise TypeError(f"Cloud is of an unknown type {type(cloud)}. It should either be a pandas DataFrame or a numpy " 
                        f"ndarray.")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(data)

    # Compute normales
    pcd.estimate_normals(o3d.geometry.KDTreeSearchParamKNN(100), )

    return pcd.normals


def compute_point_normal(pcd, weights=None):
    """
    Compute normal with the PCA approach
    The normal to a point on the surface of an object is approximated to the normal to the tangent plane
    defined by the point and its neighbours. It becomes a least squares problem.
    See https://pcl.readthedocs.io/projects/tutorials/en/latest/normal_estimation.html

    The normal vector corresponds to the vector associated with the smallest eigen value of the neighborhood point
    covariance matrix.
    """
    if isinstance(pcd, pd.DataFrame):
        data = pcd.loc[["x", "y", "z"]]

        # Compute the centroid of the nearest neighbours
        centroid = data.mean(axis=0)

        data = data.to_numpy()

    elif isinstance(pcd, np.ndarray):
        data = pcd

        if len(data.shape) != 2:
            raise ValueError(f"Data dimension is incorrect. It should be 2 dimensional. "
                             f"Found {len(data.shape)} dimensions.")
        if data.shape[1] != 3:
            raise ValueError("Data should be expressed as points along the rows and coordinates along the columns.")

        # Compute the centroid of the nearest neighbours
        centroid = np.mean(data, axis=0)

    else:
        raise TypeError(f"Cloud is of an unknown type {type(pcd)}. It should either be a pandas DataFrame or a numpy " 
                        f"ndarray.")

    # Compute the covariance matrix
    cov_mat = np.cov(data - centroid, rowvar=False, aweights=weights)

    # Find eigen values and vectors
    # use the Singular Value Decomposition A = U * S * V^T
    u, s, vT = np.linalg.svd(cov_mat)

    # TODO: find the right orientation for the normal

    return u[:, -1]


def compute_pcd_normals(df_pcd, knn=30, weights_distance=False, weights_color=False, workers=1):
    """
    Compute the normal for each point of the cloud
    """

    # Init
    tree = KDTree(df_pcd[["x", "y", "z"]].to_numpy())

    # Query the knn for each point cloud data
    _, ind = tree.query(df_pcd[["x", "y", "z"]].to_numpy(), k=knn, workers=workers)

    weights = None
    results = []

    for row in tqdm(ind):
        results.append(compute_point_normal(tree.data[row, :], weights))

    results = np.asarray(results)

    df_pcd = df_pcd.assign(n_x=results[:, 0], n_y=results[:, 1], n_z=results[:, 2])

    return df_pcd



# def set_normal(df_cloud, normals):
#     """
#     Set normals to cloud dataframe
#     """
#     df_cloud.loc[:, ("nx", "ny", "nz")] = normals
#     return df_cloud
#
#
# def sdv_from_neighbor_array(array, nn_ind, coef=None):
#     """
#     Helper to compute normales
#     """
#     xyz = array[nn_ind]
#     centre = xyz.mean(axis=-2)
#     xyz = xyz - centre[:, None, :]
#     if coef is not None:
#         xyz *= np.sqrt(coef)
#     correlation_matrix = np.swapaxes(xyz, 1, 2) @ xyz
#     matrix_v, singular_values, matrix_vh = np.linalg.svd(correlation_matrix)
#     return matrix_v, singular_values, matrix_vh
#
#
# def normal_selective(
#     df_xyz: pd.DataFrame,
#     df_colors: pd.DataFrame,
#     sigma_c: float = 40.0,
#     sigma_d: float = 2.0,
#     k: int = 10,
#     tree=None,
# ):
#     """
#     Compute normal vectors of cloud dataframe
#     """
#     sigma_c_2 = sigma_c ** 2
#     normals = np.zeros((len(df_xyz), 3))
#
#     np_xyz = df_xyz.values
#     np_colors = df_colors.values
#
#     if tree is None:
#         tree = cKDTree(np_xyz)
#
#     nb_group = 20000
#     for i in range(0, len(df_xyz), nb_group):
#         ind = tree.data[i : i + nb_group, :]
#         _, nn_ind = tree.query(ind, k=(k ** 2))
#
#         neighbours_xyz = np_xyz[nn_ind]
#         neighbours_colors = np_colors[nn_ind]
#
#         points_xyz = neighbours_xyz[:, 0, :]
#         points_colors = neighbours_colors[:, 0, :]
#
#         delta_xyz = neighbours_xyz - points_xyz[..., None, :]
#         delta_colors = neighbours_colors - points_colors[..., None, :]
#
#         # calcul de la ponderation spatiale
#         w_total = np.exp(-(delta_xyz ** 2).sum(axis=-1) / (2 * sigma_d ** 2))
#         # calcul de la ponderation couleurs
#         w_total *= np.exp(-(delta_colors ** 2).sum(axis=-1) / (2 * sigma_c_2))
#
#         eigenvectors, _, _ = sdv_from_neighbor_array(
#             np_xyz, nn_ind, coef=w_total[..., None]
#         )
#         normals[i : i + nb_group, :] = eigenvectors[..., 2]
#     normals *= np.sign(normals[:, 2, None])
#     return normals