import pyvista as pv

# coordinates of enclosing polygon
poly_points = [
    (0,0),(0.2,0),(0.2,0.2),(0.16,0.2),(0.16,0.04),(0,0.04)
    # (0,0.025),(0.65,0.025),(0.65,-0.1),(0.7,-0.1),(0.7,-0.15),(0.85,-0.15),(0.85,-0.05),(0.7,-0.05),(0.7,0.15),(0.85,0.15),(0.85,0.25),(0.7,0.25),(0.7,0.2),(0.65,0.2),(0.65,0.075),(0,0.075)
]

z0, z1 = 0.0, 0.05

def points_2d_to_poly(points, z):
    """Convert a sequence of 2d coordinates to a polydata with a polygon."""
    faces = [len(points), *range(len(points))]
    poly = pv.PolyData([p + (z,) for p in points], faces=faces)
    return poly

# bounding polygon
polygon = points_2d_to_poly(poly_points, z0)
polygon.plot()
# triangulate poly with all three subpolygons supplying edges
# (relative face orientation is critical here)
polygon_with_holes = polygon.delaunay_2d(edge_source=polygon)
polygon_with_holes.plot()
# extrude
holey_solid = polygon_with_holes.extrude((0, 0, z1 - z0), capping=True)
holey_solid.plot()
# import pyvista as pv
pl = pv.Plotter()
_ = pl.add_mesh(holey_solid)
pl.export_obj('hook.obj') 
pl.save_graphic('hook.svg')