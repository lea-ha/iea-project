package pathfinding;

import tools.Coordinate;

import java.util.ArrayList;
import java.util.List;

public class Node {
    Coordinate coordinate;
    int g;
    List<Node> path;

    public Node(Coordinate coordinate, int g, List<Node> path) {
        this.coordinate = coordinate;
        this.g = g;
        this.path = new ArrayList<>(path);
    }
}