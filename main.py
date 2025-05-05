import pygame
from typing import List, Tuple, Set
from algorithm_selector import AlgorithmSelector
from config import WIDTH, HEIGHT, CELL_SIZE, BACKGROUND, GRID_LINES
from request import Coordinate, AgentPath, call_cbs_api
from game import Game
from destination_selector import DestinationSelector
import time

def main():
    # Game restart loop
    while True:
        selector = DestinationSelector()
        origins, destinations, obstacles = selector.run()
        
        # Get the selected algorithm
        selected_algorithm = selector.get_selected_algorithm()
        
        # Get the morphing status
        morphing_enabled = selector.is_morphing_enabled()
        
        # Get the priority strategy
        priority_strategy = selector.get_selected_priority()
        
        # Get the conflict resolution strategy
        conflict_resolution = selector.get_selected_conflict_resolution()
        
        if not destinations:
            print("No destinations selected, using defaults.")
            origins = [
                [0, 8], [1, 8], [2, 8], [3, 8], [4, 8],
                [5, 8], [6, 8], [7, 8], [8, 8], [9, 8],
                [0, 9], [1, 9], [2, 9], [3, 9], [4, 9],
                [5, 9], [6, 9], [7, 9], [8, 9], [9, 9]
            ]
            destinations = [
                [3, 1], [4, 1], [5, 1],
                [2, 2], [6, 2],
                [1, 3], [7, 3],
                [2, 4], [6, 4],
                [3, 5], [4, 5], [5, 5],
                [2, 6], [6, 6],
                [1, 7], [7, 7],
                [2, 8], [6, 8],
                [3, 9], [4, 9]
            ]
            obstacles = []  # Default empty obstacles
        else:
            print(f"Selected {len(destinations)} destinations:")
            for i, dest in enumerate(destinations):
                print(f"  Destination {i+1}: [{dest[0]}, {dest[1]}]")
                
            if obstacles:
                print(f"Placed {len(obstacles)} obstacles:")
                for i, obs in enumerate(obstacles):
                    print(f"  Obstacle {i+1}: [{obs[0]}, {obs[1]}]")
        
        # Log the selected algorithm, morphing status, priority strategy, and conflict resolution strategy
        print(f"Using algorithm: {selected_algorithm}")
        print(f"Morphing enabled: {morphing_enabled}")
        print(f"Priority strategy: {priority_strategy}")
        print(f"Conflict resolution: {conflict_resolution}")
        
        # Create grid with obstacles marked
        grid = [[0 for _ in range(10)] for _ in range(10)]
        for obs in obstacles:
            x, y = obs
            if 0 <= x < 10 and 0 <= y < 10:  # Ensure obstacles are within grid bounds
                grid[y][x] = 1  # Mark obstacle cells with 1
        
        # Prepare payload for the API
        payload = {
            "grid": grid, 
            "origins": origins,
            "destinations": destinations,
            "algorithm": selected_algorithm,
            "morphing": morphing_enabled, 
            "priorityStrategy": priority_strategy,
            "conflictResolutionStrategy": conflict_resolution
        }
        
        start_time = time.time()
        agent_paths = call_cbs_api(payload)
        if agent_paths is None:
            print("Could not find path")
            continue  # Try again with new inputs
        else:
            end_time = time.time()
            print(f"Time taken to get agent paths: {end_time - start_time} seconds")
            
            # Debug info
            for agent in agent_paths:
                print(f"Agent {agent.agent_id}:")
                for coord in agent.path:
                    print(f"  Coordinate(x={coord.x}, y={coord.y})")
            
            # Pass obstacles to the Game constructor
            game = Game(agent_paths, obstacles)
            restart = game.run()
            
            # If restart was not requested, break out of the game loop
            if not restart:
                break

if __name__ == "__main__":
    main()