# Constants
GRID_COLS = 10
GRID_ROWS = 10
CELL_SIZE = 60
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
CUBE_COUNT = 20
MOVE_INTERVAL = 50  # Time between moves in milliseconds 
MOVE_SPEED = 0.1  # Speed of cube movement animation

# Dark theme colors
BACKGROUND = (18, 18, 18)
GRID_LINES = (45, 45, 45)
OVERLAP_COLOR = (255, 0, 0)
REACHED_COLOR = (34, 139, 34)
CUBE_COLORS = [
    (0, 184, 148),     # Turquoise
    #We can add more colors if we want, and they will be chosen based on %
]

CUBE_HOVER_COLOR = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0, 50)