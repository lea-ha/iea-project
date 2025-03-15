from game import Game
from destination_selector import DestinationSelector
from request import call_cbs_api

if __name__ == "__main__":
    # Create a selector for destination selection
    selector = DestinationSelector()
    origins, destinations = selector.run()
    
    # If user didn't quit during selection
    if origins and destinations:
        # Create payload for API in the same format as before
        payload = {
            "grid": [[0 for _ in range(10)] for _ in range(10)],
            "origins": origins,
            "destinations": destinations
        }
        
        # Call the API using the payload
        agent_paths = call_cbs_api(payload)
        
        if agent_paths:
            # For debugging, print the paths
            for agent in agent_paths:
                print(f"Agent {agent.agent_id}:")
                for coord in agent.path:
                    print(f"  Coordinate(x={coord.x}, y={coord.y})")
            
            # Create and run the game with the paths
            game = Game(agent_paths)
            game.run()
        else:
            print("Failed to get paths from API")