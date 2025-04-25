from typing import Tuple
import pygame

class AlgorithmSelector:
    """Class to handle algorithm selection for pathfinding."""
    
    def __init__(self) -> None:
        """Initialize the algorithm selector."""
        self.algorithms = ["astar", "bfs"]
        self.selected_algorithm = "astar"  # Default algorithm
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the algorithm selection panel."""
        # Set up the right panel
        panel_width = 200
        screen_width, screen_height = screen.get_size()
        panel_area = (screen_width - panel_width, 0, panel_width, screen_height)
        
        pygame.draw.rect(screen, (40, 40, 50), panel_area)
        pygame.draw.line(screen, (80, 80, 90), 
                         (screen_width - panel_width, 0), 
                         (screen_width - panel_width, screen_height), 2)
        
        font = pygame.font.SysFont('Arial', 20)
        title = font.render("Routing Algorithm", True, (255, 255, 255))
        screen.blit(title, (screen_width - panel_width + 15, 20))
        
        # Draw algorithm options with checkboxes
        checkbox_size = 20
        spacing = 40
        
        for i, algo in enumerate(self.algorithms):
            y_pos = 70 + i * spacing
            
            # Draw checkbox
            checkbox_rect = pygame.Rect(screen_width - panel_width + 20, y_pos, checkbox_size, checkbox_size)
            pygame.draw.rect(screen, (200, 200, 200), checkbox_rect, 2)
            
            # Fill checkbox if selected
            if algo == self.selected_algorithm:
                inner_rect = pygame.Rect(checkbox_rect.x + 4, checkbox_rect.y + 4, 
                                         checkbox_size - 8, checkbox_size - 8)
                pygame.draw.rect(screen, (100, 200, 100), inner_rect)
            
            # Draw label
            label = font.render(algo.upper(), True, (255, 255, 255))
            screen.blit(label, (checkbox_rect.right + 10, checkbox_rect.y))
            
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        Process mouse clicks for algorithm selection.
        Returns True if any algorithm was selected.
        """
        screen_width = pygame.display.get_surface().get_size()[0]
        panel_width = 200
        checkbox_size = 20
        spacing = 40
        
        # Check if click is within algorithm selection area
        if pos[0] > screen_width - panel_width:
            for i, algo in enumerate(self.algorithms):
                y_pos = 70 + i * spacing
                checkbox_rect = pygame.Rect(screen_width - panel_width + 20, y_pos, checkbox_size, checkbox_size)
                
                if checkbox_rect.collidepoint(pos):
                    self.selected_algorithm = algo
                    return True
                    
        return False
        
    def get_selected_algorithm(self) -> str:
        """Return the currently selected algorithm."""
        return self.selected_algorithm
