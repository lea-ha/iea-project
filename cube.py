import pygame
from typing import List, Tuple, Dict
from config import CUBE_COLORS, CELL_SIZE, SHADOW_COLOR, CUBE_HOVER_COLOR
from request import Coordinate


class Cube:
    """
    A movable cube object that navigates on a grid along a precomputed path.
    The cube is initialized with a full path (list of Coordinates) where the first element is its start
    and the last element is its destination.
    """

    def __init__(self, cube_id: int, path: List[Coordinate], occupied_positions: Dict[Tuple[int, int], 'Cube']) -> None:
        """
        Initialize a Cube with its ID, precomputed path, and the occupied_positions dictionary.

        Args:
            cube_id: Unique identifier for the cube.
            path: List of Coordinates representing the path from start to destination.
            occupied_positions: Dictionary mapping (grid_x, grid_y) to the Cube that occupies that cell.
        """
        self.cube_id = cube_id
        self.path = path  # Full list of Coordinate objects
        self.current_step = 0  # Index in the path; starting at 0

        # Set initial grid position based on the first coordinate in the path.
        self.grid_x = path[0].x
        self.grid_y = path[0].y

        # Destination is the last coordinate in the path.
        self.destination = (path[-1].x, path[-1].y)

        # Create a pygame.Rect for rendering.
        self.rect = pygame.Rect(self.grid_x * CELL_SIZE + 5, self.grid_y * CELL_SIZE + 5, CELL_SIZE - 10,
                                CELL_SIZE - 10)

        # Use a color based on cube_id.
        self.color = CUBE_COLORS[cube_id % len(CUBE_COLORS)]
        self.hover = False

        # Waiting state if the cube cannot move.
        self.waiting = False

    def move(self, occupied_positions: Dict[Tuple[int, int], 'Cube']) -> None:
        """
        Move the cube along its precomputed path.
        If the next coordinate is occupied by another cube, the cube waits.
        Otherwise, it advances to the next coordinate and updates its position.
        """
        if self.current_step >= len(self.path) - 1:
            return  # Already at destination

        next_coord = self.path[self.current_step + 1]
        new_pos = (next_coord.x, next_coord.y)

        if new_pos in occupied_positions and occupied_positions[new_pos] != self:
            self.waiting = True  # Wait if next position is occupied
            return

        # Move is allowed: update current step and grid position.
        old_pos = (self.grid_x, self.grid_y)
        self.current_step += 1
        self.grid_x = next_coord.x
        self.grid_y = next_coord.y
        self.rect.x = self.grid_x * CELL_SIZE + 5
        self.rect.y = self.grid_y * CELL_SIZE + 5
        self.waiting = False

    def is_reached(self) -> bool:
        """
        Check if the cube has reached its destination.
        """
        return (self.grid_x, self.grid_y) == self.destination

    def distance_to_destination(self) -> int:
        """
        Compute the Manhattan distance from the current position to the destination.
        """
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
        if self.is_reached():
            base_color = tuple(min(c + 50, 255) for c in self.color)  # Brighter color if reached
        elif self.waiting:
            pulse = (pygame.time.get_ticks() % 1000) / 1000
            pulse_value = int(150 + 105 * pulse)
            base_color = (pulse_value, pulse_value, 0)  # Pulsing yellow for waiting
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