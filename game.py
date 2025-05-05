import pygame
from typing import List, Optional, Dict, Tuple
from config import WIDTH, HEIGHT, CELL_SIZE, MOVE_INTERVAL, GRID_LINES, BACKGROUND
from cube import Cube
from request import Coordinate, AgentPath


class Game:
    def __init__(self, agent_paths: List[AgentPath], obstacles: List[List[int]]) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shapeshifter")
        self.clock = pygame.time.Clock()
        self.agent_paths = agent_paths
        
        # Store obstacles as (x, y) tuples for easier access
        self.obstacles = set((obs[0], obs[1]) for obs in obstacles)

        # Create cubes
        self.cubes = [Cube(path.agent_id, path.path, {}) for path in agent_paths]
        
        self.last_move_time = pygame.time.get_ticks()
        
        # Add pause functionality
        self.paused = False
        self.pause_button = pygame.Rect(WIDTH - 50, 10, 40, 40)
        self.font = pygame.font.SysFont('Arial', 16)
        
        # Timer functionality
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.pause_start_time = 0  # To track when pause begins
        
        # Add restart functionality
        self.show_restart = False
        self.restart_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 25, 150, 50)
        # Flag to signal when to restart
        self.restart_game = False
        
        # Flag to track if all agents have reached their destinations
        self.all_completed = False
        # Store the final completion time
        self.completion_time = 0

    def run(self) -> bool:
        """Main game loop. Returns True if restart was requested."""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button.collidepoint(event.pos):
                        if not self.paused:
                            self.pause_start_time = current_time
                        else:
                            pause_duration = current_time - self.pause_start_time
                            self.start_time += pause_duration
                        
                        self.paused = not self.paused
                    
                    # Check if restart button was clicked
                    if self.show_restart and self.restart_button.collidepoint(event.pos):
                        return True  # Signal to restart the game
                        
            if not self.paused:
                # Only update elapsed time if not all agents have reached destination
                if not self.all_completed:
                    self.elapsed_time = current_time - self.start_time
                
                for cube in self.cubes:
                    cube.update()

                if current_time - self.last_move_time >= MOVE_INTERVAL:
                    all_cubes_stable = all(not cube.is_moving for cube in self.cubes)
                    if all_cubes_stable:
                        for cube in self.cubes:
                            cube.move()
                        self.last_move_time = current_time
                        
                        # Check for overlaps after moving all cubes
                        self.check_overlaps()
                
                # Check if all agents have reached their destinations
                if self.all_agents_reached() and not self.all_completed:
                    self.all_completed = True
                    self.completion_time = self.elapsed_time  # Store the completion time
                    self.show_restart = True

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return False

    def all_agents_reached(self) -> bool:
        """Check if all agents have reached their destinations."""
        return all(cube.is_reached() for cube in self.cubes)

    def draw(self) -> None:
        """Draw the grid, obstacles, cubes, and labels."""
        self.draw_grid()
        self.draw_obstacles()
        self.draw_destinations()
        for cube in self.cubes:
            cube.draw(self.screen)
        self.draw_stats()
        self.draw_timer()  
        self.draw_pause_button()
        
        # Draw restart button if all agents have reached their destinations
        if self.show_restart:
            self.draw_restart_button()
    
    def draw_restart_button(self) -> None:
        """Draw the restart button when all agents have reached their destinations."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))  # Black with 60% opacity
        self.screen.blit(overlay, (0, 0))
        
        # Draw the button
        pygame.draw.rect(self.screen, (50, 150, 50), self.restart_button, border_radius=10)
        pygame.draw.rect(self.screen, (30, 100, 30), self.restart_button, width=2, border_radius=10)
        
        # Button text
        font = pygame.font.SysFont('Arial', 24)
        restart_text = font.render("Restart", True, (255, 255, 255))
        text_rect = restart_text.get_rect(center=self.restart_button.center)
        self.screen.blit(restart_text, text_rect)
        
        # Congratulations text
        congrats_font = pygame.font.SysFont('Arial', 32)
        congrats_text = congrats_font.render("All agents reached destinations!", True, (255, 255, 255))
        congrats_rect = congrats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.screen.blit(congrats_text, congrats_rect)
        
        # Display completion time - use the stored completion time
        time_font = pygame.font.SysFont('Arial', 24)
        minutes = self.completion_time // 60000
        seconds = (self.completion_time % 60000) // 1000
        time_text = time_font.render(f"Completion time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(time_text, time_rect)
        
    
    def draw_obstacles(self) -> None:
        """Draw the obstacles on the grid."""
        for x, y in self.obstacles:
            obstacle_rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                                      CELL_SIZE - 4, CELL_SIZE - 4)
            pygame.draw.rect(self.screen, (80, 80, 80), obstacle_rect)
            
            # Add a cross pattern to make obstacles more visually distinct
            pygame.draw.line(self.screen, (40, 40, 40), 
                          (x * CELL_SIZE + 2, y * CELL_SIZE + 2),
                          (x * CELL_SIZE + CELL_SIZE - 4, y * CELL_SIZE + CELL_SIZE - 4), 3)
            pygame.draw.line(self.screen, (40, 40, 40), 
                          (x * CELL_SIZE + CELL_SIZE - 4, y * CELL_SIZE + 2),
                          (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 4), 3)

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
        Draw the pause/play button with appropriate icon and color.
        """
        button_color = (220, 50, 50) if self.paused else (50, 200, 50) 
        pygame.draw.rect(self.screen, button_color, self.pause_button, border_radius=5)
        
        icon_color = (255, 255, 255)  
        if not self.paused:
            # play triangle icon
            play_icon_points = [
                (self.pause_button.left + 12, self.pause_button.top + 10),
                (self.pause_button.left + 12, self.pause_button.bottom - 10),
                (self.pause_button.right - 10, self.pause_button.centery)
            ]
            pygame.draw.polygon(self.screen, icon_color, play_icon_points)
        else:
            # pause bars
            bar_width = 6
            bar_height = 20
            gap = 4
            bar_y = self.pause_button.centery - bar_height // 2
            
            left_bar = pygame.Rect(
                self.pause_button.centerx - bar_width - gap//2,
                bar_y,
                bar_width, 
                bar_height
            )
            
            right_bar = pygame.Rect(
                self.pause_button.centerx + gap//2,
                bar_y,
                bar_width, 
                bar_height
            )
            
            pygame.draw.rect(self.screen, icon_color, left_bar)
            pygame.draw.rect(self.screen, icon_color, right_bar)
            
    def draw_timer(self) -> None:
        """
        Draw the timer showing elapsed time below the stats.
        """
        # If all agents have reached their destinations, use the stored completion time
        # Otherwise, use the current elapsed time
        display_time = self.completion_time if self.all_completed else self.elapsed_time
        
        seconds = display_time // 1000
        minutes = seconds // 60
        seconds %= 60
        
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        
        if self.paused:
            timer_text += " (PAUSED)"
            
        font = pygame.font.SysFont('Arial', 16)
        
        shadow_surf = font.render(timer_text, True, (0, 0, 0))
        self.screen.blit(shadow_surf, (11, 31))
        
        timer_surf = font.render(timer_text, True, (255, 255, 255))
        self.screen.blit(timer_surf, (10, 30))

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