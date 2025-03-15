package cbs;

import astar.Astar;
import astar.SubNode;
import tools.*;

import java.util.*;

public class CBS {

    /**
     * Runs conflict-based search on the given grid and list of agents.
     * Returns a map from agent ID to its computed path (list of Coordinates).
     */
    public static Map<Integer, List<Coordinate>> cbs(int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations) {
        // Create a map of agent priorities (lower number = higher priority)
        Map<Integer, Integer> priorities = new HashMap<>();
        for (Agent agent : agents) {
            priorities.put(agent.id(), agent.getPriority());
        }

        // Initial planning: plan each agent’s path ignoring others (but reserving its cells)
        Map<SubNode, Integer> reservations = new HashMap<>(fallbackReservations);
        Map<Integer, List<Coordinate>> paths = new HashMap<>();

        // Plan in priority order (sort agents by priority)
        agents.sort(Comparator.comparingInt(Agent::getPriority));
        for (Agent agent : agents) {
            List<Coordinate> path = Astar.aStar(grid, agent, reservations, 20);
            if (path == null) {
                System.out.println("Agent " + agent.id() + " failed to find path!\nFallback mechanism initiated");
                // Reserve this spot for this agent in the future
                SubNode fallbackReservation = computeFallbackReservation(agent, reservations);
                fallbackReservations.put(fallbackReservation, agent.id());
                // Relaunch CBS with the updated fallbackReservation
                return cbs(grid, agents, fallbackReservations);
            }
            if (path.isEmpty()){
                return null;
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

            // Copy constraints and add the new one.
            List<Constraint> newConstraints = new ArrayList<>(node.constraints());
            newConstraints.add(constraint);

            // Re-plan the lower-priority agent with the new constraint:
            // Create new reservations ignoring the lower-priority agent’s current path.
            Map<SubNode, Integer> newReservations = createReservations(node.agentIdToPath(), agentLow);
            Agent agentLowObj = findAgentById(agents, agentLow);
            assert agentLowObj != null;
            List<Coordinate> constrainedPath = Astar.aStar(grid, agentLowObj, newReservations, 20);
            if (constrainedPath == null) {
                // No valid path found under this constraint; skip this branch.
                continue;
            }

            // Copy paths and update the lower-priority agent’s path.
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
        int t = 1;
        SubNode candidate;

        while (true) {
            candidate = SubNode.of(agent.start(), t);
            if (!reservations.containsKey(candidate)) {
                return candidate;
            }
            t++;

            if (t > 10) {
                System.out.println("No available fallback reservation found for agent " + agent.id());
            }
        }
    }

    public static Map<Integer, List<Coordinate>> cbsExperimental(
            int[][] grid, List<Agent> agents, HashMap<SubNode, Integer> fallbackReservations, int maxPathLength) {
        // Create a map of agent priorities (lower number = higher priority)
        Map<Integer, Integer> priorities = new HashMap<>();
        for (Agent agent : agents) {
            priorities.put(agent.id(), agent.getPriority());
        }

        // Initial planning: plan each agent’s path ignoring others (but reserving its cells)
        Map<SubNode, Integer> reservations = new HashMap<>(fallbackReservations);
        Map<Integer, List<Coordinate>> paths = new HashMap<>();

        // Plan in priority order (sort agents by priority)
        agents.sort(Comparator.comparingInt(Agent::getPriority));
        for (Agent agent : agents) {
            List<Coordinate> path = Astar.aStar(grid, agent, reservations, maxPathLength);
            if (path == null) {
                System.out.println("Agent " + agent.id() + " failed to find path!\nFallback mechanism initiated");
                // Reserve this spot for this agent in the future
                SubNode fallbackReservation = computeFallbackReservation(agent, reservations);
                fallbackReservations.put(fallbackReservation, agent.id());
                // Relaunch CBS with the updated fallbackReservation
                return cbs(grid, agents, fallbackReservations);
            }
            if (path.isEmpty()){
                return null;
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

            // Copy constraints and add the new one.
            List<Constraint> newConstraints = new ArrayList<>(node.constraints());
            newConstraints.add(constraint);

            // Re-plan the lower-priority agent with the new constraint:
            // Create new reservations ignoring the lower-priority agent’s current path.
            Map<SubNode, Integer> newReservations = createReservations(node.agentIdToPath(), agentLow);
            Agent agentLowObj = findAgentById(agents, agentLow);
            assert agentLowObj != null;
            List<Coordinate> constrainedPath = Astar.aStar(grid, agentLowObj, newReservations, maxPathLength);
            if (constrainedPath == null) {
                // No valid path found under this constraint; skip this branch.
                continue;
            }

            // Copy paths and update the lower-priority agent’s path.
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
}