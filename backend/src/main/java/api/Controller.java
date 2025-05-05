package api;

import cbs.Searcher;
import hungarian.HungarianSolver;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import tools.Agent;
import tools.Coordinate;

import java.util.List;
import java.util.Map;

@RestController
public class Controller {

    @PostMapping("/cbs")
    public ResponseEntity<Map<Integer, List<Coordinate>>> cbs(@RequestBody CbsRequest cbsRequest) {
        // Get priority strategy from request ("y-axis" if not provided)
        String priorityStrategy = cbsRequest.priorityStrategy() != null ?
                cbsRequest.priorityStrategy() : "y-axis";

        // Get conflict resolution strategy ("priority" if not provided)
        String conflictResolutionStrategy = cbsRequest.conflictResolutionStrategy() != null ?
                cbsRequest.conflictResolutionStrategy() : "priority";

        // Start timing
        long startTime = System.nanoTime();

        // Create agents with the specified priority strategy
        List<Agent> agents = HungarianSolver.getHungarianAgents(
                cbsRequest.origins(),
                cbsRequest.destinations(),
                priorityStrategy
        );

        Map<Integer, List<Coordinate>> cbs = Searcher.boostedCbs(
                cbsRequest.grid(),
                agents,
                cbsRequest.algorithm(), // "astar" or "bfs"
                cbsRequest.morphing(),  // morphing enabled or disabled
                conflictResolutionStrategy // "priority" or "minimax"
        );

        // End timing
        long endTime = System.nanoTime();

        double elapsedTimeMs = (endTime - startTime) / 1_000_000.0;

        // Print timing information
        System.out.println("CBS algorithm execution time: " + elapsedTimeMs + " ms");

        if (cbs == null || cbs.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        return ResponseEntity.ok(cbs);
    }
}
