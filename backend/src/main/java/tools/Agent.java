package tools;

public class Agent {

    int id;
    Coordinate start;
    Coordinate goal;
    int priority;
    String priorityStrategy; // "y-axis" or "manhattan"

    public Agent(int id, Coordinate start, Coordinate goal) {
        this(id, start, goal, "y-axis"); // Default to y-axis priority
    }

    public Agent(int id, Coordinate start, Coordinate goal, String priorityStrategy) {
        this.id = id;
        this.start = start;
        this.goal = goal;
        this.priorityStrategy = priorityStrategy;
        this.priority = calculatePriority();
    }

    private int calculatePriority() {
        if ("manhattan".equals(priorityStrategy)) {
            // Manhattan distance priority
            return Math.abs(start.x() - goal.x()) + Math.abs(start.y() - goal.y());
        } else {
            // Default y-axis priority
            return goal.y();
        }
    }

    public int getPriority() {
        return priority;
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

    public String getPriorityStrategy() {
        return priorityStrategy;
    }
}