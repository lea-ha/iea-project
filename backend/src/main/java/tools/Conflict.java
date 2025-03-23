package tools;

public class Conflict {
    public int agentLow;
    public int agentHigh;
    public Coordinate coordinate;
    public int t;

    public Conflict(int agentLow, int agentHigh, Coordinate coordinate, int t) {
        this.agentLow = agentLow;
        this.agentHigh = agentHigh;
        this.coordinate = coordinate;
        this.t = t;
    }
}