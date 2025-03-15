package cbs;

import tools.Conflict;
import tools.Coordinate;

import java.util.List;
import java.util.Map;

public class ConflictDetector {

    public static Conflict detectConflict(
            Map<Integer, List<Coordinate>> paths, Map<Integer, Integer> priorities) {

        for (Map.Entry<Integer, List<Coordinate>> entry1 : paths.entrySet()) {
            int agent1 = entry1.getKey();
            List<Coordinate> path1 = entry1.getValue();
            for (Map.Entry<Integer, List<Coordinate>> entry2 : paths.entrySet()) {
                int agent2 = entry2.getKey();
                if (agent1 >= agent2) continue;
                List<Coordinate> path2 = entry2.getValue();
                int maxTime = Math.min(path1.size(), path2.size());
                for (int t = 0; t < maxTime; t++) {
                    Coordinate pos1 = path1.get(t);
                    Coordinate pos2 = path2.get(t);
                    if (pos1.equals(pos2)) {
                        int prio1 = priorities.get(agent1);
                        int prio2 = priorities.get(agent2);

                        int agentLow = (prio1 > prio2) ? agent1 : agent2;
                        int agentHigh = (agentLow == agent1) ? agent2 : agent1;
                        return new Conflict(agentLow, agentHigh, Coordinate.with(pos1.x(), pos1.y()), t);
                    }
                }
            }
        }
        return null; // No conflicts!
    }
}
