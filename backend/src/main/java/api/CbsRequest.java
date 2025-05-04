package api;

public record CbsRequest(
        int[][] grid,
        int[][] origins,
        int[][] destinations,
        String algorithm,
        boolean morphing,
        String priorityStrategy // "y-axis" or "manhattan"
) {

}