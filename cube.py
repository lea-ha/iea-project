import pygame
from astar import find_path
from config import CUBE_COLORS, CELL_SIZE, GRID_COLS, GRID_ROWS, SHADOW_COLOR, CUBE_HOVER_COLOR
from typing import List, Tuple, Callable, Optional, Iterator


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
    """
    
    def __init__(self, x: int, y: int, size: int, destination: Tuple[int, int]) -> None:
        """
        Initialize a cube object with position and destination.
        
        Args:
            x: Initial X coordinate in pixels
            y: Initial Y coordinate in pixels  
            size: Size of the cube in pixels
            destination: Target (grid_x, grid_y) coordinates on grid
        """
        self.rect = pygame.Rect(x + 5, y + 5, size - 10, size - 10)
        self.color = CUBE_COLORS[0]
        self.hover = False
        self.grid_x = x // CELL_SIZE
        self.grid_y = y // CELL_SIZE
        self.destination = destination
        print(f"\nInitial Position: ({self.grid_x}, {self.grid_y})")
        print(f"Destination: {self.destination}")
        self.path = self.calculate_path()
        print(f"Full path movements: {self.path}\n")
    
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
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Down, Right, Up, Left
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
                neighbors.append((new_x, new_y))
        return neighbors
    
    def calculate_path(self) -> List[Tuple[int, int]]:
        """
        Calculate path using A* algorithm from the astar package.
        
        Returns:
            List of movement instructions as tuples (dx, dy)
        """
        start = (self.grid_x, self.grid_y)
        goal = self.destination
        
        # Find path using astar package
        path_nodes = find_path(
            start=start,
            goal=goal,
            neighbors_fnct=self.get_neighbors,
            heuristic_cost_estimate_fnct=lambda a, b: abs(b[0] - a[0]) + abs(b[1] - a[1]),
            distance_between_fnct=lambda a, b: 1.0
        )
        
        if not path_nodes:
            print("No path found!")
            return []
        
        # Convert path nodes to movement instructions
        movements = []
        path_nodes = list(path_nodes)
        print(f"Path nodes: {path_nodes}")
        
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
        if self.path:
            return False
        return True
    
    def move(self) -> None:
        """
        Move the cube one step along its path.
        
        If path exists, pops the next movement instruction and updates position.
        If destination is reached, prints confirmation message.
        """
        if self.path:
            dx, dy = self.path.pop(0)
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            
            print(f"Moving from ({self.grid_x}, {self.grid_y}) to ({new_x}, {new_y})")
            print(f"Remaining moves: {self.path}")
            
            if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
                self.grid_x = new_x
                self.grid_y = new_y
                self.rect.x = (self.grid_x * CELL_SIZE) + 5
                self.rect.y = (self.grid_y * CELL_SIZE) + 5
        else:
            if self.grid_x == self.destination[0] and self.grid_y == self.destination[1]:
                print("Destination reached!")
    
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
        """
        # Shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x + 4, self.rect.y + 4))
        
        # Cube with gradient
        color = CUBE_HOVER_COLOR if self.hover else self.color
        gradient_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = 255 - (i * 100 // self.rect.height)
            highlight_color = (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50),
                alpha
            )
            pygame.draw.line(gradient_rect, highlight_color,
                            (0, i), (self.rect.width, i))
        
        base_rect = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(base_rect, color, base_rect.get_rect(), border_radius=10)
        base_rect.blit(gradient_rect, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(base_rect, self.rect)