package cbs;

import pathfinding.PathFinder;
import pathfinding.SubNode;
import tools.*;

import java.util.*;

import static pathfinding.Astar.heuristic;

public class CBS {

    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations) {
        return cbs(grid, agents, fallbackReservations, "astar", false);  // Default to A* without morphing
    }


    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations,
            String algorithm, boolean enableMorphing) {

        // Get the appropriate pathfinder based on the algorithm parameter
        PathFinder pathFinder = PathFinder.getPathFinder(algorithm);

        // Create a map of agent priorities (lower number = higher priority) and find max path length
        Map<Integer, Integer> priorities = new HashMap<>();
        int maxDistance = 0;
        for (Agent agent : agents) {
            priorities.put(agent.id(), agent.getPriority());
            int distance = heuristic(agent.start(), agent.goal());
            maxDistance = Math.max(maxDistance, distance);
        }
        int maxPathLength = maxDistance + (fallbackReservations.size() / 5);
        System.out.println("Max path length: " + maxPathLength);
        if (maxPathLength > 200){
            System.out.println("No solution with less than 200 steps was found!");
            return null;
        }
        // Initial planning: plan each agent's path ignoring others (but reserving its cells)
        ReservationManager reservationManager = new ReservationManager(grid, enableMorphing);
        reservationManager.addAllReservations(initiateReservationsMap(agents, fallbackReservations));
        Map<Integer, List<Coordinate>> paths = new HashMap<>();

        // Plan in priority order (sort agents by priority)
        agents.sort(Comparator.comparingInt(Agent::getPriority));

        for (Agent agent : agents) {
            List<Coordinate> path = pathFinder.findPath(grid, agent, reservationManager, maxPathLength);
            if (path == null) {
                System.out.println("Agent " + agent.id() + " failed to find path!\nFallback mechanism initiated");
                // Reserve this spot for this agent in the future
                SubNode fallbackReservation = computeFallbackReservation(agent, reservationManager, enableMorphing);
                fallbackReservations.put(fallbackReservation, agent.id());
                // Relaunch CBS with the updated fallbackReservation
                return cbs(grid, agents, fallbackReservations, algorithm, enableMorphing);
            }

            // Reserve the path cells (other agents must avoid these)
            for (int t = 0; t < path.size(); t++) {
                Coordinate pos = path.get(t);
                SubNode key = SubNode.of(pos, t);
                reservationManager.addReservation(key, agent.id());
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
                System.out.println("Found solution with " + maxPathLength + " steps");
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

            // Clear and update the reservation manager
            reservationManager.clearReservations();
            reservationManager.addAllReservations(newReservations);

            Agent agentLowObj = findAgentById(agents, agentLow);
            assert agentLowObj != null;
            List<Coordinate> constrainedPath = pathFinder.findPath(grid, agentLowObj, reservationManager, maxPathLength);
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
                SubNode key = SubNode.of(pos, t2);
                reservationManager.addReservation(key, agentLow);
            }

            int newCost = newPaths.values().stream().mapToInt(List::size).sum();
            CBSNode newNode = new CBSNode(newPaths, newConstraints, newCost);
            openSet.add(newNode);
        }
        return null; // Failed to find a solution.
    }

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

    public static SubNode computeFallbackReservation(Agent agent, ReservationManager reservationManager, boolean enableMorphing) {
        SubNode latestReservationForAgent = getLatestReservationForAgent(reservationManager.getReservations(), agent);
        Coordinate latestCoordinate = latestReservationForAgent.coordinate;

        if (!enableMorphing) {
            // Use the old logic when morphing not enableds
            if (latestCoordinate.y() > agent.goal().y()) {
                return SubNode.of(
                        Coordinate.with(latestCoordinate.x(), latestCoordinate.y() - 1),
                        latestReservationForAgent.g + 1);
            }
            return SubNode.of(latestCoordinate, latestReservationForAgent.g + 1);
        }

        // Use the more complex morphing-aware logic when morphing is enabled
        SubNode fallbackNode = SubNode.of(latestCoordinate, latestReservationForAgent.g + 1);
        SubNode morphicNode = null;

        if (latestCoordinate.x() > agent.goal().x()) {
            SubNode node = SubNode.of(
                    Coordinate.with(latestCoordinate.x() - 1, latestCoordinate.y()),
                    latestReservationForAgent.g + 1);
            if (reservationManager.getMorphicPositions().contains(node) &&
                    !reservationManager.getReservations().containsKey(node)) {
                morphicNode = node;
            }
        }
        else if (latestCoordinate.x() < agent.goal().x()) {
            SubNode node = SubNode.of(
                    Coordinate.with(latestCoordinate.x() + 1, latestCoordinate.y()),
                    latestReservationForAgent.g + 1);
            if (reservationManager.getMorphicPositions().contains(node) &&
                    !reservationManager.getReservations().containsKey(node)) {
                morphicNode = node;
            }
        }
        else if (latestCoordinate.y() > agent.goal().y()) {
            SubNode node = SubNode.of(
                    Coordinate.with(latestCoordinate.x(), latestCoordinate.y() - 1),
                    latestReservationForAgent.g + 1);
            if (reservationManager.getMorphicPositions().contains(node) &&
                    !reservationManager.getReservations().containsKey(node)) {
                morphicNode = node;
            }
        }
        else if (latestCoordinate.y() < agent.goal().y()) {
            SubNode node = SubNode.of(
                    Coordinate.with(latestCoordinate.x(), latestCoordinate.y() + 1),
                    latestReservationForAgent.g + 1);
            if (reservationManager.getMorphicPositions().contains(node) &&
                    !reservationManager.getReservations().containsKey(node)) {
                morphicNode = node;
            }
        }

        if (morphicNode != null) {
            System.out.println("Morphic fallback reservation for " + agent.id() + ": " +
                    morphicNode.coordinate.toString() + " at " + morphicNode.g);
            return morphicNode;
        }

        System.out.println("Fallback reservation for " + agent.id() + ": " +
                fallbackNode.coordinate.toString() + " at " + fallbackNode.g);
        return fallbackNode;
    }

    public static SubNode getLatestReservationForAgent(Map<SubNode, Integer> reservations, Agent agent) {
        SubNode latestSubNode = null;
        int latestTime = Integer.MIN_VALUE; // Start with the smallest possible time

        for (Map.Entry<SubNode, Integer> entry : reservations.entrySet()) {
            SubNode subNode = entry.getKey();
            int reservedAgentId = entry.getValue();

            if (reservedAgentId == agent.id()) {
                int nodeTime = subNode.g;

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

    private static Map<SubNode, Integer> initiateReservationsMap(
            List<Agent> agents,
            Map<SubNode, Integer> fallbackReservations) {
        HashMap<SubNode, Integer> reservations = new HashMap<>(fallbackReservations);
        agents.forEach(agent -> reservations.put(SubNode.of(agent.start(), 0), agent.id()));
        return reservations;
    }
}