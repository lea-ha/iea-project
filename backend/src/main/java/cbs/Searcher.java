package cbs;

import pathfinding.PathFinder;
import tools.Agent;
import tools.Coordinate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Searcher {

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents) {
        return boostedCbs(grid, agents, "astar");  // A* is default
    }

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents, String algorithm) {
        Map<Integer, List<Coordinate>> solution = CBS.cbs(grid, agents, new HashMap<>(), algorithm);
        return solution;
    }
}