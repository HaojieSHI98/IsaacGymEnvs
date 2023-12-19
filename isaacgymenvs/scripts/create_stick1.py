import pyvista as pv
import math
# coordinates of enclosing polygon
# poly_points = [
#     # (-0.025,-0.025),(0.025,-0.025),(0.025,0.025),(-0.025,0.025)
#     # (-0.05,-0.01),(0.15,-0.01),(0.15,0.19),(0.13,0.19),(0.13,0.01),(-0.05,0.01) #hook
#     (0,0.025),(0.68,0.025),(0.68,-0.055),(0.73,-0.055),(0.73,-0.025),(0.7,-0.025),(0.7,0.075),(0.73,0.075),(0.73,0.125),(0.68,0.125),(0.68,0.05),(0,0.05) #coat_hanger
# ]
def get_points(length,width):
    poly_points = [(0,-width/2),(length,-width/2),(length,width/2),(0,width/2)]
    return poly_points

def points_2d_to_poly(points, z):
    """Convert a sequence of 2d coordinates to a polydata with a polygon."""
    faces = [len(points), *range(len(points))]
    poly = pv.PolyData([p + (z,) for p in points], faces=faces)
    return poly

def create_mesh(poly_points,h):
    # bounding polygon
    polygon = points_2d_to_poly(poly_points, -h/2)
    # polygon.plot()
    # triangulate poly with all three subpolygons supplying edges
    # (relative face orientation is critical here)
    polygon_with_holes = polygon.delaunay_2d(edge_source=polygon)
    # polygon_with_holes.plot()
    # extrude
    holey_solid = polygon_with_holes.extrude((0, 0, h), capping=True)
    # holey_solid.plot()
    return holey_solid

mesh_list = []
# width_list = [0.03,0.06,0.08]
# length_list = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
width_list = [0.06]
length_list = [0.7,0.8,0.9,1.0]
title_list = []
for width in width_list:
    for length in length_list:
        points = get_points(length,width)
        print(width,length,points)
        mesh = create_mesh(points,0.05)
        # mesh.save("ply_dataset/stick1_L{}_W{}_H5.ply".format(int(length*100),int(width*100)))
        mesh_list.append(mesh)
        title_list.append("L{}_W{}".format(int(length*100),int(width*100)))
num = len(mesh_list)
num_x = int(math.sqrt(num))
num_y = int(num//num_x)
if num%num_x>0:
    num_y+=1

p = pv.Plotter(shape=(num_x,num_y))
for i in range(num_x):
    for j in range(num_y):
        if i*num_y+j<num:
            p.subplot(i,j)
            p.add_mesh(mesh_list[i*num_y+j],color='lightblue',show_edges=True)
            p.export_obj('../../assets/urdf/robotool/meshes2/stick1_'+title_list[i*num_y+j]+'_H5.obj') 
            # p.add_title(title_list[i*num_y+j])

p.save_graphic('stick1.svg')
# pl = pv.Plotter()
# _ = pl.add_mesh(holey_solid)
# pl.export_obj('coat_hanger.obj') 
# # pl.save_graphic('hook.svg')