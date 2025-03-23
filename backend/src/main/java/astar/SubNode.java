package astar;

import tools.Coordinate;

import java.util.Objects;

public class SubNode {
    public Coordinate coordinate;
    public int g;

    public SubNode(Coordinate coordinate, int g) {
        this.coordinate = coordinate;
        this.g = g;
    }

    public static SubNode of(Coordinate coordinate, int g) {
        return new SubNode(coordinate, g);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof SubNode)) return false;
        SubNode subNode = (SubNode) o;
        return g == subNode.g &&
                Objects.equals(coordinate, subNode.coordinate);
    }

    @Override
    public int hashCode() {
        return Objects.hash(coordinate, g);
    }
}