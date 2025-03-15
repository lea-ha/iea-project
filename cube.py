import pygame
from typing import List, Tuple, Dict
from config import CUBE_COLORS, CELL_SIZE, SHADOW_COLOR, CUBE_HOVER_COLOR
from request import Coordinate


# Modified version of the Cube class
class Cube:
    def __init__(self, cube_id: int, path: List[Coordinate], occupied_positions: Dict[Tuple[int, int], 'Cube']) -> None:
        self.cube_id = cube_id
        self.path = path
        self.current_step = 0
        
        # Set initial position
        self.grid_x = path[0].x
        self.grid_y = path[0].y
        
        # Destination
        self.destination = (path[-1].x, path[-1].y)
        
        # Create rect for rendering
        self.rect = pygame.Rect(self.grid_x * CELL_SIZE + 5, self.grid_y * CELL_SIZE + 5, 
                            CELL_SIZE - 10, CELL_SIZE - 10)
        
        # Use a color based on cube_id
        self.color = CUBE_COLORS[cube_id % len(CUBE_COLORS)]
        self.hover = False
        self.waiting = False  # We keep this but don't use it for movement logic
        self.overlapping = False  # Add this to track cell overlaps
        
    def move(self) -> None:
        """
        Move the cube to the next position in its path.
        The API has already ensured paths are collision-free.
        """
        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            next_coord = self.path[self.current_step]
            self.grid_x = next_coord.x
            self.grid_y = next_coord.y
            self.rect.x = self.grid_x * CELL_SIZE + 5
            self.rect.y = self.grid_y * CELL_SIZE + 5

    def is_reached(self) -> bool:
        """Check if the cube has reached its destination."""
        return (self.grid_x, self.grid_y) == self.destination

    def distance_to_destination(self) -> int:
        """Compute Manhattan distance to destination."""
        return abs(self.grid_x - self.destination[0]) + abs(self.grid_y - self.destination[1])

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the cube on the given pygame surface, including visual effects.
        """
        # Shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x + 4, self.rect.y + 4))

        # Determine base color
        if self.overlapping:
            # Red color for overlapping cubes
            base_color = (255, 0, 0)  # Bright red to indicate collision
        elif self.is_reached():
            base_color = tuple(min(c + 50, 255) for c in self.color)  # Brighter color if reached
        elif self.hover:
            base_color = CUBE_HOVER_COLOR
        else:
            base_color = self.color

        # Draw cube
        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)

        # Draw cube ID for identification
        font = pygame.font.SysFont('Arial', 18)
        id_text = font.render(str(self.cube_id + 1), True, (255, 255, 255))
        text_rect = id_text.get_rect(center=self.rect.center)
        screen.blit(id_text, text_rect)