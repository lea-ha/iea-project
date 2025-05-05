package cbs;

// Local Imports
import tools.*;

import java.util.*;

public class MinimaxConflictResolver {

    private final int maxDepth; // Depth of the tree (max search depth)
    private final int[][] grid;

    public MinimaxConflictResolver(int[][] grid, int maxDepth) {
        this.grid = grid;
        this.maxDepth = maxDepth; // tree's depth
    }

    public int resolveConflict(Agent agent1, Agent agent2, Conflict conflict,
                               Map<Integer, List<Coordinate>> currentPaths) {
        // We'll treat agent1 as the maximizing player and agent2 as the minimizing player
        int score = minimax(agent1, agent2, conflict, currentPaths, 0, true,
                Integer.MIN_VALUE, Integer.MAX_VALUE);

        // If the score is positive, agent1 wins (agent2 should be constrained)
        // If the score is negative, agent2 wins (agent1 should be constrained)
        return score >= 0 ? agent2.id() : agent1.id();
    }

    private int minimax(Agent agent1, Agent agent2, Conflict conflict,
                        Map<Integer, List<Coordinate>> currentPaths,
                        int depth, boolean isMaximizingPlayer, int alpha, int beta) {

        // Terminal conditions
        if (depth >= maxDepth) {
            return evaluateState(agent1, agent2, conflict, currentPaths);
        }

        // Get possible moves for the current player
        Agent currentAgent = isMaximizingPlayer ? agent1 : agent2;
        List<Coordinate> possibleMoves = generatePossibleMoves(currentAgent, conflict, currentPaths);

        if (isMaximizingPlayer) {
            int maxEval = Integer.MIN_VALUE;
            for (Coordinate move : possibleMoves) {
                // Create a copy of current paths and apply the move
                Map<Integer, List<Coordinate>> newPaths = applyMove(currentPaths, currentAgent.id(), move, conflict.t);

                // Recursive minimax call
                int eval = minimax(agent1, agent2, conflict, newPaths, depth + 1, false, alpha, beta);
                maxEval = Math.max(maxEval, eval);

                // Alpha-beta pruning
                alpha = Math.max(alpha, eval);
                if (beta <= alpha) {
                    break;
                }
            }
            return maxEval;
        } else {
            int minEval = Integer.MAX_VALUE;
            for (Coordinate move : possibleMoves) {
                // Create a copy of current paths and apply the move
                Map<Integer, List<Coordinate>> newPaths = applyMove(currentPaths, currentAgent.id(), move, conflict.t);

                // Recursive minimax call
                int eval = minimax(agent1, agent2, conflict, newPaths, depth + 1, true, alpha, beta);
                minEval = Math.min(minEval, eval);

                // Alpha-beta pruning
                beta = Math.min(beta, eval);
                if (beta <= alpha) {
                    break;
                }
            }
            return minEval;
        }
    }

    private List<Coordinate> generatePossibleMoves(Agent agent, Conflict conflict,
                                                   Map<Integer, List<Coordinate>> currentPaths) {
        List<Coordinate> possibleMoves = new ArrayList<>();
        int time = conflict.t;

        // Get the current position at time t-1 (or start position if t=0)
        Coordinate currentPos;
        if (time > 0) {
            List<Coordinate> agentPath = currentPaths.get(agent.id());
            currentPos = time - 1 < agentPath.size() ? agentPath.get(time - 1) : agent.start();
        } else {
            currentPos = agent.start();
        }

        int[][] directions = {{0, 0}, {0, 1}, {1, 0}, {0, -1}, {-1, 0}};

        for (int[] dir : directions) {
            int newX = currentPos.x() + dir[0];
            int newY = currentPos.y() + dir[1];

            // Check if the new position is valid
            if (isValidPosition(newX, newY)) {
                possibleMoves.add(Coordinate.with(newX, newY));
            }
        }

        return possibleMoves;
    }

    private boolean isValidPosition(int x, int y) {
        return x >= 0 && x < grid.length && y >= 0 && y < grid[0].length && grid[y][x] != 1;
    }

    private Map<Integer, List<Coordinate>> applyMove(Map<Integer, List<Coordinate>> currentPaths,
                                                     int agentId, Coordinate move, int time) {
        Map<Integer, List<Coordinate>> newPaths = new HashMap<>();

        for (Map.Entry<Integer, List<Coordinate>> entry : currentPaths.entrySet()) {
            int id = entry.getKey();
            List<Coordinate> path = new ArrayList<>(entry.getValue());

            if (id == agentId) {
                // Modify the path for this agent
                while (path.size() <= time) {
                    path.add(path.get(path.size() - 1));
                }
                path.set(time, move);
            }

            newPaths.put(id, path);
        }

        return newPaths;
    }

    // Evaluate the current state based on various heuristics (including y axis, manhattan...)
    // Returns a positive score if agent1 is favored, negative if agent2 is favored.
    private int evaluateState(Agent agent1, Agent agent2, Conflict conflict,
                              Map<Integer, List<Coordinate>> currentPaths) {
        int score = 0;

        // Factor 1: Distance to goal
        List<Coordinate> path1 = currentPaths.get(agent1.id());
        List<Coordinate> path2 = currentPaths.get(agent2.id());

        Coordinate pos1 = path1.get(Math.min(conflict.t, path1.size() - 1));
        Coordinate pos2 = path2.get(Math.min(conflict.t, path2.size() - 1));

        int distToGoal1 = manhattanDistance(pos1, agent1.goal());
        int distToGoal2 = manhattanDistance(pos2, agent2.goal());

        // Lower distance to goal is better, so subtract agent1's distance and add agent2's
        score += (distToGoal2 - distToGoal1);

        // Factor 2: Path length comparison
        int pathLength1 = path1.size();
        int pathLength2 = path2.size();
        score += (pathLength2 - pathLength1) * 2;

        // Factor 3: Priority-based weight
        int priority1 = agent1.getPriority();
        int priority2 = agent2.getPriority();
        score += (priority2 - priority1) * 3;

        return score;
    }

    private int manhattanDistance(Coordinate a, Coordinate b) {
        return Math.abs(a.x() - b.x()) + Math.abs(a.y() - b.y());
    }
}