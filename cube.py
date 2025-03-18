import pygame
from typing import List, Tuple, Dict
from config import CUBE_COLORS, CELL_SIZE, SHADOW_COLOR, CUBE_HOVER_COLOR, REACHED_COLOR, OVERLAP_COLOR, MOVE_SPEED
from request import Coordinate


class Cube:
    def __init__(self, cube_id: int, path: List[Coordinate], occupied_positions: Dict[Tuple[int, int], 'Cube']) -> None:
        self.cube_id = cube_id
        self.path = path
        self.current_step = 0
        
        self.grid_x = path[0].x
        self.grid_y = path[0].y
        
        self.visual_x = self.grid_x * CELL_SIZE + 5
        self.visual_y = self.grid_y * CELL_SIZE + 5
        
        self.destination = (path[-1].x, path[-1].y)
        
        self.rect = pygame.Rect(self.visual_x, self.visual_y, 
                            CELL_SIZE - 10, CELL_SIZE - 10)
        
        # Movement animation
        self.is_moving = False
        self.move_progress = 0.0
        self.move_speed = MOVE_SPEED  
        self.next_grid_x = self.grid_x
        self.next_grid_y = self.grid_y
        
        self.direction = None  # 'up', 'down', 'left', or 'right'
        
        self.color = CUBE_COLORS[cube_id % len(CUBE_COLORS)]
        self.hover = False
        self.waiting = False
        self.overlapping = False
    
    def update(self) -> None:
        """
        Update the cube's visual position for smooth movement.
        Should be called every frame.
        """
        if self.is_moving:
            # Update progress
            self.move_progress += self.move_speed
            
            if self.move_progress >= 1.0:
                # Movement complete
                self.is_moving = False
                self.move_progress = 0.0
                self.grid_x = self.next_grid_x
                self.grid_y = self.next_grid_y
                self.visual_x = self.grid_x * CELL_SIZE + 5
                self.visual_y = self.grid_y * CELL_SIZE + 5
            else:
                start_x = self.grid_x * CELL_SIZE + 5
                start_y = self.grid_y * CELL_SIZE + 5
                end_x = self.next_grid_x * CELL_SIZE + 5
                end_y = self.next_grid_y * CELL_SIZE + 5
                
                self.visual_x = start_x + (end_x - start_x) * self.move_progress
                self.visual_y = start_y + (end_y - start_y) * self.move_progress
            
            self.rect.x = self.visual_x
            self.rect.y = self.visual_y
    
    def move(self) -> None:
        """
        Start moving the cube to the next position in its path.
        """
        if not self.is_moving and self.current_step < len(self.path) - 1:
            self.current_step += 1
            next_coord = self.path[self.current_step]
            
            self.next_grid_x = next_coord.x
            self.next_grid_y = next_coord.y
            
            if self.next_grid_x > self.grid_x:
                self.direction = 'right'
            elif self.next_grid_x < self.grid_x:
                self.direction = 'left'
            elif self.next_grid_y > self.grid_y:
                self.direction = 'down'
            elif self.next_grid_y < self.grid_y:
                self.direction = 'up'
            
            self.is_moving = True
            self.move_progress = 0.0

    def is_reached(self) -> bool:
        """Check if the cube has reached its destination."""
        return (self.grid_x, self.grid_y) == self.destination and not self.is_moving

    def distance_to_destination(self) -> int:
        """Compute Manhattan distance to destination."""
        return abs(self.grid_x - self.destination[0]) + abs(self.grid_y - self.destination[1])

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the cube on the given pygame surface, including direction indicators.
        """

        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW_COLOR, shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, (self.rect.x + 4, self.rect.y + 4))

        if self.overlapping:
            base_color = OVERLAP_COLOR
        elif self.is_reached():
            base_color = REACHED_COLOR
        elif self.hover:
            base_color = CUBE_HOVER_COLOR
        else:
            base_color = self.color

        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)

        # Draw cube ID for identification
        font = pygame.font.SysFont('Arial', 18)
        id_text = font.render(str(self.cube_id + 1), True, (255, 255, 255))
        text_rect = id_text.get_rect(center=self.rect.center)
        screen.blit(id_text, text_rect)