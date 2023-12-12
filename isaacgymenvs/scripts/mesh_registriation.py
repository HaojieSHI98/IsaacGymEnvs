import copy

import numpy as np
import open3d as o3d


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


def main():
    voxel_size = 0.01
    print(":: Load two mesh.")
    target_mesh = o3d.io.read_triangle_mesh('stick_example.ply')
    # source_mesh = copy.deepcopy(target_mesh)
    source_mesh = o3d.io.read_triangle_mesh('stick_example2.ply')
    source_mesh.rotate(source_mesh.get_rotation_matrix_from_xyz((np.pi / 4, 0, np.pi / 4)), center=(0, 0, 0))
    source_mesh.translate((0, 0.05, 0))
    draw_registration_result(target_mesh, source_mesh, np.identity(4))

    print(":: Sample mesh to point cloud")
    target = target_mesh.sample_points_uniformly(1000)
    source = source_mesh.sample_points_uniformly(1000)
    draw_registration_result(source, target, np.identity(4))

    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)
    result_ransac = execute_global_registration(source_down, target_down,
                                                source_fpfh, target_fpfh,
                                                voxel_size)
    print(result_ransac)
    draw_registration_result(source_down, target_down, result_ransac.transformation)
    draw_registration_result(source_mesh, target_mesh, result_ransac.transformation)


if __name__ == '__main__':
    main()