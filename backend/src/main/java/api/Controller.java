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
                cbsRequest.morphing()   // morphing enabled or disabled
        );

        if (cbs == null || cbs.isEmpty()) {
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
        return ResponseEntity.ok(cbs);
    }
}