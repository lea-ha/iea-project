import requests
from dataclasses import dataclass
from typing import List, Dict
import json

url = "http://localhost:8080/cbs"

@dataclass
class Coordinate:
    x: int
    y: int

@dataclass
class AgentPath:
    agent_id: int
    path: List[Coordinate]


def parse_agent_paths(response_data: Dict[str, List[Dict[str, int]]]) -> List[AgentPath]:
    agent_paths = []
    for agent_id_str, coord_list in response_data.items():
        agent_id = int(agent_id_str)
        path = [Coordinate(**coord) for coord in coord_list]
        agent_paths.append(AgentPath(agent_id, path))
    return agent_paths

def call_cbs_api(payload):
    response = requests.post(url, json=payload)
    if response.ok:
        print("Success!")
        response_json = response.json()
        agent_paths = parse_agent_paths(response_json)
        return agent_paths
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None