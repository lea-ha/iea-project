package pathfinding;

import cbs.ReservationManager;
import tools.Agent;
import tools.Coordinate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public abstract class PathFinder {
    private static boolean allowDiagonals = false;

    public abstract List<Coordinate> findPath(
            int[][] grid,
            Agent agent,
            ReservationManager reservationManager,
            int maxPathLength
    );

    public static PathFinder getPathFinder(String algorithm) {
        if ("bfs".equalsIgnoreCase(algorithm)) {
            return new Bfs();
        } else {
            return new Astar();
        }
    }

    public static void setAllowDiagonals(boolean allowDiag) {
        allowDiagonals = allowDiag;
    }

    public static boolean getAllowDiagonals() {
        return allowDiagonals;
    }

    public static List<Coordinate> getNeighbors(Coordinate currentCoordinate, int[][] grid) {
        List<Coordinate> neighbors = new ArrayList<>();

        // (Von Neumann)
        int[][] cardinalDirections = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}, {0, 0}};
        for (int[] direction : cardinalDirections) {
            int nx = currentCoordinate.x() + direction[0];
            int ny = currentCoordinate.y() + direction[1];
            if (nx >= 0 && nx < grid.length && ny >= 0 && ny < grid[0].length && grid[ny][nx] != 1) {
                neighbors.add(Coordinate.with(nx, ny));
            }
        }

        // Add diagonal directions if allowDiagonals is true (Moore)
        if (allowDiagonals) {
            int[][] diagonalDirections = {{1,1}, {1,-1}, {-1,-1}, {-1,1}};
            for (int[] direction : diagonalDirections) {
                int nx = currentCoordinate.x() + direction[0];
                int ny = currentCoordinate.y() + direction[1];
                if (nx >= 0 && nx < grid.length && ny >= 0 && ny < grid[0].length && grid[ny][nx] != 1) {
                    neighbors.add(Coordinate.with(nx, ny));
                }
            }
        }

        return neighbors;
    }

    public static List<Coordinate> getPath(Node node) {
        List<Coordinate> path = new ArrayList<>();
        for (Node n : node.path) {
            path.add(new Coordinate(n.coordinate.x(), n.coordinate.y()));
        }
        return path;
    }

    public static int heuristic(Coordinate start, Coordinate goal) {
        if (allowDiagonals) {
            return Math.max(Math.abs(start.x() - goal.x()), Math.abs(start.y() - goal.y()));
        } else {
            return Math.abs(start.x() - goal.x()) + Math.abs(start.y() - goal.y());
        }
    }
}