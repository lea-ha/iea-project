package tools;

import java.util.List;
import java.util.Map;

public record CBSNode(Map<Integer, List<Coordinate>> agentIdToPath, List<Constraint> constraints, int totalCost) implements Comparable<CBSNode> {

    @Override
    public int compareTo(CBSNode other) {
        return Integer.compare(this.totalCost, other.totalCost);
    }
}
