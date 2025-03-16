import pygame
from typing import List, Optional, Dict, Tuple
from config import WIDTH, HEIGHT, CELL_SIZE, MOVE_INTERVAL, GRID_LINES, BACKGROUND
from cube import Cube
from request import Coordinate, AgentPath


class Game:
    def __init__(self, agent_paths: List[AgentPath]) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shapeshifter")
        self.clock = pygame.time.Clock()
        self.agent_paths = agent_paths

        # Create cubes
        self.cubes = [Cube(path.agent_id, path.path, {}) for path in agent_paths]
        
        self.last_move_time = pygame.time.get_ticks()
        
        # Add pause functionality
        self.paused = False
        self.pause_button = pygame.Rect(WIDTH - 110, 10, 100, 30)
        self.font = pygame.font.SysFont('Arial', 16)

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if pause button was clicked
                    if self.pause_button.collidepoint(event.pos):
                        self.paused = not self.paused
                        
            # Only move cubes when not paused
            if not self.paused and current_time - self.last_move_time >= MOVE_INTERVAL:
                for cube in self.cubes:
                    cube.move()
                self.last_move_time = current_time
                
                # Check for overlaps after moving all cubes
                self.check_overlaps()

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def draw(self) -> None:
        """Draw the grid, cubes, and labels."""
        self.draw_grid()
        self.draw_destinations()
        for cube in self.cubes:
            cube.draw(self.screen)
        self.draw_stats()
        self.draw_pause_button()


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
        Display stats about completed paths.
        """
        font = pygame.font.SysFont('Arial', 16)
        completed = sum(
            1 for cube in self.cubes if cube.is_reached() and (cube.grid_x, cube.grid_y) == cube.destination)
        stats_text = f"Completed: {completed}/{len(self.cubes)}"
        stats_surf = font.render(stats_text, True, (255, 255, 255))
        self.screen.blit(stats_surf, (10, 10))
        
    def draw_pause_button(self) -> None:
        """
        Draw the pause/play button.
        """
        # Draw button background
        button_color = (100, 100, 100)
        pygame.draw.rect(self.screen, button_color, self.pause_button, border_radius=5)
        
        # Draw button text
        button_text = "Resume" if self.paused else "Pause"
        text_surf = self.font.render(button_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.pause_button.center)
        self.screen.blit(text_surf, text_rect)

    # In Game class, add a method to check for overlaps
    def check_overlaps(self):
        """Check for cubes that occupy the same cell and mark them."""
        positions = {}
        for cube in self.cubes:
            pos = (cube.grid_x, cube.grid_y)
            if pos in positions:
                # Mark both cubes as overlapping
                cube.overlapping = True
                positions[pos].overlapping = True
            else:
                positions[pos] = cube
                cube.overlapping = False