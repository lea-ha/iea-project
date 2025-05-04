package cbs;

import pathfinding.SubNode;
import tools.Agent;
import tools.Coordinate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ReservationManager {
    private int[][] grid;
    private Map<SubNode, Integer> reservations = new HashMap<>();
    private List<SubNode> morphicPositions = new ArrayList<>();
    private boolean morphingEnabled;

    public ReservationManager(int[][] grid, boolean morphingEnabled) {
        this.grid = grid;
        this.morphingEnabled = morphingEnabled;
        if (morphingEnabled) {
            updateMorphicPositions();
        }
    }

    public void clearReservations() {
        reservations.clear();
        if (morphingEnabled) {
            morphicPositions.clear();
        }
    }

    public void addReservation(SubNode node, Integer agentId) {
        reservations.put(node, agentId);
        if (morphingEnabled) {
            updateMorphicPositions();
        }
    }

    public void addAllReservations(Map<SubNode, Integer> newReservations) {
        reservations.putAll(newReservations);
        if (morphingEnabled) {
            updateMorphicPositions();
        }
    }

    public void addAllMorphicPositions(List<SubNode> morphicPositions) {
        this.morphicPositions.addAll(morphicPositions);
    }

    private void updateMorphicPositions() {
        if (!morphicPositions.isEmpty()) {
            morphicPositions.clear();
        }
        reservations.forEach((k, v) -> morphicPositions.addAll(getMorphicNeighbors(k)));
    }

    public Map<SubNode, Integer> getReservations() {
        return reservations;
    }

    public List<SubNode> getMorphicPositions() {
        return morphicPositions;
    }

    public boolean isMorphicToMove(SubNode node, Agent agent) {
        int nodeTime = node.g;
        Coordinate nodeCoordinate = node.coordinate;
        for (Map.Entry<SubNode, Integer> entry : reservations.entrySet()) {
            if (entry.getKey().g != nodeTime) {
                continue;
            }
            if (entry.getValue() == agent.id()) {
                return true;
            }
            if (entry.getValue() != agent.id()) {
                List<SubNode> morphicNeighbors = getMorphicNeighbors(entry.getKey());
                if (morphicNeighbors.contains(SubNode.of(nodeCoordinate, nodeTime+1))) {
                    return true;
                }
            }
        }
        return false;
    }

    public boolean isMorphingEnabled() {
        return morphingEnabled;
    }

    private List<SubNode> getMorphicNeighbors(SubNode node) {
        int[][] directions = {{0,-1},{0,1},{-1,0},{1,0},{-1,-1}, {1,-1},{-1,1},{1,1}, {0,0}};
        List<SubNode> neighbors = new ArrayList<>();
        Coordinate currentCoordinate = node.coordinate;
        int time = node.g + 1;
        for (int[] direction : directions) {
            int nx = currentCoordinate.x() + direction[0];
            int ny = currentCoordinate.y() + direction[1];
            if (nx >= 0 && nx < grid.length && ny >= 0 && ny < grid[0].length && grid[ny][nx] != 1) {
                neighbors.add(SubNode.of(Coordinate.with(nx, ny), time));
            }
        }
        return neighbors;
    }
}