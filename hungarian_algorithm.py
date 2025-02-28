import numpy as np
from scipy.optimize import linear_sum_assignment


def hungarian_algorithm(cost_matrix):
    """
    Implement the Hungarian algorithm using scipy's linear_sum_assignment

    Parameters:
    cost_matrix (numpy.ndarray): A matrix where cost_matrix[i,j] is the cost of
                                 assigning cube i to position j

    Returns:
    tuple: (row_indices, col_indices) where row_indices[i] is matched with col_indices[i]
    float: Total minimum cost of the assignment
    """
    row_indices, col_indices = linear_sum_assignment(cost_matrix)
    total_cost = cost_matrix[row_indices, col_indices].sum()

    return (row_indices, col_indices), total_cost


def create_cost_matrix(cubes, shape_positions, cost_function):
    """
    Create a cost matrix for the assignment problem

    Parameters:
    cubes (list): List of cube objects or positions
    shape_positions (list): List of target positions in the shape
    cost_function (function): A function that takes a cube and position and returns a cost

    Returns:
    numpy.ndarray: Cost matrix where cost_matrix[i,j] is the cost of assigning cube i to position j
    """
    n_cubes = len(cubes)
    n_positions = len(shape_positions)

    # Initialize cost matrix with zeros
    cost_matrix = np.zeros((n_cubes, n_positions))

    # Fill cost matrix with costs for each cube-position pair
    for i, cube in enumerate(cubes):
        for j, position in enumerate(shape_positions):
            cost_matrix[i, j] = cost_function(cube, position)

    return cost_matrix


# Example usage with a Manhattan distance cost function
def manhattan_distance(cube_pos, target_pos):
    """Calculate Manhattan distance between two positions"""
    return sum(abs(a - b) for a, b in zip(cube_pos, target_pos))
