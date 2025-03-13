import pygame
from typing import List

from request import call_cbs_api

# Constants
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
BACKGROUND_COLOR = (30, 30, 30)
AGENT_COLOR = (0, 255, 0)
MOVE_INTERVAL = 50  # milliseconds


class Agent:
    def __init__(self, agent_path):
        self.path = agent_path.path
        self.index = 0
        self.x, self.y = self.path[0].x, self.path[0].y

    def move(self):
        if self.index < len(self.path) - 1:
            self.index += 1
            self.x, self.y = self.path[self.index].x, self.path[self.index].y

    def draw(self, screen):
        pygame.draw.rect(screen, AGENT_COLOR, (self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def main(agent_paths: List):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True
    agents = [Agent(path) for path in agent_paths]  # Fix: Iterate over the list
    last_move_time = pygame.time.get_ticks()

    while running:
        screen.fill(BACKGROUND_COLOR)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks()
        if current_time - last_move_time >= MOVE_INTERVAL:
            for agent in agents:
                agent.move()
            last_move_time = current_time

        for agent in agents:
            agent.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# Example usage
if __name__ == "__main__":
    payload = {
        "grid": [[0 for _ in range(10)] for _ in range(10)],
        "origins": [
            [0, 8], [1, 8], [2, 8], [3, 8], [4, 8],
            [5, 8], [6, 8], [7, 8], [8, 8], [9, 8],
            [0, 9], [1, 9], [2, 9], [3, 9], [4, 9],
            [5, 9], [6, 9], [7, 9], [8, 9], [9, 9]
        ],
        "destinations": [
            [1, 1], [2, 1], [3, 1], [4, 2], [5, 3], [5, 4], [4, 5], [3, 6], [2, 6], [1, 5],
            [0, 4], [0, 3], [0, 2], [1, 0], [2, 0], [3, 0], [4, 1], [5, 2], [4, 4], [3, 5]

        ]
    }
    agent_paths = call_cbs_api(payload)
    main(agent_paths)
