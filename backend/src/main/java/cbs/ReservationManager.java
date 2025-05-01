package cbs;

import pathfinding.SubNode;
import tools.Coordinate;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ReservationManager {

    int[][] grid;
    Map<SubNode, Integer> reservations = new HashMap<>();
    List<SubNode> morphicPositions = new ArrayList<>();

    public ReservationManager(int[][] grid) {
        this.grid = grid;
    }

    public void clearReservations(){
        reservations.clear();
    }

    public void addReservation(SubNode node, Integer agentId) {
        reservations.put(node, agentId);
        updateMorphicPositions();
    }

    public void addAllReservations(Map<SubNode, Integer> newReservations) {
        reservations.putAll(newReservations);
        updateMorphicPositions();
    }

    private void updateMorphicPositions() {
        if (!morphicPositions.isEmpty()) {
            morphicPositions.clear();
        }
        reservations.forEach((k, v) -> morphicPositions.addAll(getMorphicNeighbors(k)));
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

    public Map<SubNode, Integer> getReservations() {
        return reservations;
    }

    public List<SubNode> getMorphicPositions() {
        return morphicPositions;
    }
}
