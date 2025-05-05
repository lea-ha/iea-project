package cbs;

import tools.Conflict;
import tools.Coordinate;
import tools.Agent;

import java.util.List;
import java.util.Map;

public class ConflictDetector {

    public static Conflict detectConflict(
            Map<Integer, List<Coordinate>> paths, Map<Integer, Integer> priorities) {
        return detectConflict(paths, priorities, "priority", null, null);
    }

    public static Conflict detectConflict(
            Map<Integer, List<Coordinate>> paths, Map<Integer, Integer> priorities,
            String conflictResolutionStrategy, int[][] grid, List<Agent> agents) {

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
                        int agentLow, agentHigh;

                        if ("minimax".equals(conflictResolutionStrategy) && grid != null && agents != null) {
                            // Find the agent objects
                            Agent agentObj1 = findAgentById(agents, agent1);
                            Agent agentObj2 = findAgentById(agents, agent2);

                            if (agentObj1 != null && agentObj2 != null) {
                                MinimaxConflictResolver resolver = new MinimaxConflictResolver(grid, 3); // depth of 3
                                Conflict tempConflict = new Conflict(
                                        agent1, agent2, Coordinate.with(pos1.x(), pos1.y()), t);

                                int constrainedAgent = resolver.resolveConflict(
                                        agentObj1, agentObj2, tempConflict, paths);

                                agentLow = constrainedAgent;
                                agentHigh = (constrainedAgent == agent1) ? agent2 : agent1;
                            } else {
                                // Fallback to priority-based resolution
                                int prio1 = priorities.get(agent1);
                                int prio2 = priorities.get(agent2);

                                agentLow = (prio1 > prio2) ? agent1 : agent2;
                                agentHigh = (agentLow == agent1) ? agent2 : agent1;
                            }
                        } else {
                            // Use the standard priority-based resolution
                            int prio1 = priorities.get(agent1);
                            int prio2 = priorities.get(agent2);

                            agentLow = (prio1 > prio2) ? agent1 : agent2;
                            agentHigh = (agentLow == agent1) ? agent2 : agent1;
                        }

                        return new Conflict(agentLow, agentHigh, Coordinate.with(pos1.x(), pos1.y()), t);
                    }
                }
            }
        }

        return null; // No conflicts!
    }

    private static Agent findAgentById(List<Agent> agents, int id) {
        for (Agent agent : agents) {
            if (agent.id() == id) {
                return agent;
            }
        }
        return null;
    }
}