import pygame
from typing import List, Tuple, Set
from algorithm_selector import AlgorithmSelector
from config import WIDTH, HEIGHT, CELL_SIZE, BACKGROUND, GRID_LINES
from request import Coordinate, AgentPath, call_cbs_api
from game import Game
from destination_selector import DestinationSelector
import time

def main():
    selector = DestinationSelector()
    origins, destinations = selector.run()
    
    # Get the selected algorithm
    selected_algorithm = selector.get_selected_algorithm()
    
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
    else:
        print(f"Selected {len(destinations)} destinations:")
        for i, dest in enumerate(destinations):
            print(f"  Destination {i+1}: [{dest[0]}, {dest[1]}]")
    
    # Log the selected algorithm
    print(f"Using algorithm: {selected_algorithm}")
    
    # Prepare payload for the API
    payload = {
        "grid": [[0 for _ in range(10)] for _ in range(10)],
        "origins": origins,
        "destinations": destinations,
        "algorithm": selected_algorithm  # Include the selected algorithm in the payload
    }
    
    start_time = time.time()
    agent_paths = call_cbs_api(payload)
    if agent_paths is None:
        print("Could not find path")
        main()
    else:
        end_time = time.time()
        print(f"Time taken to get agent paths: {end_time - start_time} seconds")
    
        # Debug info
        for agent in agent_paths:
            print(f"Agent {agent.agent_id}:")
            for coord in agent.path:
                print(f"  Coordinate(x={coord.x}, y={coord.y})")
    
        game = Game(agent_paths)
        game.run()

if __name__ == "__main__":
    main()