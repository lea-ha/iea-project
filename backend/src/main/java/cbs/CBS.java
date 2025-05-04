package cbs;

import pathfinding.Astar;
import pathfinding.PathFinder;
import pathfinding.SubNode;
import tools.*;

import java.util.*;

import static pathfinding.Astar.heuristic;

public class CBS {

    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations) {
        return cbs(grid, agents, fallbackReservations, "astar", false, null);  // Default to A* without morphing
    }


    public static Map<Integer, List<Coordinate>> cbs(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations,
            String algorithm, boolean enableMorphing, Integer maxPathLength) {

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
        if (maxPathLength == null) {
            maxPathLength = maxDistance;
        }
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
                System.out.println("Agent " + agent.id() + " failed to find path! Fallback mechanism initiated");
                // Reserve this spot for this agent in the future
                Fallback fallback = computeFallbackReservation(agent, reservationManager, grid, enableMorphing, maxPathLength);
                if (fallback == null) {
                    return null;
                }
                int sizeBefore = fallbackReservations.size();
                fallbackReservations.put(fallback.reservation(), agent.id());
                int sizeAfter = fallbackReservations.size();
                Integer fallbackMaxPathLength = fallback.maxPathLength();
                int newPathLength = sizeAfter == sizeBefore ? fallbackMaxPathLength + 1 : fallbackMaxPathLength; //means 2 agents are clashing -> give them space!
                // Relaunch CBS with the updated fallback
                return cbs(grid, agents, fallbackReservations, algorithm, enableMorphing, newPathLength);
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

            if (conflict == null) {
                System.out.println("Found solution with " + maxPathLength + " steps");
                return node.agentIdToPath();
            }

            int agentLow = conflict.agentLow;
            Constraint constraint = new Constraint(agentLow, conflict.coordinate, conflict.t);
            System.out.println(constraint);

            List<Constraint> newConstraints = new ArrayList<>(node.constraints());
            newConstraints.add(constraint);

            // Re-plan the lower-priority agent with the new constraint:
            // Create new reservations ignoring the lower-priority agent's current path.
            Map<SubNode, Integer> newReservations = createReservations(node.agentIdToPath(), agentLow);

            reservationManager.clearReservations();
            reservationManager.addAllReservations(newReservations);

            Agent agentLowObj = findAgentById(agents, agentLow);
            assert agentLowObj != null;
            List<Coordinate> constrainedPath = pathFinder.findPath(grid, agentLowObj, reservationManager, maxPathLength);
            if (constrainedPath == null) {
                continue;
            }

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
        return null;
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

    public static Fallback computeFallbackReservation(Agent agent,
                                                      ReservationManager reservationManager,
                                                      int[][] grid, boolean enableMorphing, int maxPathLength) {
        int pathLength = 0;
        int morphicPathLength = 0;
        SubNode latestReservationForAgent = getLatestReservationForAgent(reservationManager.getReservations(), agent);
        Coordinate latestCoordinateReached = latestReservationForAgent.coordinate;
        Coordinate fallbackCoordinate;
        Agent virtualAgent = new Agent(100, latestCoordinateReached, agent.goal());
        ReservationManager virtualReservationManager = new ReservationManager(grid, false);
        ReservationManager morphicReservationManager = new ReservationManager(grid, true);
        morphicReservationManager.addAllMorphicPositions(reservationManager.getMorphicPositions());
        PathFinder pathFinder = new Astar();
        List<Coordinate> path = pathFinder.findPath(grid, virtualAgent, virtualReservationManager, pathLength);
        List<Coordinate> morphicPath = pathFinder.findPath(grid, virtualAgent, morphicReservationManager, pathLength);
        while (path == null) {
            pathLength++;
            path = pathFinder.findPath(grid, virtualAgent, virtualReservationManager, pathLength);
            if (pathLength > 100){
                break;
            }
        }
        while (morphicPath == null) {
            morphicPathLength++;
            morphicPath = pathFinder.findPath(grid, virtualAgent, morphicReservationManager, pathLength);
            if (morphicPathLength > 100){
                break;
            }
        }
        if (path == null) {
            System.out.println("There is no possible path for agent " + agent.id());
            return null;
        }
        if (morphicPath != null && enableMorphing){
            int max = Math.max(morphicPathLength, maxPathLength);
            fallbackCoordinate = morphicPath.size() > 1 ? morphicPath.get(1) : morphicPath.get(0);
            int newTime = Math.min(latestReservationForAgent.g + 1, max);
            System.out.println("Morphic Fallback coordinate: " + fallbackCoordinate + ", " + newTime);
            return new Fallback(SubNode.of(fallbackCoordinate, newTime), max);
        }
        int max = Math.max(pathLength, maxPathLength);
        fallbackCoordinate = path.size() > 1 ? path.get(1) : path.get(0);
        int newTime = Math.min(latestReservationForAgent.g + 1, max);
        System.out.println("Fallback coordinate: " + fallbackCoordinate + ", " + newTime);
        return new Fallback(SubNode.of(fallbackCoordinate, newTime), max);
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