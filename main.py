from game import Game
from request import call_cbs_api
from destination_selector import DestinationSelector

if __name__ == "__main__":
    selector = DestinationSelector()
    origins, destinations = selector.run()
    
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
    
    # Prepare payload for the API
    payload = {
        "grid": [[0 for _ in range(10)] for _ in range(10)],
        "origins": origins,
        "destinations": destinations
    }
    
    # Call the API to get agent paths
    agent_paths = call_cbs_api(payload)
    
    # Debug information
    for agent in agent_paths:
        print(f"Agent {agent.agent_id}:")
        for coord in agent.path:
            print(f"  Coordinate(x={coord.x}, y={coord.y})")
    
    # Run the game with the generated paths
    game = Game(agent_paths)
    game.run()