# config.py - AlgoFlow Configuration
# All colors, sizes, and constants in one place

# Window
WINDOW_WIDTH = 1875
WINDOW_HEIGHT = 975
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
SIZE_OPTIONS = ["10", "20", "30", "50", "100"]

# Speed control (discrete multipliers replace continuous slider)
SPEED_OPTIONS = ["0.25x", "0.5x", "1x", "1.5x", "2x"]
SPEED_MULTIPLIERS = {"0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "1.5x": 1.5, "2x": 2.0}
BASE_SPEED = 30  # base operations per second at 1x

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
    GRID_VISITED = (70, 100, 160)
    GRID_FRONTIER = (100, 180, 230)
    GRID_PATH = (255, 200, 50)
    GRID_LINE = (30, 30, 42)

    # Tree nodes
    NODE_DEFAULT = (70, 130, 210)
    NODE_HIGHLIGHT = (255, 200, 50)
    NODE_FOUND = (50, 200, 100)
    NODE_NOT_FOUND = (230, 70, 70)
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

# Fonts (initialized after pygame.init())
FONT_SIZES = {
    "tiny": 20,
    "small": 23,
    "medium": 30,
    "large": 36,
    "title": 42,
    "brand": 33,
}

# Tabs
TABS = ["Sorting", "Pathfinding", "Trees"]
