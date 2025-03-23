package astar;

import tools.Agent;
import tools.Coordinate;

import java.util.*;

public class Astar {

    public static List<Coordinate> aStar(
            int[][] grid, Agent agent, Map<SubNode, Integer> reservations, int maxPathLength) {
        Coordinate start = agent.start();
        Coordinate goal = agent.goal();

        PriorityQueue<Node> openSet = new PriorityQueue<>(
                Comparator.comparingInt(node -> node.g + heuristic(node.coordinate, goal)));

        Node startNode = new Node(Coordinate.with(start.x(), start.y()), 0, new ArrayList<>());
        startNode.path.add(startNode); // Add the starting node to its own path.
        openSet.add(startNode);

        Set<SubNode> visited = new HashSet<>();

        while (!openSet.isEmpty()) {

            Node current = openSet.poll();

            // EARLY PRUNING
            if (current.g > maxPathLength) {
                continue;
            }

            if (visited.contains(SubNode.of(current.coordinate, current.g))) {
                continue;
            }
            visited.add(SubNode.of(current.coordinate, current.g));

            if (current.coordinate.equals(goal) && current.g == maxPathLength) {
                return getPath(current);
            }

            List<Coordinate> neighbors = getNeighbors(current.coordinate, grid);
            for (Coordinate neighbor : neighbors) {
                int t = current.g + 1;
                SubNode neighborNode = SubNode.of(neighbor, t);
                if (reservations.containsKey(neighborNode) && !reservations.get(neighborNode).equals(agent.id())) {
                    continue; //reserved by another agent
                }

                List<Node> newPath = new ArrayList<>(current.path);
                newPath.add(new Node(neighbor, t, newPath));
                openSet.add(new Node(neighbor, t, newPath));
            }
        }
        return null; // No path found
    }

    private static List<Coordinate> getNeighbors(Coordinate currentCoordinate, int[][] grid) {
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

    private static List<Coordinate> getPath(Node node) {
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
