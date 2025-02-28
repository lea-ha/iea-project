import pygame
import random
from astar import find_path
from config import CUBE_COLORS, CELL_SIZE, GRID_COLS, GRID_ROWS, SHADOW_COLOR, CUBE_HOVER_COLOR
from typing import List, Tuple, Callable, Optional, Iterator, Dict, Set

from hungarian_algorithm import manhattan_distance


class Cube:
    """
    A movable cube object that navigates on a grid using A* pathfinding.
    
    Attributes:
        rect (pygame.Rect): Rectangle representing the cube's position and size
        color (tuple): RGB color of the cube
        hover (bool): Whether the cube is being hovered over
        grid_x (int): Current X position on the grid
        grid_y (int): Current Y position on the grid
        destination (tuple): Target (x, y) coordinates on grid
        path (list): List of movement steps to reach the destination
        cube_id (int): Unique identifier for the cube
        get_occupied_positions_fn (Callable): Function to get occupied positions
    """
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        size: int, 
        destination: Tuple[int, int], 
        cube_id: int, 
        get_occupied_positions_fn: Callable[[], Set[Tuple[int, int]]]
    ) -> None:
        """
        Initialize a cube object with position and destination.
        
        Args:
            x: Initial X coordinate in pixels
            y: Initial Y coordinate in pixels  
            size: Size of the cube in pixels
            destination: Target (grid_x, grid_y) coordinates on grid
            cube_id: Unique identifier for the cube
            get_occupied_positions_fn: Function that returns occupied grid positions
        """
        self.rect = pygame.Rect(x + 5, y + 5, size - 10, size - 10)
        self.cube_id = cube_id
        # Use different colors for different cubes
        self.color = CUBE_COLORS[cube_id % len(CUBE_COLORS)]
        self.hover = False
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE
        self.destination = destination
        self.get_occupied_positions_fn = get_occupied_positions_fn
        self.path = self.calculate_path()
        self.waiting = False
        self.wait_counter = 0
        self.max_wait = 1
        
        print(f"\nCube {cube_id} - Initial Position: ({self.grid_x}, {self.grid_y})")
        print(f"Cube {cube_id} - Destination: {self.destination}")
        if self.path:
            print(f"Cube {cube_id} - Full path movements: {self.path}\n")
        else:
            print(f"Cube {cube_id} - No path found initially\n")
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions on the grid.
        
        Args:
            pos: Current (x, y) grid position
        
        Returns:
            List of valid neighboring (x, y) positions as tuples
        """
        x, y = pos
        neighbors = []
        
        # Get currently occupied positions excluding the current position
        occupied = self.get_occupied_positions_fn()
        current_pos = (self.grid_x, self.grid_y)
        if current_pos in occupied:
            occupied.remove(current_pos)
        
        # Don't consider the destination of other cubes as occupied if pathfinding
        # This allows cubes to plan paths through positions that will eventually be clear
        if pos != current_pos:
            if self.destination in occupied:
                occupied.remove(self.destination)
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            new_x, new_y = x + dx, y + dy
            new_pos = (new_x, new_y)
            
            # Check if position is within grid bounds and not occupied
            if (0 <= new_x < GRID_COLS and 
                0 <= new_y < GRID_ROWS and 
                new_pos not in occupied):
                neighbors.append(new_pos)
                
        return neighbors
    
    def distance_to_destination(self) -> int:
        """
        Calculate Manhattan distance to destination.
        
        Returns:
            Integer representing the Manhattan distance to destination
        """
        return abs(self.grid_x - self.destination[0]) + abs(self.grid_y - self.destination[1])
    
    def calculate_path(self) -> List[Tuple[int, int]]:
        """
        Calculate path using A* algorithm from the astar package.
        
        Returns:
            List of movement instructions as tuples (dx, dy)
        """
        start = (self.grid_x, self.grid_y)
        goal = self.destination
        
        # If already at destination, return empty path
        if start == goal:
            return []
        
        # If destination is occupied by another cube, we'll try to find a path anyway
        # The cube will stop before reaching the destination and wait
        
        # Find path using astar package
        path_nodes = find_path(
            start=start,
            goal=goal,
            neighbors_fnct=self.get_neighbors,
            heuristic_cost_estimate_fnct=lambda a, b: abs(b[0] - a[0]) + abs(b[1] - a[1])
        )
        
        if not path_nodes:
            print(f"Cube {self.cube_id} - No path found!")
            return []
        
        # Convert path nodes to movement instructions
        movements = []
        path_nodes = list(path_nodes)
        
        for i in range(len(path_nodes) - 1):
            current = path_nodes[i]
            next_pos = path_nodes[i + 1]
            dx = next_pos[0] - current[0]
            dy = next_pos[1] - current[1]
            movements.append((dx, dy))
            
        return movements
    
    def is_reached(self) -> bool:
        """
        Check if the cube has reached its destination.
        
        Returns:
            True if the path is empty (destination reached), False otherwise
        """
        # If we're at the destination, we've reached it
        if (self.grid_x, self.grid_y) == self.destination:
            return True
        
        # If we have a path, we're still moving
        if self.path:
            return False
        
        # If waiting (for obstacle to clear), not reached
        if self.waiting:
            return False
        
        # If no path and not at destination, try to recalculate
        self.path = self.calculate_path()
        return False
    
    def move(self, occupied_positions: Dict[Tuple[int, int], 'Cube']) -> None:
        """
        Move the cube one step along its path.
        
        Args:
            occupied_positions: Dictionary of positions that are currently occupied
            
        If path exists, pops the next movement instruction and updates position.
        If destination is reached, prints confirmation message.
        """
        # If we're at destination, nothing to do
        if (self.grid_x, self.grid_y) == self.destination:
            return
            
        # Handle waiting state
        if self.waiting:
            self.wait_counter += 1
            if self.wait_counter >= self.max_wait:
                self.waiting = False
                self.wait_counter = 0
                self.path = self.calculate_path()  # Try to calculate a new path
            return
            
        # If no path, try to calculate one
        if not self.path:
            self.path = self.calculate_path()
            if not self.path:
                # If still no path, go into waiting state
                self.waiting = True
                self.wait_counter = 0
                distance_from_goal = manhattan_distance((self.grid_x, self.grid_y), self.destination)
                if distance_from_goal < 3:
                    self.max_wait = 1
                elif distance_from_goal < 5:
                    self.max_wait = 2
                else:
                    self.max_wait = 3
                return
                
        # Check if the next move is valid
        dx, dy = self.path[0]
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        new_pos = (new_x, new_y)
        
        # Check if the next position is occupied by another cube
        if new_pos in occupied_positions and occupied_positions[new_pos] != self:
            other_cube = occupied_positions[new_pos]
            
            # If the cube in our way is at its destination, we need to find a different route
            if new_pos == other_cube.destination:
                print(f"Cube {self.cube_id} - Position {new_pos} is a destination for cube {other_cube.cube_id}, recalculating path...")
                self.path = self.calculate_path()
                return
            
            # Otherwise, wait and see if it moves
            print(f"Cube {self.cube_id} - Position {new_pos} is occupied by cube {other_cube.cube_id}, waiting...")
            self.waiting = True
            self.wait_counter = 0
            return
        
        # If clear to move, update position
        self.path.pop(0)  # Remove the first move after using it
        
        if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
            self.grid_x = new_x
            self.grid_y = new_y
            self.rect.x = (self.grid_x * CELL_SIZE) + 5
            self.rect.y = (self.grid_y * CELL_SIZE) + 5
            
        if (self.grid_x, self.grid_y) == self.destination:
            print(f"Cube {self.cube_id} - Destination reached!")
    
    def draw(self, screen: pygame.Surface) -> None:
        """
        Render the cube on the screen with visual effects.
        
        Args:
            screen: Pygame surface to draw on
            
        Visual effects include:
        - Shadow effect with offset
        - Gradient lighting effect
        - Hover state color change
        - Rounded corners
        - Waiting state indicator
        """
        # Shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x + 4, self.rect.y + 4))
        
        # Determine cube color based on state
        if (self.grid_x, self.grid_y) == self.destination:
            # Use a brighter version of the color for reached destination
            base_color = tuple(min(c + 50, 255) for c in self.color)
        elif self.waiting:
            # Use a pulsing yellow for waiting state
            pulse = (pygame.time.get_ticks() % 1000) / 1000  # 0 to 1 over 1 second
            pulse_value = int(150 + 105 * pulse)  # Pulse between 150 and 255
            base_color = (pulse_value, pulse_value, 0)  # Pulsing yellow
        elif self.hover:
            base_color = CUBE_HOVER_COLOR
        else:
            base_color = self.color
        
        # Cube with gradient
        gradient_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = 255 - (i * 100 // self.rect.height)
            highlight_color = (
                min(255, base_color[0] + 50),
                min(255, base_color[1] + 50),
                min(255, base_color[2] + 50),
                alpha
            )
            pygame.draw.line(gradient_rect, highlight_color,
                            (0, i), (self.rect.width, i))
        
        base_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(base_rect, base_color, base_rect.get_rect(), border_radius=10)
        base_rect.blit(gradient_rect, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(base_rect, self.rect)
        
        # Add cube ID text for identification
        font = pygame.font.SysFont('Arial', 18)
        id_text = font.render(str(self.cube_id + 1), True, (255, 255, 255))
        text_rect = id_text.get_rect(center=self.rect.center)
        screen.blit(id_text, text_rect)