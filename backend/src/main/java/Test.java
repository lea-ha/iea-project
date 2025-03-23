import cbs.CBS;
import hungarian.HungarianSolver;
import tools.Agent;
import tools.Coordinate;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Test {
    public static void main(String[] args) {

        int[][] grid = new int[10][10];

        for (int[] ints : grid) {
            Arrays.fill(ints, 0);
        }

        int[][] origins = {
                {0, 8}, {1, 8}, {2, 8}, {3, 8}, {4, 8}, {5, 8}, {6, 8}, {7, 8}, {8, 8}, {9, 8},
                {0, 9}, {1, 9}, {2, 9}, {3, 9}, {4, 9}, {5, 9}, {6, 9}, {7, 9}, {8, 9}, {9, 9}
        };

        int[][] destinations = {
                {3, 1}, {4, 1}, {5, 1}, {6, 1},
                {3, 2}, {4, 2}, {5, 2}, {6, 2},
                {3, 3}, {4, 3}, {5, 3}, {6, 3},
                {3, 4}, {4, 4}, {5, 4}, {6, 4},
                {3, 5}, {4, 5}, {5, 5}, {6, 5}
        };

        List<Agent> agents = HungarianSolver.getHungarianAgents(origins, destinations);


        Map<Integer, List<Coordinate>> cbs = CBS.cbs(grid, agents, new HashMap<>());

        System.out.println(cbs);

    }
}