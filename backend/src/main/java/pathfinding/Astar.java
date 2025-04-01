package pathfinding;

import tools.Agent;
import tools.Coordinate;

import java.util.*;

public class Astar extends PathFinder {

    @Override
    public List<Coordinate> findPath(
            int[][] grid, Agent agent, Map<SubNode, Integer> reservations, int maxPathLength) {
        Coordinate start = agent.start();
        Coordinate goal = agent.goal();

        PriorityQueue<Node> openSet = new PriorityQueue<>(
                Comparator.comparingInt(node -> node.g + heuristic(node.coordinate, goal)));

        Node startNode = new Node(Coordinate.with(start.x(), start.y()), 0, new ArrayList<>());
        startNode.path.add(startNode);
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

            List<Coordinate> neighbors = getNeighbors(current.coordinate, grid); //valid positions inside the grid
            for (Coordinate neighbor : neighbors) {
                int t = current.g + 1;
                Set<SubNode> morphingSet = createMorphingSet(reservations, t, grid);
                SubNode neighborNode = SubNode.of(neighbor, t);
                if (reservations.containsKey(neighborNode) && !reservations.get(neighborNode).equals(agent.id())) {
                    continue; //reserved by another agent
                }
                if (!morphingSet.contains(neighborNode)) {
                    continue; //not a morphic position
                }

                List<Node> newPath = new ArrayList<>(current.path);
                newPath.add(new Node(neighbor, t, newPath));
                openSet.add(new Node(neighbor, t, newPath));
            }
        }
        return null; // No path found
    }

    /*public static List<Coordinate> centroidAstar(
            int[][] grid, Agent agent, Map<SubNode, Integer> reservations, int maxPathLength) {
        Coordinate start = agent.start();
        Coordinate goal = agent.centroidGoal();

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

            List<Coordinate> neighbors = getNeighbors(current.coordinate, grid); //valid positions inside the grid
            for (Coordinate neighbor : neighbors) {
                int t = current.g + 1;
                Set<SubNode> morphingSet = createMorphingSet(reservations, t, grid);
                SubNode neighborNode = SubNode.of(neighbor, t);
                if (reservations.containsKey(neighborNode) && !reservations.get(neighborNode).equals(agent.id())) {
                    continue; //reserved by another agent
                }
                if (!morphingSet.contains(neighborNode)) {
                    continue; //not a morphic position
                }

                List<Node> newPath = new ArrayList<>(current.path);
                newPath.add(new Node(neighbor, t, newPath));
                openSet.add(new Node(neighbor, t, newPath));
            }
        }
        return null; // No path found
    }*/

    public static int heuristic(Coordinate start, Coordinate goal) {
        // Manhattan distance
        return Math.abs(start.x() - goal.x()) + Math.abs(start.y() - goal.y());
    }

    public static Set<SubNode> createMorphingSet(Map<SubNode, Integer> reservations, int time, int[][] grid) {
        Set<SubNode> morphingSet = new HashSet<>();
        reservations.keySet()
                .stream().filter(subNode -> subNode.g == time)
                .forEach(subnode -> {
                    List<Coordinate> neighbors = getMorphingNeighbors(subnode.coordinate, grid);
                    neighbors.forEach(neighbor -> morphingSet.add(SubNode.of(neighbor, time)));
                });
        return morphingSet;
    }

    private static List<Coordinate> getMorphingNeighbors(Coordinate currentCoordinate, int[][] grid) {
        int[][] directions = {{0, 1}, {1, 0}, {1,1}, {1,-1},{0, -1}, {-1, 0}, {-1, 1}, {-1,-1}, {0,0}};
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

}