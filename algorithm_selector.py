from typing import Tuple
import pygame

class AlgorithmSelector:
    """Class to handle algorithm selection for pathfinding."""
    
    def __init__(self) -> None:
        """Initialize the algorithm selector."""
        self.algorithms = ["astar", "bfs"]
        self.selected_algorithm = "astar"  # Default algorithm
        
        # Add morphing toggle
        self.morphing_enabled = True  # Default to enabled
        
        # Add priority strategy selection
        self.priority_strategies = ["y-axis", "manhattan"]
        self.selected_priority = "y-axis"  # Default priority strategy
        
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
        
        # Draw priority strategy section
        priority_y_pos = 70 + len(self.algorithms) * spacing + 20
        priority_title = font.render("Priority Strategy", True, (255, 255, 255))
        screen.blit(priority_title, (screen_width - panel_width + 15, priority_y_pos))
        
        # Draw priority strategy options
        for i, strategy in enumerate(self.priority_strategies):
            y_pos = priority_y_pos + 30 + i * spacing
            
            # Draw checkbox
            checkbox_rect = pygame.Rect(screen_width - panel_width + 20, y_pos, checkbox_size, checkbox_size)
            pygame.draw.rect(screen, (200, 200, 200), checkbox_rect, 2)
            
            # Fill checkbox if selected
            if strategy == self.selected_priority:
                inner_rect = pygame.Rect(checkbox_rect.x + 4, checkbox_rect.y + 4,
                                      checkbox_size - 8, checkbox_size - 8)
                pygame.draw.rect(screen, (100, 200, 100), inner_rect)
            
            # Draw label
            label = font.render(strategy.capitalize(), True, (255, 255, 255))
            screen.blit(label, (checkbox_rect.right + 10, checkbox_rect.y))
        
        # Draw morphing toggle
        morph_y_pos = priority_y_pos + 30 + len(self.priority_strategies) * spacing + 20
        morph_title = font.render("Morphing", True, (255, 255, 255))
        screen.blit(morph_title, (screen_width - panel_width + 15, morph_y_pos))
        
        toggle_width = 50
        toggle_height = 24
        toggle_x = screen_width - panel_width + 20
        toggle_y = morph_y_pos + 30
        
        # Draw toggle background
        toggle_color = (100, 200, 100) if self.morphing_enabled else (200, 100, 100)
        toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
        pygame.draw.rect(screen, toggle_color, toggle_rect, border_radius=toggle_height//2)
        
        # Draw toggle switch
        switch_pos = toggle_x + toggle_width - toggle_height + 4 if self.morphing_enabled else toggle_x + 4
        switch_rect = pygame.Rect(switch_pos, toggle_y + 4, toggle_height - 8, toggle_height - 8)
        pygame.draw.rect(screen, (255, 255, 255), switch_rect, border_radius=(toggle_height - 8)//2)
        
        # Draw toggle labels
        toggle_label = "ON" if self.morphing_enabled else "OFF"
        small_font = pygame.font.SysFont('Arial', 16)
        label = small_font.render(toggle_label, True, (255, 255, 255))
        label_x = toggle_x + toggle_width + 10
        screen.blit(label, (label_x, toggle_y + 4))
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        Process mouse clicks for algorithm selection.
        Returns True if any algorithm was selected or if morphing toggle was changed.
        """
        screen_width = pygame.display.get_surface().get_size()[0]
        panel_width = 200
        checkbox_size = 20
        spacing = 40
        
        # Check if click is within algorithm selection area
        if pos[0] > screen_width - panel_width:
            # Check algorithm selection
            for i, algo in enumerate(self.algorithms):
                y_pos = 70 + i * spacing
                checkbox_rect = pygame.Rect(screen_width - panel_width + 20, y_pos, checkbox_size, checkbox_size)
                
                if checkbox_rect.collidepoint(pos):
                    self.selected_algorithm = algo
                    return True
            
            # Check priority strategy selection
            priority_y_pos = 70 + len(self.algorithms) * spacing + 20
            for i, strategy in enumerate(self.priority_strategies):
                y_pos = priority_y_pos + 30 + i * spacing
                checkbox_rect = pygame.Rect(screen_width - panel_width + 20, y_pos, checkbox_size, checkbox_size)
                
                if checkbox_rect.collidepoint(pos):
                    self.selected_priority = strategy
                    return True
            
            # Check morphing toggle
            morph_y_pos = priority_y_pos + 30 + len(self.priority_strategies) * spacing + 20
            toggle_width = 50
            toggle_height = 24
            toggle_x = screen_width - panel_width + 20
            toggle_y = morph_y_pos + 30
            toggle_rect = pygame.Rect(toggle_x, toggle_y, toggle_width, toggle_height)
            
            if toggle_rect.collidepoint(pos):
                self.morphing_enabled = not self.morphing_enabled
                return True
            
        return False
        
    def get_selected_algorithm(self) -> str:
        """Return the currently selected algorithm."""
        return self.selected_algorithm
    
    def is_morphing_enabled(self) -> bool:
        """Return whether morphing is enabled."""
        return self.morphing_enabled
        
    def get_selected_priority(self) -> str:
        """Return the currently selected priority strategy."""
        return self.selected_priority