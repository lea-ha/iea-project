# Constants
GRID_COLS = 10
GRID_ROWS = 10
CELL_SIZE = 60
WIDTH, HEIGHT = GRID_COLS * CELL_SIZE, GRID_ROWS * CELL_SIZE
CUBE_COUNT = 20
MOVE_INTERVAL = 1000  # Time between moves in milliseconds (1 second)

# Dark theme colors
BACKGROUND = (18, 18, 18)
GRID_LINES = (45, 45, 45)
CUBE_COLORS = [
    (88, 101, 242),    # Discord Blue
    (114, 137, 218),   # Light Discord Blue
    (145, 170, 242),   # Lighter Blue
    (250, 166, 26),    # Orange
    (245, 119, 49),    # Bright Orange
    (237, 66, 69),     # Red
    (220, 20, 60),     # Crimson
    (124, 187, 0),     # Lime Green
    (46, 204, 113),    # Emerald Green
    (155, 89, 182),    # Purple
    (142, 68, 173),    # Dark Purple
    (52, 152, 219),    # Blue
    (0, 184, 148),     # Turquoise
    (255, 159, 243),   # Pink
    (255, 118, 117),   # Salmon
    (241, 196, 15),    # Yellow
    (26, 188, 156),    # Teal
    (181, 126, 220),   # Lavender
    (240, 147, 43),    # Amber
    (231, 76, 60)      # Pomegranate
]

CUBE_HOVER_COLOR = (255, 215, 0)
SHADOW_COLOR = (0, 0, 0, 50)