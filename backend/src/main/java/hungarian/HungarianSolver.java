package hungarian;

import tools.Agent;
import tools.Coordinate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HungarianSolver {

    private static int[][] createCostMatrix(int[][] origins, int[][] destinations) {
        int[][] costMatrix = new int[origins.length][destinations.length];

        for (int i = 0; i < origins.length; i++) {
            int ox = origins[i][0];
            int oy = origins[i][1];

            for (int j = 0; j < destinations.length; j++) {
                int dx = destinations[j][0];
                int dy = destinations[j][1];

                // Compute distance (choose one)
                int distance = manhattanDistance(ox, oy, dx, dy);
                // double distance = euclideanDistance(ox, oy, dx, dy);

                costMatrix[i][j] = distance;
            }
        }

        return costMatrix;
    }

    private static Map<Coordinate, Coordinate> applyHungarianAlgorithm(int[][] origins, int[][] destinations) {

        int[][] costMatrix = createCostMatrix(origins, destinations);
        Map<Coordinate, Coordinate> hungarianMap = new HashMap<>();
        HungarianAlgorithm hungarianAlgorithm = new HungarianAlgorithm(costMatrix);
        int[][] assignment = hungarianAlgorithm.findOptimalAssignment();
        if (assignment.length > 0) {
            for (int[] ints : assignment) {
                int originIndex = ints[0];
                int destinationIndex = ints[1];

                int[] origin = origins[originIndex];
                int[] destination = destinations[destinationIndex];

                hungarianMap.put(new Coordinate(origin[0], origin[1]), new Coordinate(destination[0], destination[1]));
            }

        } else {
            System.out.println("no assignment found!");
        }
        return hungarianMap;
    }


    private static int manhattanDistance(int x1, int y1, int x2, int y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }


    private static int euclideanDistance(int x1, int y1, int x2, int y2) {
        return (int) Math.hypot(x1 - x2, y1 - y2);
    }

    public static List<Agent> getHungarianAgents(int[][] origins, int[][] destinations) {
        Map<Coordinate, Coordinate> hungarianMap =
                HungarianSolver.applyHungarianAlgorithm(origins, destinations);

        List<Agent> agents = new ArrayList<>();
        int id = 0;
        for (Map.Entry<Coordinate, Coordinate> entry : hungarianMap.entrySet()) {
            Coordinate start = entry.getKey();
            Coordinate goal = entry.getValue();

            Agent agent = new Agent(id, start, goal);
            agents.add(agent);

            id++;
        }
        return agents;
    }
}
