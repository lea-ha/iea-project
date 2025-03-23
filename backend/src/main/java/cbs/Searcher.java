package cbs;

import tools.Agent;
import tools.Coordinate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Searcher {

    public static Map<Integer, List<Coordinate>> boostedCbs(int[][] grid, List<Agent> agents) {
        int minBeforeStart = 3;
        int maxBeforeGiveUp = 50;
        for (int i = minBeforeStart; i < maxBeforeGiveUp; i++) {
            Map<Integer, List<Coordinate>> solution = CBS.cbsExperimental(grid, agents, new HashMap<>(), i);
            if (solution != null) {
                System.out.println("Found a solution with only " + i + " steps!");
                return solution;
            }
        }
        return null;
    }

}
