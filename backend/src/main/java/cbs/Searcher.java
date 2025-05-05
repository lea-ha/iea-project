package cbs;

import pathfinding.PathFinder;
import tools.Agent;
import tools.Coordinate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Searcher {

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents) {
        return boostedCbs(grid, agents, "astar", true, "priority");  // Default: A* and morphing enabled, priority-based conflict resolution
    }

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents, String algorithm) {
        return boostedCbs(grid, agents, algorithm, true, "priority");  // Default: morphing enabled, priority-based conflict resolution
    }

    public static Map<Integer, List<Coordinate>> boostedCbs(
            int[][] grid, List<Agent> agents, String algorithm, boolean morphingEnabled) {
        return boostedCbs(grid, agents, algorithm, morphingEnabled, "priority"); // Default: priority-based conflict resolution
    }

    public static Map<Integer, List<Coordinate>> boostedCbs(
            int[][] grid, List<Agent> agents, String algorithm,
            boolean morphingEnabled, String conflictResolutionStrategy) {
        Map<Integer, List<Coordinate>> solution = CBS.cbs(
                grid, agents, new HashMap<>(), algorithm, morphingEnabled, null, conflictResolutionStrategy);
        return solution;
    }
}