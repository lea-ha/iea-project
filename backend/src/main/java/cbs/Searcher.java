package cbs;

import tools.Agent;
import tools.Coordinate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Searcher {

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents) {

        Map<Integer, List<Coordinate>> solution = CBS.cbs(grid, agents, new HashMap<>());
        return solution;
    }

}
