#!/usr/bin/env python
# coding: utf8
#
# Copyright (C) 2022 CNES.
#
# This file is part of mesh3d
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
Define classes for handling common objects
"""

from typing import Union

import numpy as np
import open3d as o3d
import pandas as pd
from loguru import logger

COLORS = ["red", "green", "blue", "nir"]
NORMALS = ["n_x", "n_y", "n_z"]
UVS = ["uv1_row", "uv1_col", "uv2_row", "uv2_col", "uv3_row", "uv3_col"]


class PointCloud(object):
    """Point cloud data"""

    def __init__(
        self,
        df: Union[None, pd.DataFrame] = None,
        o3d_pcd: Union[None, o3d.geometry.PointCloud] = None,
    ) -> None:

        if (not isinstance(df, pd.DataFrame)) and (df is not None):
            raise TypeError(
                f"Input point cloud data 'df' should either be None or a pd.DataFrame. Here found "
                f"'{type(df)}'."
            )

        if (not isinstance(o3d_pcd, o3d.geometry.PointCloud)) and (
            o3d_pcd is not None
        ):
            raise TypeError(
                f"Input open3d point cloud data 'o3d_pcd' should either be None or a "
                f"o3d.geometry.PointCloud. Here found '{type(o3d_pcd)}'."
            )

        self.df = df
        self.o3d_pcd = o3d_pcd

    def set_df_from_o3d_pcd(self):
        """Set pandas.DataFrame from open3D PointCloud"""
        if self.o3d_pcd is None:
            raise ValueError(
                "Could not set df from open3d pcd because it is empty."
            )

        # Set point cloud data
        self.set_df_from_vertices(np.asarray(self.o3d_pcd.vertices))
        # Add attributes if available
        if self.o3d_pcd.has_colors():
            self.set_df_colors(
                colors=np.asarray(self.o3d_pcd.colors),
                color_names=["red", "green", "blue"],
            )
        if self.o3d_pcd.has_normals():
            self.set_df_normals(np.asarray(self.o3d_pcd.normals))
        # TODO: Open3D has no classification attribute: need to do a research in the df pcd to bring them back? the
        #  point order might be different

    def set_df_from_vertices(self, vertices: np.ndarray) -> None:
        """Set point coordinates in the pandas DataFrame"""
        self.df = pd.DataFrame(
            data=np.asarray(vertices, dtype=np.float64), columns=["x", "y", "z"]
        )

    def set_df_colors(self, colors: np.ndarray, color_names: list) -> None:
        """Set color attributes per point in the pandas DataFrame"""
        colors = np.asarray(colors)

        for c in color_names:
            if c not in COLORS:
                raise ValueError(
                    f"{c} is not a possible color. Should be in {COLORS}."
                )

        if colors.shape[1] != len(color_names):
            raise ValueError(
                f"The number of columns ({colors.shape[1]}) is not equal to the number "
                f"of column names ({len(color_names)})."
            )

        self.df[color_names] = colors

    def set_df_normals(self, normals: np.ndarray) -> None:
        """Set normal attributes per point in the pandas DataFrame"""
        normals = np.asarray(normals)

        if normals.shape[1] != 3:
            raise ValueError(
                f"Normals should have three columns (x, y, z). Found ({normals.shape[1]})."
            )

        self.df[NORMALS] = normals

    def set_o3d_pcd_from_df(self):
        """Set open3d PointCloud from pandas.DataFrame"""
        self.o3d_pcd = o3d.geometry.PointCloud(
            points=o3d.utility.Vector3dVector(
                self.df[["x", "y", "z"]].to_numpy()
            )
        )

        if self.has_colors:
            self.set_o3d_colors()
        if self.has_normals:
            self.set_o3d_normals()

    def set_o3d_colors(self) -> None:
        """Set color attribute of open3D PointCloud"""

        # Check o3d point cloud is initialized
        if self.o3d_pcd is None:
            raise ValueError("Open3D Point Cloud is empty.")

        # add colors if applicable (only RGB)
        # init to zero
        colors_arr = np.zeros_like(
            self.df[["x", "y", "z"]].to_numpy(), dtype=np.float64
        )
        # retrieve information from the dataframe
        for k, c in enumerate(["red", "green", "blue"]):
            if c in self.df:
                colors_arr[:, k] = self.df[c].to_numpy()
            else:
                raise ValueError(
                    f"Open3D only deals with RGB colors. Here '{c}' is missing."
                )
        # normalize colours in [0, 1]
        colors_arr = np.divide(
            colors_arr - colors_arr.min(),
            colors_arr.max() - colors_arr.min(),
            out=np.zeros_like(colors_arr),
            where=(colors_arr.max() - colors_arr.min()) != 0.0,
        )
        # add to opend3d point cloud
        self.o3d_pcd.colors = o3d.utility.Vector3dVector(colors_arr)

    def set_o3d_normals(self) -> None:
        """Set normal attribute of open3D PointCloud"""

        # Check o3d point cloud is initialized
        if self.o3d_pcd is None:
            raise ValueError("Open3D Point Cloud is empty.")

        self.o3d_pcd.normals = o3d.utility.Vector3dVector(
            self.df[NORMALS].to_numpy()
        )

    def get_vertices(self) -> pd.DataFrame:
        """Get vertex data"""
        return self.df[["x", "y", "z"]]

    def get_colors(self) -> pd.DataFrame:
        """Get color data"""
        if not self.has_colors:
            raise ValueError("Point cloud has no color.")
        return self.df[[c for c in COLORS if c in self.df.head()]]

    def get_normals(self) -> pd.DataFrame:
        """Get normals"""
        if not self.has_normals:
            raise ValueError("Point cloud has no normals.")
        return self.df[NORMALS]

    @property
    def has_colors(self) -> bool:
        if self.df is None:
            raise ValueError("Point cloud (pandas DataFrame) is not assigned.")
        else:
            return any([c in self.df.head() for c in COLORS])

    @property
    def has_normals(self) -> bool:
        if self.df is None:
            raise ValueError("Point cloud (pandas DataFrame) is not assigned.")
        else:
            return all([n in self.df.head() for n in NORMALS])

    @property
    def has_classes(self) -> bool:
        if self.df is None:
            raise ValueError("Point cloud (pandas DataFrame) is not assigned.")
        else:
            return "classification" in self.df.head()

    def serialize(self, filepath: str, **kwargs) -> None:
        """Serialize point cloud"""
        from .point_cloud_io import serialize_point_cloud

        serialize_point_cloud(filepath, self.df, **kwargs)

    def deserialize(self, filepath: str) -> None:
        """Deserialize point cloud"""
        from .point_cloud_io import deserialize_point_cloud

        self.df = deserialize_point_cloud(filepath)


class Mesh(object):
    """Mesh data"""

    def __init__(
        self,
        pcd: Union[None, pd.DataFrame] = None,
        mesh: Union[None, pd.DataFrame] = None,
        o3d_pcd: Union[None, o3d.geometry.PointCloud] = None,
        o3d_mesh: Union[None, o3d.geometry.TriangleMesh] = None,
    ):

        self.pcd = PointCloud(df=pcd, o3d_pcd=o3d_pcd)
        self.df = mesh

        self.o3d_mesh = o3d_mesh

        # image texture
        self.image_texture_path = None

    def set_df_from_o3d_mesh(self) -> None:
        if self.o3d_mesh is None:
            raise ValueError(
                "Could not set df from open3d mesh because it is empty."
            )

        # Set face indexes
        self.set_df_from_vertices(np.asarray(self.o3d_mesh.triangles))

        # Set point cloud data
        self.pcd.set_df_from_vertices(np.asarray(self.o3d_mesh.vertices))

        # Add attributes if available
        # Mesh
        if self.o3d_mesh.has_textures():
            if self.image_texture_path is None:
                logger.warning(
                    f"No image texture path is given to the Mesh object. Texture will remain incomplete."
                )

        if self.o3d_mesh.has_triangle_uvs():
            self.set_df_uvs(
                uvs=np.asarray(self.o3d_mesh.triangle_uvs).reshape((-1, 6))
            )

        # Point Cloud
        if self.o3d_mesh.has_vertex_colors():
            self.pcd.set_df_colors(
                colors=np.asarray(self.o3d_mesh.vertex_colors),
                color_names=["red", "green", "blue"],
            )
        if self.o3d_mesh.has_vertex_normals():
            self.pcd.set_df_normals(np.asarray(self.o3d_mesh.vertex_normals))
        # TODO: Open3D has no classification attribute: need to do a research in the df pcd to bring them back? the
        #  point order might be different

    def set_df_from_vertices(self, vertices) -> None:
        self.df = pd.DataFrame(data=vertices, columns=["p1", "p2", "p3"])

    def set_image_texture_path(self, image_texture_path) -> None:
        self.image_texture_path = image_texture_path

    def set_df_uvs(self, uvs) -> None:
        """
        UVs

        Parameters
        ----------
        uvs: (N, 6) np.ndarray or list
            Image texture (row, col) normalized coordinates per triangle vertex
        """
        uvs = np.asarray(uvs)

        # Check characteristics
        if uvs.shape[0] != self.df.shape[0]:
            raise ValueError(
                f"Inconsistent number of triangles between triangle vertex indexes ({self.df.shape[0]} "
                f"triangles) and uvs ({uvs.shape[0]} data)."
            )
        if uvs.shape[1] != 6:
            raise ValueError(
                f"UVs should be a numpy ndarray or a list of list with exactly 6 columns (3 vertices "
                f"associated to a pair of image texture coordinates (row, col). "
                f"Here found {uvs.shape[1]}."
            )

        self.df[UVS] = uvs

    def set_o3d_mesh_from_df(self) -> None:
        if self.df is None:
            raise ValueError(
                "Could not set open3d mesh from df mesh because it is empty."
            )
        if self.pcd.df is None:
            raise ValueError(
                "Could not set open3d mesh from df pcd because it is empty."
            )

        self.o3d_mesh = o3d.geometry.TriangleMesh(
            vertices=o3d.utility.Vector3dVector(
                self.pcd.df[["x", "y", "z"]].to_numpy()
            ),
            triangles=o3d.utility.Vector3iVector(
                self.df[["p1", "p2", "p3"]].to_numpy()
            ),
        )
        # Add attributes if available
        # Mesh
        if self.has_texture:
            self.set_o3d_image_texture_and_uvs()
        # Point cloud
        if self.pcd.has_colors:
            self.set_o3d_vertex_colors()
        if self.pcd.has_normals:
            self.set_o3d_vertex_normals()

        # TODO: Open3D has no classification attribute: need to do a research in the df pcd to bring them back? the
        #  point order might be different

    def set_o3d_vertex_colors(self) -> None:
        """Set color attribute of open3D TriangleMesh"""

        # Check o3d mesh is initialized
        if self.o3d_mesh is None:
            raise ValueError(
                "Could not set df from open3d mesh because it is empty."
            )

        # add colors if applicable (only RGB)
        # init to zero
        colors_arr = np.zeros_like(
            self.pcd.df[["x", "y", "z"]].to_numpy(), dtype=np.float64
        )
        # retrieve information from the dataframe
        for k, c in enumerate(["red", "green", "blue"]):
            if c in self.pcd.df:
                colors_arr[:, k] = self.pcd.df[c].to_numpy()
            else:
                raise ValueError(
                    f"Open3D only deals with RGB colors. Here '{c}' is missing."
                )
        # normalize colours in [0, 1]
        colors_arr = np.divide(
            colors_arr - colors_arr.min(),
            colors_arr.max() - colors_arr.min(),
            out=np.zeros_like(colors_arr),
            where=(colors_arr.max() - colors_arr.min()) != 0.0,
        )
        # add to opend3d mesh
        self.o3d_mesh.vertex_colors = o3d.utility.Vector3dVector(colors_arr)

    def set_o3d_vertex_normals(self) -> None:
        """Set normal attribute of open3D TriangleMesh"""

        # Check o3d mesh is initialized
        if self.o3d_mesh is None:
            raise ValueError(
                "Could not set df from open3d mesh because it is empty."
            )

        self.o3d_mesh.vertex_normals = o3d.utility.Vector3dVector(
            self.pcd.df[NORMALS].to_numpy()
        )

    def set_o3d_image_texture_and_uvs(self) -> None:
        """Set image texture path and uvs of open3D TriangleMesh"""

        # Check o3d mesh is initialized
        if self.o3d_mesh is None:
            raise ValueError(
                "Could not set df from open3d mesh because it is empty."
            )

        if not self.has_texture:
            raise ValueError(
                f"Mesh object has no texture (either the image texture path or the uvs are missing."
            )

        # UVs in open3d are expressed as a (3 * num_triangles, 2)
        # Reshape data before feeding open3d TriangleMesh
        uvs = self.df[UVS].to_numpy()
        uvs = uvs.reshape((-1, 2))
        self.o3d_mesh.triangle_uvs = o3d.utility.Vector2dVector(uvs)

        # Add image texture path
        self.o3d_mesh.textures = [o3d.io.read_image(self.image_texture_path)]

    def get_triangles(self) -> pd.DataFrame:
        return self.df[["p1", "p2", "p3"]]

    def get_triangle_uvs(self) -> pd.DataFrame:
        if not self.has_triangle_uvs:
            raise ValueError("Mesh has no triangle uvs.")
        else:
            return self.df[UVS]

    def get_image_texture_path(self) -> str:
        if self.image_texture_path is None:
            raise ValueError("Mesh has no image texture path defined.")
        else:
            return self.image_texture_path

    @property
    def has_triangles(self) -> bool:
        if self.df is None:
            raise ValueError("Mesh (pandas DataFrame) is not assigned.")
        else:
            return all([n in self.df.head() for n in ["p1", "p2", "p3"]]) and not self.df.empty

    @property
    def has_texture(self) -> bool:
        if self.df is None:
            raise ValueError("Mesh (pandas DataFrame) is not assigned.")
        else:
            return (self.image_texture_path is not None) and all(
                [
                    el in self.df.head()
                    for el in [
                        "uv1_row",
                        "uv1_col",
                        "uv2_row",
                        "uv2_col",
                        "uv3_row",
                        "uv3_col",
                    ]
                ]
            ) and not self.df.empty

    @property
    def has_triangle_uvs(self) -> bool:
        if self.df is None:
            raise ValueError("Mesh (pandas DataFrame) is not assigned.")
        else:
            return all(
                [
                    el in self.df.head()
                    for el in [
                        "uv1_row",
                        "uv1_col",
                        "uv2_row",
                        "uv2_col",
                        "uv3_row",
                        "uv3_col",
                    ]
                ]
            ) and not self.df.empty

    @property
    def has_normals(self) -> bool:
        if self.df is None:
            raise ValueError("Mesh (pandas DataFrame) is not assigned.")
        else:
            return all([n in self.df.head() for n in NORMALS]) and not self.df.empty

    @property
    def has_classes(self) -> bool:
        if self.df is None:
            raise ValueError("Mesh (pandas DataFrame) is not assigned.")
        else:
            return "classification" in self.df.head() and not self.df.empty

    def serialize(self, filepath: str, **kwargs) -> None:
        """Serialize mesh"""
        from .mesh_io import serialize_mesh

        serialize_mesh(filepath, self, **kwargs)

    def deserialize(self, filepath: str) -> None:
        """Deserialize mesh"""
        from .mesh_io import deserialize_mesh

        self.pcd.df, self.df = deserialize_mesh(filepath)
