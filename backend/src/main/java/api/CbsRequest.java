package api;

public record CbsRequest(
        int[][] grid,
        int[][] origins,
        int[][] destinations,
        String algorithm,
        boolean morphing,
        String priorityStrategy,
        String conflictResolutionStrategy,
        boolean allowDiagonals
) {}