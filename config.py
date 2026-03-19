# config.py - Algorithm Visualizer Configuration
# All colors, sizes, and constants in one place

# Window
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "Algorithm & Data Structure Visualizer"

# Layout
TAB_BAR_HEIGHT = 50
CONTROL_PANEL_HEIGHT = 60
CANVAS_TOP = TAB_BAR_HEIGHT + 10
CANVAS_BOTTOM = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT - 10

# Colors (RGB tuples)
class Colors:
    # Background
    BG = (20, 20, 30)
    PANEL_BG = (30, 30, 45)
    
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
    
    # Slider
    SLIDER_TRACK = (55, 55, 80)
    SLIDER_FILL = (60, 130, 200)
    SLIDER_KNOB = (220, 220, 230)

# Fonts (initialized after pygame.init())
FONT_SIZES = {
    "small": 14,
    "medium": 18,
    "large": 24,
    "title": 32,
}

# Tabs
TABS = ["Sorting", "Pathfinding", "Trees"]
