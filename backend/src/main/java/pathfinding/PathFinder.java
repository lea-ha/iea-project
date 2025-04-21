package pathfinding;

import tools.Agent;
import tools.Coordinate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public abstract class PathFinder {

    public abstract List<Coordinate> findPath(
            int[][] grid,
            Agent agent,
            Map<SubNode, Integer> reservations,
            int maxPathLength
    );

    public static PathFinder getPathFinder(String algorithm) {
        if ("bfs".equalsIgnoreCase(algorithm)) {
            return new Bfs();
        } else {
            return new Astar();
        }
    }

    public static List<Coordinate> getNeighbors(Coordinate currentCoordinate, int[][] grid) {
        int[][] directions = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}, {0, 0}};
        List<Coordinate> neighbors = new ArrayList<>();

        for (int[] direction : directions) {
            int nx = currentCoordinate.x() + direction[0];
            int ny = currentCoordinate.y() + direction[1];

            if (nx >= 0 && nx < grid.length && ny >= 0 && ny < grid[0].length) {
                neighbors.add(Coordinate.with(nx, ny));
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
        // Manhattan distance
        return Math.abs(start.x() - goal.x()) + Math.abs(start.y() - goal.y());
    }
}
