import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 32  # 32x32 pixel grid
CELL_SIZE = 15  # Each pixel cell is 15x15 pixels on screen
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 300  # Extra space for color palette
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 100  # Extra space for controls
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Color palette
COLORS = [
    (0, 0, 0),        # Black
    (255, 255, 255),  # White
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (255, 165, 0),    # Orange
    (128, 0, 128),    # Purple
    (165, 42, 42),    # Brown
    (255, 192, 203),  # Pink
    (128, 128, 128),  # Gray
    (0, 128, 0),      # Dark Green
    (128, 0, 0),      # Dark Red
    (0, 0, 128),      # Dark Blue
]

class PixelPainter:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pixel Painter")
        self.clock = pygame.time.Clock()
        
        # Initialize grid (filled with white)
        self.grid = [[WHITE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Current selected color
        self.current_color = BLACK
        
        # Drawing mode
        self.drawing = False
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.drawing = True
                    self.paint_pixel(event.pos)
                    self.select_color(event.pos)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    self.paint_pixel(event.pos)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # Clear canvas
                    self.clear_canvas()
                elif event.key == pygame.K_s:  # Save
                    self.save_image()
                elif event.key == pygame.K_l:  # Load
                    self.load_image()
                    
        return True
    
    def paint_pixel(self, mouse_pos):
        x, y = mouse_pos
        
        # Check if click is within the grid area
        if 0 <= x < GRID_SIZE * CELL_SIZE and 0 <= y < GRID_SIZE * CELL_SIZE:
            grid_x = x // CELL_SIZE
            grid_y = y // CELL_SIZE
            
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                self.grid[grid_y][grid_x] = self.current_color
    
    def select_color(self, mouse_pos):
        x, y = mouse_pos
        
        # Color palette area
        palette_x = GRID_SIZE * CELL_SIZE + 20
        palette_y = 20
        color_size = 30
        
        for i, color in enumerate(COLORS):
            row = i // 4
            col = i % 4
            color_x = palette_x + col * (color_size + 5)
            color_y = palette_y + row * (color_size + 5)
            
            if (color_x <= x <= color_x + color_size and 
                color_y <= y <= color_y + color_size):
                self.current_color = color
                break
    
    def clear_canvas(self):
        self.grid = [[WHITE for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def save_image(self):
        try:
            # Save as a simple format
            data = {
                'grid': [[[r, g, b] for r, g, b in row] for row in self.grid],
                'size': GRID_SIZE
            }
            with open('pixel_art.json', 'w') as f:
                json.dump(data, f)
            print("Image saved as 'pixel_art.json'")
        except Exception as e:
            print(f"Error saving: {e}")
    
    def load_image(self):
        try:
            with open('pixel_art.json', 'r') as f:
                data = json.load(f)
            self.grid = [[tuple(pixel) for pixel in row] for row in data['grid']]
            print("Image loaded from 'pixel_art.json'")
        except Exception as e:
            print(f"Error loading: {e}")
    
    def draw(self):
        self.screen.fill(LIGHT_GRAY)
        
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, self.grid[y][x], rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
        
        # Draw color palette
        palette_x = GRID_SIZE * CELL_SIZE + 20
        palette_y = 20
        color_size = 30
        
        for i, color in enumerate(COLORS):
            row = i // 4
            col = i % 4
            x = palette_x + col * (color_size + 5)
            y = palette_y + row * (color_size + 5)
            
            rect = pygame.Rect(x, y, color_size, color_size)
            pygame.draw.rect(self.screen, color, rect)
            
            # Highlight selected color
            if color == self.current_color:
                pygame.draw.rect(self.screen, BLACK, rect, 3)
            else:
                pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "Click to paint pixels",
            "Click colors to select",
            "Press 'C' to clear",
            "Press 'S' to save",
            "Press 'L' to load"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, BLACK)
            self.screen.blit(text, (palette_x, palette_y + 200 + i * 25))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    painter = PixelPainter()
    painter.run()