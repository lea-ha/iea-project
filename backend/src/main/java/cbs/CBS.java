package cbs;

import pathfinding.Astar;
import pathfinding.PathFinder;
import pathfinding.SubNode;
import tools.*;

import java.util.*;

import static pathfinding.Astar.heuristic;

public class CBS {

    /**
     * Runs conflict-based search on the given grid and list of agents.
     * Returns a map from agent ID to its computed path (list of Coordinates).
     */

    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations) {
        return cbs(grid, agents, fallbackReservations, "astar");  // Default to A*
    }

    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations, String algorithm) {

        // Get the appropriate pathfinder based on the algorithm parameter
        PathFinder pathFinder = PathFinder.getPathFinder(algorithm);

        // Create a map of agent priorities (lower number = higher priority) and find max path length
        Map<Integer, Integer> priorities = new HashMap<>();
        int maxPathLength = 0;
        for (Agent agent : agents) {
            priorities.put(agent.id(), agent.getPriority());
            int distance = heuristic(agent.start(), agent.goal());
            maxPathLength = Math.max(maxPathLength, distance) + fallbackReservations.size();
        }
        System.out.println("Found solution with " + maxPathLength + " steps");
        // Initial planning: plan each agent's path ignoring others (but reserving its cells)
        Map<SubNode, Integer> reservations = new HashMap<>(fallbackReservations);
        Map<Integer, List<Coordinate>> paths = new HashMap<>();

        // Plan in priority order (sort agents by priority)
        agents.sort(Comparator.comparingInt(Agent::getPriority));

        for (Agent agent : agents) {
            List<Coordinate> path = pathFinder.findOptimalPath(grid, agent, reservations, maxPathLength);
            if (path == null) {
                System.out.println("Agent " + agent.id() + " failed to find path!\nFallback mechanism initiated");
                // Reserve this spot for this agent in the future
                SubNode fallbackReservation = computeFallbackReservation(agent, reservations);
                fallbackReservations.put(fallbackReservation, agent.id());
                // Relaunch CBS with the updated fallbackReservation
                return cbs(grid, agents, fallbackReservations, algorithm);
            }
            // Reserve the path cells (other agents must avoid these)
            for (int t = 0; t < path.size(); t++) {
                Coordinate pos = path.get(t);
                SubNode key = SubNode.of(pos, t);
                reservations.put(key, agent.id());
            }
            paths.put(agent.id(), path);
        }

        // Create the root CBS node
        int totalCost = paths.values().stream().mapToInt(List::size).sum();
        CBSNode root = new CBSNode(paths, new ArrayList<>(), totalCost);
        PriorityQueue<CBSNode> openSet = new PriorityQueue<>();
        openSet.add(root);

        while (!openSet.isEmpty()) {
            CBSNode node = openSet.poll();
            Conflict conflict = ConflictDetector.detectConflict(node.agentIdToPath(), priorities);

            // If no conflict exists, we've found a valid solution.
            if (conflict == null) {
                return node.agentIdToPath();
            }

            int agentLow = conflict.agentLow;
            // Create a constraint for the lower-priority agent to avoid the conflict
            Constraint constraint = new Constraint(agentLow, conflict.coordinate, conflict.t);
            System.out.println(constraint);

            // Copy constraints and add the new one.
            List<Constraint> newConstraints = new ArrayList<>(node.constraints());
            newConstraints.add(constraint);

            // Re-plan the lower-priority agent with the new constraint:
            // Create new reservations ignoring the lower-priority agent's current path.
            Map<SubNode, Integer> newReservations = createReservations(node.agentIdToPath(), agentLow);
            Agent agentLowObj = findAgentById(agents, agentLow);
            assert agentLowObj != null;
            List<Coordinate> constrainedPath = pathFinder.findPath(grid, agentLowObj, newReservations, maxPathLength);
            if (constrainedPath == null) {
                // No valid path found under this constraint; skip this branch.
                continue;
            }

            // Copy paths and update the lower-priority agent's path.
            Map<Integer, List<Coordinate>> newPaths = new HashMap<>(node.agentIdToPath());
            newPaths.put(agentLow, constrainedPath);

            // Add reservations for the updated path.
            for (int t2 = 0; t2 < constrainedPath.size(); t2++) {
                Coordinate pos = constrainedPath.get(t2);
                newReservations.put(SubNode.of(pos, t2), agentLow);
            }

            int newCost = newPaths.values().stream().mapToInt(List::size).sum();
            CBSNode newNode = new CBSNode(newPaths, newConstraints, newCost);
            openSet.add(newNode);
        }
        return null; // Failed to find a solution.
    }

    /**
     * Build a reservation table from all paths except the one for the given agent.
     */
    public static Map<SubNode, Integer> createReservations(Map<Integer, List<Coordinate>> paths, Integer excludeAgent) {
        Map<SubNode, Integer> reservations = new HashMap<>();
        for (Map.Entry<Integer, List<Coordinate>> entry : paths.entrySet()) {
            if (entry.getKey().equals(excludeAgent)) continue;
            List<Coordinate> path = entry.getValue();
            for (int t = 0; t < path.size(); t++) {
                Coordinate pos = path.get(t);
                reservations.put(SubNode.of(pos, t), entry.getKey());
            }
        }
        return reservations;
    }

    private static Agent findAgentById(List<Agent> agents, int id) {
        for (Agent agent : agents) {
            if (agent.id() == id) {
                return agent;
            }
        }
        return null;
    }

    public static SubNode computeFallbackReservation(Agent agent, Map<SubNode, Integer> reservations) {

        SubNode latestReservationForAgent = getLatestReservationForAgent(reservations, agent);
        Coordinate latestCoordinate = latestReservationForAgent.coordinate;
        SubNode fallbackNode = SubNode.of(latestCoordinate, latestReservationForAgent.g + 1);

        if (latestCoordinate.y() > agent.goal().y()) {
            fallbackNode = SubNode.of(
                    Coordinate.with(latestCoordinate.x(), latestCoordinate.y() - 1), latestReservationForAgent.g + 1);
        }

        else if (latestCoordinate.x() > agent.goal().x()) {
            fallbackNode = SubNode.of(
                    Coordinate.with(latestCoordinate.x() - 1, latestCoordinate.y()), latestReservationForAgent.g + 1);
        }

        else if (latestCoordinate.x() < agent.goal().x()) {
            fallbackNode = SubNode.of(
                    Coordinate.with(latestCoordinate.x() + 1, latestCoordinate.y()), latestReservationForAgent.g + 1);
        }

        if (reservations.containsKey(fallbackNode)) {
            System.out.println("CRITICAL RESERVATION NOT RESPECTED  COMPLETE LOGIC ON FALLBACK");
        }

        System.out.println("Fallback reservation for " + agent.id() + ": " + fallbackNode.coordinate.toString() + " at " + fallbackNode.g);
        return fallbackNode;
    }

    public static SubNode getLatestReservationForAgent(Map<SubNode, Integer> reservations, Agent agent) {
        SubNode latestSubNode = null;
        int latestTime = Integer.MIN_VALUE; // Start with the smallest possible time

        for (Map.Entry<SubNode, Integer> entry : reservations.entrySet()) {
            SubNode subNode = entry.getKey();
            int reservedAgentId = entry.getValue();

            if (reservedAgentId == agent.id()) {
                int nodeTime = subNode.g; // Assuming SubNode has time()

                if (nodeTime > latestTime) {
                    latestTime = nodeTime;
                    latestSubNode = subNode;
                }
            }
        }

        if (latestSubNode == null) {
            return SubNode.of(agent.start(), 0);
        }

        return latestSubNode;
    }



}