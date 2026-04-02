# config.py - AlgoFlow Configuration
# All colors, sizes, and constants in one place

# Window
WINDOW_WIDTH = 2400
WINDOW_HEIGHT = 1350
FPS = 60
TITLE = "AlgoFlow"
FONT_FAMILY = "Segoe UI, Roboto, Arial"

# Layout
HEADER_HEIGHT = 72
CONTROL_PANEL_HEIGHT = 96
INFO_PANEL_WIDTH = 450

# Visualization
BOX_MODE_THRESHOLD = 30
DEFAULT_ARRAY_SIZE = 20
SIZE_OPTIONS = ["10", "20", "30"]

# Speed control
BASE_SPEED = 15  # base operations per second at 1x (slider range: 0.1x–4.0x)

# Colors (RGB tuples)
class Colors:
    # Background
    BG = (20, 20, 30)
    PANEL_BG = (30, 30, 45)

    # Header / branding
    HEADER_BG = (25, 25, 38)
    BRAND_TEXT = (255, 255, 255)

    # Tab bar
    TAB_ACTIVE = (60, 130, 200)
    TAB_INACTIVE = (45, 45, 65)
    TAB_HOVER = (55, 55, 80)
    TAB_TEXT = (220, 220, 230)
    TAB_TEXT_ACTIVE = (255, 255, 255)

    # Sorting bars
    BAR_DEFAULT = (70, 130, 210)
    BAR_COMPARING = (230, 70, 70)
    BAR_SWAPPING = (255, 200, 50)
    BAR_SORTED = (50, 200, 100)
    BAR_PIVOT = (200, 100, 255)

    # Box visualization
    BOX_BG = (45, 45, 65)
    BOX_BORDER = (70, 70, 100)
    BOX_TEXT = (220, 220, 230)

    # Info panel cards
    CARD_BG = (38, 38, 55)
    CARD_BORDER = (55, 55, 75)

    # Pathfinding grid
    GRID_EMPTY = (40, 40, 55)
    GRID_WALL = (60, 60, 80)
    GRID_START = (50, 200, 100)
    GRID_END = (230, 70, 70)
    GRID_VISITED = (120, 80, 160)
    GRID_FRONTIER = (100, 180, 230)
    GRID_PATH = (255, 200, 50)
    GRID_LINE = (30, 30, 42)

    # Tree nodes
    NODE_DEFAULT = (70, 130, 210)
    NODE_HIGHLIGHT = (255, 200, 50)
    NODE_FOUND = (50, 200, 100)
    NODE_NOT_FOUND = (230, 70, 70)
    NODE_COMPARING = (230, 70, 70)
    NODE_SUCCESSOR = (255, 165, 0)
    NODE_VISITED = (120, 80, 160)
    EDGE_COLOR = (100, 100, 130)

    # UI elements
    BUTTON_BG = (55, 55, 80)
    BUTTON_HOVER = (70, 70, 100)
    BUTTON_ACTIVE = (60, 130, 200)
    BUTTON_TEXT = (220, 220, 230)
    TEXT_PRIMARY = (220, 220, 230)
    TEXT_SECONDARY = (140, 140, 160)
    TEXT_ACCENT = (100, 180, 230)
    HINT_TEXT = (100, 100, 120)

    # Slider
    SLIDER_TRACK = (55, 55, 80)
    SLIDER_FILL = (60, 130, 200)
    SLIDER_KNOB = (220, 220, 230)

    # Pointer labels (study mode)
    POINTER_COLORS = {
        "i": (100, 180, 230), "j": (100, 180, 230), "j+1": (100, 180, 230),
        "min": (230, 70, 70), "key": (255, 200, 50), "pivot": (200, 100, 255),
        "low": (50, 200, 100), "high": (230, 70, 70),
        "k": (50, 200, 100), "L": (100, 200, 230), "R": (230, 100, 100),
    }
    POINTER_DEFAULT_COLOR = (140, 140, 160)
    POINTER_TEXT_COLOR = (255, 255, 255)
    SORTED_BOUNDARY_COLOR = (80, 200, 120)

# Fonts (initialized after pygame.init())
FONT_SIZES = {
    "tiny": 20,
    "small": 23,
    "medium": 30,
    "large": 36,
    "title": 42,
    "brand": 33,
}

# --- Pathfinding ---
GRID_SIZES = {
    "Small": (15, 11),
    "Medium": (25, 18),
    "Large": (40, 25),
}
DEFAULT_GRID_SIZE = "Medium"
GRID_SIZE_OPTIONS = ["Small", "Medium", "Large"]
CELL_GAP = 1

# --- Tree visualization ---
TREE_NODE_RADIUS = 24
TREE_LEVEL_GAP = 80
TREE_MIN_H_SPACING = 50
TREE_EDGE_WIDTH = 2
HEAP_STRIP_HEIGHT = 60
DEFAULT_BST_VALUES = [40, 20, 60, 10, 30, 50, 70, 5, 15, 25, 35, 45, 55, 65, 75]
DEFAULT_HEAP_VALUES = [5, 10, 15, 20, 25, 30, 35]

# Tabs
TABS = ["Sorting", "Pathfinding", "Trees"]
