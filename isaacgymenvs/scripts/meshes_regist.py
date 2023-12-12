import copy
import os
import numpy as np
import open3d as o3d
import random
import math
def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp])


def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh


def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result

def sample_meshes(path,k):
    dir = os.listdir(path)
    samples_path = random.sample(dir,k)
    target = samples_path[0]
    width = target[-8]
    for x in ['3','6','8']:
        if x!= width:
            new_target = target[:-8]+x+target[-7:]
            break
    samples_path.append(new_target)
    samples_path = [os.path.join('./ply_dataset',s) for s in samples_path]
    mesh_list = [o3d.io.read_triangle_mesh(s) for s in samples_path]
    return mesh_list

def preprocess_meshes(mesh_list):
    mesh_num = len(mesh_list)
    num_x = int(math.sqrt(mesh_num))
    num_y = int(mesh_num//num_x)
    if mesh_num%num_x>0:
        num_y+=1
    for i in range(num_x):
        for j in range(num_y):
            frame = i*num_y+j
            if frame<mesh_num:
                frame = i*num_y+j
                if frame ==0:
                    mesh_list[frame].paint_uniform_color([1, 0.706, 0])
                else:
                    mesh_list[frame].paint_uniform_color([0, 0.651, 0.929])
                mesh_list[frame].translate((1.2*i, 1.2*j, 0))
                mesh_list[frame].rotate(mesh_list[frame].get_rotation_matrix_from_xyz((0, 0, np.pi / 3*random.random())), center=(0, 0, 0))
    return mesh_list

def compare_two_mesh(target_mesh,source_mesh):
    voxel_size = 0.01
    target = target_mesh.sample_points_uniformly(1000)
    source = source_mesh.sample_points_uniformly(1000)
    draw_registration_result(source, target, np.identity(4))

    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    result_ransac = execute_global_registration(source_down, target_down,
                                                source_fpfh, target_fpfh,
                                                voxel_size) 
    draw_registration_result(source_down, target_down, result_ransac.transformation)
    return result_ransac.fitness

def main():
    print(":: Load k mesh.")
    mesh_list = sample_meshes("./ply_dataset",5)
    mesh_list = preprocess_meshes(mesh_list)
    o3d.visualization.draw_geometries(mesh_list)
    fitness_list = []
    for i in range(1,len(mesh_list)):
        fitness = compare_two_mesh(mesh_list[0],mesh_list[i])
        fitness_list.append(fitness)
        mesh_list[i].paint_uniform_color([fitness, 0.706, 0])
    o3d.visualization.draw_geometries(mesh_list)
    print(fitness_list)
    # print(":: Sample mesh to point cloud")
    # target = target_mesh.sample_points_uniformly(1000)
    # source = source_mesh.sample_points_uniformly(1000)
    # draw_registration_result(source, target, np.identity(4))

    # source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    # target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    # result_ransac = execute_global_registration(source_down, target_down,
    #                                             source_fpfh, target_fpfh,
    #                                             voxel_size)
    # print(result_ransac)
    # draw_registration_result(source_down, target_down, result_ransac.transformation)
    # draw_registration_result(source_mesh, target_mesh, result_ransac.transformation)


if __name__ == '__main__':
    main()