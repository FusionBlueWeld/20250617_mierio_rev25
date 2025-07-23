import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

def finetune_grid_with_real_data(grid_data: dict, plot_df: pd.DataFrame, x_col: str, y_col: str, z_col: str, radius: float = 0.1, power: int = 2):
    if not all(k in grid_data for k in ['X', 'Y', 'Z']):
        raise ValueError("grid_data must contain 'X', 'Y', and 'Z' keys.")
    if not all(c in plot_df.columns for c in [x_col, y_col, z_col]):
        raise ValueError(f"plot_df must contain columns: {x_col}, {y_col}, {z_col}.")
    if plot_df.empty:
        return grid_data

    finetuned_grid = {
        'X': np.copy(grid_data['X']),
        'Y': np.copy(grid_data['Y']),
        'Z': np.copy(grid_data['Z'])
    }

    real_points = plot_df[[x_col, y_col]].values
    real_z_values = plot_df[z_col].values
    
    grid_x = finetuned_grid['X']
    grid_y = finetuned_grid['Y']
    grid_z = finetuned_grid['Z']

    try:
        kdtree = cKDTree(real_points)
    except Exception as e:
        raise ValueError(f"Failed to build KDTree from real data points. Check for NaNs or invalid values. Original error: {e}")

    grid_height, grid_width = grid_z.shape

    x_vec = grid_x[0, :] if len(grid_x.shape) > 1 else grid_x
    y_vec = grid_y[:, 0] if len(grid_y.shape) > 1 else grid_y

    if len(x_vec) != grid_width or len(y_vec) != grid_height:
        raise ValueError("Grid dimensions do not match. X-vector length must match Z-grid width, and Y-vector length must match Z-grid height.")

    for i in range(grid_height):
        for j in range(grid_width):
            grid_point = np.array([x_vec[j], y_vec[i]])
            indices = kdtree.query_ball_point(grid_point, r=radius)
            
            if not indices:
                continue

            total_weight = 0.0
            weighted_z_diff_sum = 0.0
            
            current_grid_z = grid_z[i, j]

            for idx in indices:
                neighbor_point = real_points[idx]
                neighbor_z = real_z_values[idx]

                distance = np.linalg.norm(grid_point - neighbor_point)

                epsilon = 1e-6
                if distance < epsilon:
                    weight = 1.0 / epsilon
                else:
                    weight = 1.0 / (distance ** power)

                z_difference = neighbor_z - current_grid_z
                
                weighted_z_diff_sum += z_difference * weight
                total_weight += weight

            if total_weight > 0:
                correction_value = weighted_z_diff_sum / total_weight
                finetuned_grid['Z'][i, j] += correction_value

    return finetuned_grid