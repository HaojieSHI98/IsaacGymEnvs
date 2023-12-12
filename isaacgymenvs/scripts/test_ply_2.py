import pyvista as pv

# coordinates of enclosing polygon
poly_points = [
    # (-0.025,-0.025),(0.025,-0.025),(0.025,0.025),(-0.025,0.025)
    # (-0.05,-0.01),(0.15,-0.01),(0.15,0.19),(0.13,0.19),(0.13,0.01),(-0.05,0.01) #hook
    (0,0.025),(0.68,0.025),(0.68,-0.055),(0.73,-0.055),(0.73,-0.025),(0.7,-0.025),(0.7,0.075),(0.73,0.075),(0.73,0.125),(0.68,0.125),(0.68,0.05),(0,0.05) #coat_hanger
    # (0.015,0.15),(0.115,0.15),(0.115,0.18),(-0.015,0.18),(-0.015,-0.18),(0.115,-0.18),(0.115,-0.15),(0.015,-0.15)
]

# z0, z1 = 0.0, 0.05
z0,z1 = -0.02,0.02

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
holey_solid.save('stick_example2.ply')
holey_solid.plot()
# import pyvista as pv
pl = pv.Plotter()
_ = pl.add_mesh(holey_solid)
# pl.export_obj('coat_hanger.obj') 
# pl.save_graphic('hook.svg')