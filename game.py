import pygame
from typing import List, Optional, Dict, Tuple, Set
from config import WIDTH, HEIGHT, CELL_SIZE, MOVE_INTERVAL, GRID_LINES, BACKGROUND
from cube import Cube
from request import Coordinate, AgentPath


class Game:
    """
    Main game class that manages the game window, cube objects, and game loop.
    """

    def __init__(self, agent_paths: List[AgentPath]) -> None:
        """
        Initialize the game with agent paths and simulation settings.
        
        Args:
            agent_paths: A list of AgentPath objects, each containing an agent ID and a list of Coordinates.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shapeshifter")
        self.clock = pygame.time.Clock()
        self.agent_paths = agent_paths  # List of AgentPath objects

        # Dictionary to track which positions are occupied (key is a tuple (x, y))
        self.occupied_positions: Dict[Tuple[int, int], Cube] = {}

        self.cubes = self.create_cubes()
        self.selected_cube: Optional[Cube] = None
        self.last_move_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()  # Track when simulation started

    def create_cubes(self) -> List[Cube]:
        """
        Create Cube objects from the agent_paths list.
        """
        cubes = []
        for agent_path in self.agent_paths:
            cube = Cube(agent_path.agent_id, agent_path.path, self.occupied_positions)
            cubes.append(cube)
            self.occupied_positions[(cube.grid_x, cube.grid_y)] = cube
        return cubes

    def run(self) -> None:
        """
        Main game loop.
        """
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if current_time - self.last_move_time >= MOVE_INTERVAL:
                self.update_cubes()
                self.last_move_time = current_time

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def update_cubes(self) -> None:
        """
        Move cubes along their path at intervals.
        """
        cubes_to_move = [c for c in self.cubes if not c.is_reached() and c != self.selected_cube]
        cubes_to_move.sort(key=lambda c: c.distance_to_destination())

        for cube in cubes_to_move:
            old_pos = (cube.grid_x, cube.grid_y)
            cube.move(self.occupied_positions)
            new_pos = (cube.grid_x, cube.grid_y)
            if old_pos != new_pos:
                self.update_occupied_positions(cube, old_pos, new_pos)

    def update_occupied_positions(self, cube: Cube, old_pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        """
        Update the occupied positions dictionary when a cube moves.
        """
        if old_pos in self.occupied_positions:
            del self.occupied_positions[old_pos]
        self.occupied_positions[new_pos] = cube

    def draw(self) -> None:
        """
        Draw the grid, cubes, and labels.
        """
        self.draw_grid()
        self.draw_destinations()
        for cube in self.cubes:
            cube.draw(self.screen)
        self.draw_stats()

    def draw_grid(self) -> None:
        """
        Draw the grid lines and background.
        """
        self.screen.fill(BACKGROUND)
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINES, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_LINES, (0, y), (WIDTH, y))

    def draw_destinations(self) -> None:
        """
        Draw labels for agent destinations.
        """
        font = pygame.font.SysFont('Arial', 16)
        for cube in self.cubes:
            dest_x, dest_y = cube.destination
            label = font.render(f"{cube.cube_id + 1}", True, (255, 255, 255))
            label_rect = label.get_rect(center=(dest_x * CELL_SIZE + CELL_SIZE // 2,
                                                dest_y * CELL_SIZE + CELL_SIZE // 2))
            self.screen.blit(label, label_rect)

    def draw_stats(self) -> None:
        """
        Display stats about completed paths and elapsed time.
        """
        font = pygame.font.SysFont('Arial', 16)
        
        # Completed cubes
        completed = sum(
            1 for cube in self.cubes if cube.is_reached() and (cube.grid_x, cube.grid_y) == cube.destination)
        stats_text = f"Completed: {completed}/{len(self.cubes)}"
        stats_surf = font.render(stats_text, True, (255, 255, 255))
        self.screen.blit(stats_surf, (10, 10))
        
        # Elapsed time
        elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000  # Convert to seconds
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        time_surf = font.render(time_text, True, (255, 255, 255))
        self.screen.blit(time_surf, (10, 30))