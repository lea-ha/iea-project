import pygame
from typing import List, Optional, Dict, Set, Tuple
from config import WIDTH, HEIGHT, CELL_SIZE, GRID_COLS, GRID_ROWS, MOVE_INTERVAL, GRID_LINES, BACKGROUND, CUBE_COUNT
from cube import Cube
from hungarian_algorithm import hungarian_algorithm, create_cost_matrix, manhattan_distance


class Game:
    """
    Main game class that manages the game window, cube objects, and game loop.
    
    This class handles initializing the game, creating cubes, drawing the grid,
    processing user input, and updating the game state.
    
    Attributes:
        screen (pygame.Surface): The main game display surface
        clock (pygame.time.Clock): Clock for controlling frame rate
        cubes (List[Cube]): List of cube objects in the game
        selected_cube (Optional[Cube]): Currently selected cube or None
        last_move_time (int): Timestamp of the last automatic movement
        occupied_positions (Dict[Tuple[int, int], Cube]): Tracks which grid positions are occupied
    """
    
    def __init__(self) -> None:
        """
        Initialize the game by setting up pygame, creating the display window,
        and initializing game objects.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shapeshifter")
        self.clock = pygame.time.Clock()

        # Dictionary to track which positions are occupied and by which cube
        self.occupied_positions: Dict[Tuple[int, int], Cube] = {}

        self.cubes = self.create_cubes()
        self.selected_cube: Optional[Cube] = None
        self.last_move_time = pygame.time.get_ticks()
        
    def create_cubes(self) -> List[Cube]:
        """
        Create and initialize multiple cube objects for the game.
        
        Returns:
            A list containing the initialized cube objects
        """
        cubes = []
        used_positions = set()
        
        # Predetermined destinations (rectangle in the center in this case)
        destinations = [
            (3, 1), (4, 1), (5, 1), (6, 1),
            (3, 2), (4, 2), (5, 2), (6, 2),
            (3, 3), (4, 3), (5, 3), (6, 3),
            (3, 4), (4, 4), (5, 4), (6, 4),
            (3, 5), (4, 5), (5, 5), (6, 5)
        ]
        
        # Define predetermined starting positions (Here, bottom 2 rows) (This wont be changed we always want them here)
        origins = [
            (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8),  
            (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9)
        ]
        cost_matrix = create_cost_matrix(origins, destinations, manhattan_distance)
        hungarian_algorithm(cost_matrix)

        for i in range(CUBE_COUNT):
            used_positions.add(origins[i])

            start_x = origins[i][0] * CELL_SIZE
            start_y = origins[i][1] * CELL_SIZE

            # Create the cube
            my_cube = Cube(start_x, start_y, CELL_SIZE, destinations[i], i, self.get_occupied_positions)

            # Register the cube's initial position
            pos = (my_cube.grid_x, my_cube.grid_y)
            self.occupied_positions[pos] = my_cube
            cubes.append(my_cube)

        return cubes
    
    def get_occupied_positions(self) -> Set[Tuple[int, int]]:
        """
        Get set of all currently occupied grid positions.
        
        Returns:
            Set of (x, y) tuples representing occupied grid positions
        """
        return set(self.occupied_positions.keys())
    
    def update_occupied_positions(self, cube: Cube, old_pos: Tuple[int, int], new_pos: Tuple[int, int]) -> None:
        """
        Update the occupied positions when a cube moves.
        
        Args:
            cube: The cube that moved
            old_pos: Previous (x, y) position
            new_pos: New (x, y) position
        """
        if old_pos in self.occupied_positions:
            del self.occupied_positions[old_pos]
        self.occupied_positions[new_pos] = cube
    
    def draw_grid(self) -> None:
        """
        Draw the background grid and highlight cube destinations.
        
        This method:
        1. Fills the screen with the background color
        2. Draws grid lines
        3. Highlights destination cells for all cubes
        """
        # Solid dark background
        self.screen.fill(BACKGROUND)
        
        # Grid lines
        for i in range(GRID_COLS + 1):
            pygame.draw.line(self.screen, GRID_LINES,
                            (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))
        for i in range(GRID_ROWS + 1):
            pygame.draw.line(self.screen, GRID_LINES,
                           (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
            
        if self.cubes:
            for cube in self.cubes:  # Highlight all cubes' destinations
                destination_x, destination_y = cube.destination  
                destination_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                destination_surface.fill((0, 255, 0, 100))  
                pygame.draw.rect(destination_surface, (0, 200, 0, 180), (0, 0, CELL_SIZE, CELL_SIZE), border_radius=10)
                self.screen.blit(destination_surface, (destination_x * CELL_SIZE, destination_y * CELL_SIZE))
                pygame.draw.rect(self.screen, (0, 255, 0), 
                                pygame.Rect(destination_x * CELL_SIZE, destination_y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 
                                width=3, border_radius=10)
 
    def update_grid(self, cubes: List[Cube]) -> None:
        """
        Update the grid and all cubes, then refresh the display.
        
        Args:
            cubes: List of cube objects to be drawn
        """
        self.draw_grid()
        for cube in cubes:
            cube.draw(self.screen)
        pygame.display.flip()
    
    def run(self) -> None:
        """
        Run the main game loop.
        
        This method handles:
        1. Processing pygame events (mouse, quit, etc.)
        2. Moving cubes automatically at regular intervals
        3. Updating the display
        4. Maintaining the frame rate
        
        The game loop continues until the user quits.
        """
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            #This part of the code is to drag cubes ourselves and drop them on the screen, for now we dont need this so i commented it out.
                # elif event.type == pygame.MOUSEBUTTONDOWN:
                #     mouse_pos = pygame.mouse.get_pos()
                #     for cube in self.cubes:
                #         if cube.rect.collidepoint(mouse_pos):
                #             self.selected_cube = cube
                # elif event.type == pygame.MOUSEBUTTONUP:
                #     self.selected_cube = None
                # elif event.type == pygame.MOUSEMOTION:
                #     mouse_pos = pygame.mouse.get_pos()
                #     for cube in self.cubes:
                #         cube.hover = cube.rect.collidepoint(mouse_pos)
                #     if self.selected_cube:
                #         grid_x = (mouse_pos[0] - CELL_SIZE//2) // CELL_SIZE
                #         grid_y = (mouse_pos[1] - CELL_SIZE//2) // CELL_SIZE
                #         if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                #             # Make sure the position isn't occupied by another cube
                #             pos = (grid_x, grid_y)
                #             current_pos = (self.selected_cube.grid_x, self.selected_cube.grid_y)
                #             if pos != current_pos and pos in self.occupied_positions:
                #                 continue  # Skip if position is occupied
                                
                #             # Update occupied positions
                #             self.update_occupied_positions(
                #                 self.selected_cube, 
                #                 (self.selected_cube.grid_x, self.selected_cube.grid_y),
                #                 (grid_x, grid_y)
                #             )
                            
                #             self.selected_cube.grid_x = grid_x
                #             self.selected_cube.grid_y = grid_y
                #             self.selected_cube.rect.x = (grid_x * CELL_SIZE) + 5
                #             self.selected_cube.rect.y = (grid_y * CELL_SIZE) + 5
                            
                #             # Recalculate path after drag and drop
                #             self.selected_cube.path = self.selected_cube.calculate_path()
            
            # Automatic movement - use a priority system to resolve conflicts
            if current_time - self.last_move_time >= MOVE_INTERVAL:
                # Sort cubes by distance to destination (prioritize cubes closer to their goals)
                cubes_to_move = [c for c in self.cubes if not c.is_reached() and c != self.selected_cube]
                cubes_to_move.sort(key=lambda c: c.distance_to_destination())
                
                # Process cubes in priority order
                for cube in cubes_to_move:
                    old_pos = (cube.grid_x, cube.grid_y)
                    cube.move(self.occupied_positions)
                    new_pos = (cube.grid_x, cube.grid_y)
                    
                    # Update occupied positions after movement
                    if old_pos != new_pos:
                        self.update_occupied_positions(cube, old_pos, new_pos)
                
                self.last_move_time = current_time
            
            self.draw_grid()
            
            # Add destination labels
            font = pygame.font.SysFont('Arial', 16)
            for cube in self.cubes:
                dest_x, dest_y = cube.destination
                label = font.render(f"{cube.cube_id + 1}", True, (255, 255, 255))
                label_rect = label.get_rect(center=(dest_x * CELL_SIZE + CELL_SIZE//2, 
                                                   dest_y * CELL_SIZE + CELL_SIZE//2))
                self.screen.blit(label, label_rect)
            
            # Draw cubes on top
            for cube in self.cubes:
                cube.draw(self.screen)
            
            # Display stats
            completed = sum(1 for cube in self.cubes if cube.is_reached() and 
                           (cube.grid_x, cube.grid_y) == cube.destination)
            total = len(self.cubes)
            stats_text = f"Completed: {completed}/{total}"
            stats_surf = font.render(stats_text, True, (255, 255, 255))
            self.screen.blit(stats_surf, (10, 10))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()