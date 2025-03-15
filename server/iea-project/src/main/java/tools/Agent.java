package tools;

public class Agent {

    int id;
    Coordinate start;
    Coordinate goal;
    int priority;

    public Agent(int id, Coordinate start, Coordinate goal) {
        this.id = id;
        this.start = start;
        this.goal = goal;
        this.priority = goal.y();
    }

    public int getPriority() {
        return goal.y();
    }

    public int id() {
        return id;
    }

    public Coordinate start() {
        return start;
    }

    public Coordinate goal() {
        return goal;
    }

}