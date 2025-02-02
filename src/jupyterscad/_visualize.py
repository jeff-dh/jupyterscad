"""
Jupyter SCAD
Copyright (C) 2023 Jennifer Reiber Kyle

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
"""
import math

import numpy as np
import pythreejs as pjs
import stl


def visualize_stl(
    stl_file: str, width: int = 400, height: int = 400, grid_unit: float = 1
):
    """Render a visualization of a stl.

    Typical usage example:

      r = render('cube.stl')
      display(r)

    Args:
        stl_file: stl file to visualize.
        width: Visualization pixel width on page.
        height: Visualization pixel height on page.
        grid_unit: Grid cell size.

    Returns:
        Rendering to be displayed.
    """
    v = Visualizer(stl_file)
    r = v.create_renderer(
        v.create_mesh(),
        v.create_camera(),
        width=width,
        height=height,
        grid_unit=grid_unit,
    )
    return r


class Visualizer:
    def __init__(self, stl_file):
        self.stl_mesh = stl.mesh.Mesh.from_file(stl_file)

    def create_mesh(self, color: str = "#ebcc34"):
        mesh = self.stl_mesh

        vertices = pjs.BufferAttribute(array=mesh.vectors, normalized=False)

        # broadcast face normals to each face vertex
        normals = pjs.BufferAttribute(array=np.repeat(mesh.normals, 3, axis=0))

        geometry = pjs.BufferGeometry(
            attributes={"position": vertices, "normal": normals}
        )

        return pjs.Mesh(
            geometry=geometry,
            material=pjs.MeshLambertMaterial(color=color, opacity=1, transparent=True),
            position=[0, 0, 0],
        )

    def create_camera(self):
        position = (np.array([5, 5, 5]) * self.stl_mesh.max_).tolist()
        key_light = pjs.DirectionalLight(
            color="white", position=[3, 5, 1], intensity=0.7
        )
        camera = pjs.PerspectiveCamera(
            position=position, up=[0, 0, 1], children=[key_light], fov=20
        )
        return camera

    def create_renderer(self, mesh, camera, width=400, height=400, grid_unit=1):
        children = [mesh, camera, pjs.AmbientLight(color="#777777", intensity=0.5)]
        scene = pjs.Scene(children=children)

        if grid_unit:
            self.add_grid(scene, unit=grid_unit)

        self.add_axes(scene)

        renderer_obj = pjs.Renderer(
            camera=camera,
            scene=scene,
            controls=[pjs.OrbitControls(controlling=camera)],
            width=width,
            height=height,
        )
        return renderer_obj

    def add_axes(self, scene):
        # The X axis is red. The Y axis is green. The Z axis is blue.
        scene.add(pjs.AxesHelper(max(self.stl_mesh.max_ * 2)))

    def add_grid(self, scene, unit=1):
        mesh = self.stl_mesh
        min_ = np.minimum(np.floor(mesh.min_), np.array([0, 0, 0]))
        max_ = np.maximum(np.ceil(mesh.max_), np.array([0, 0, 0]))
        extent = max_ - min_
        grid_extent = extent.max()

        grid_pos = (
            grid_extent / 2 + min_[0],
            grid_extent / 2 + min_[1],
            grid_extent / 2 + min_[2],
        )

        # X/Z plane
        gh = pjs.GridHelper(
            grid_extent + 2 * unit,
            (grid_extent + 2 * unit) / unit,
            colorCenterLine="blue",
            colorGrid="blue",
        )
        gh.position = (grid_pos[0], 0, grid_pos[2])
        scene.add(gh)

        # X/Y plane
        gh = pjs.GridHelper(
            grid_extent + 2 * unit,
            (grid_extent + 2 * unit) / unit,
            colorCenterLine="red",
            colorGrid="red",
        )
        gh.rotateX(math.pi / 2)
        gh.position = (grid_pos[0], grid_pos[1], 0)
        scene.add(gh)

        # Y/Z plane
        gh = pjs.GridHelper(
            grid_extent + 2 * unit,
            (grid_extent + 2 * unit) / unit,
            colorCenterLine="green",
            colorGrid="green",
        )
        gh.rotateZ(math.pi / 2)
        gh.position = (0, grid_pos[1], grid_pos[2])
        scene.add(gh)
