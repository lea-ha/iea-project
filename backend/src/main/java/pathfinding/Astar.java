package pathfinding;

import cbs.ReservationManager;
import tools.Agent;
import tools.Coordinate;

import java.util.*;

public class Astar extends PathFinder {
    @Override
    public List<Coordinate> findPath(
            int[][] grid, Agent agent, ReservationManager reservationManager, int maxPathLength) {
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

            List<Coordinate> neighbors = getNeighbors(current.coordinate, grid);
            for (Coordinate neighbor : neighbors) {
                int t = current.g + 1;
                SubNode neighborNode = SubNode.of(neighbor, t);

                // Check if the position is reserved by another agent
                Map<SubNode, Integer> reservations = reservationManager.getReservations();
                if (reservations.containsKey(neighborNode) &&
                        !reservations.get(neighborNode).equals(agent.id())) {
                    continue; // reserved by another agent
                }

                // If morphing is enabled, check if this is a valid morphic position
                if (reservationManager.isMorphingEnabled() &&
                        !reservationManager.getMorphicPositions().contains(neighborNode)) {
                    continue; // not a morphic position
                }
                /*if (reservationManager.isMorphingEnabled() &&
                        !reservationManager.isMorphicToMove(neighborNode, agent)){
                    continue; //not morphic to move
                }*/

                List<Node> newPath = new ArrayList<>(current.path);
                newPath.add(new Node(neighbor, t, newPath));
                openSet.add(new Node(neighbor, t, newPath));
            }
        }
        return null; // No path found
    }
}