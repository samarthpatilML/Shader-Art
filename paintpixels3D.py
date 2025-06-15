import pygame
import sys
import json
import math
import os
from PIL import Image
import numpy as np
from copy import deepcopy

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 32
CELL_SIZE = 12
PANEL_WIDTH = 400
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + PANEL_WIDTH
WINDOW_HEIGHT = max(600, GRID_SIZE * CELL_SIZE + 100)
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Color palette
COLORS = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0),
    (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255),
    (255, 165, 0), (128, 0, 128), (165, 42, 42), (255, 192, 203),
    (128, 128, 128), (0, 128, 0), (128, 0, 0), (0, 0, 128),
    (255, 215, 0), (75, 0, 130), (255, 20, 147), (0, 250, 154),
    (255, 69, 0), (138, 43, 226), (60, 179, 113), (255, 105, 180)
]

class Layer:
    def __init__(self, width, height, name="Layer"):
        self.width = width
        self.height = height
        self.name = name
        self.pixels = [[None for _ in range(width)] for _ in range(height)]
        self.visible = True
        self.opacity = 255
    
    def copy(self):
        new_layer = Layer(self.width, self.height, self.name + "_copy")
        new_layer.pixels = deepcopy(self.pixels)
        new_layer.visible = self.visible
        new_layer.opacity = self.opacity
        return new_layer

class AnimationFrame:
    def __init__(self, layers, duration=100):
        self.layers = [layer.copy() for layer in layers]
        self.duration = duration  # in milliseconds

class AdvancedPixelPainter:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Advanced Pixel Art Editor")
        self.clock = pygame.time.Clock()
        
        # Layers system
        self.layers = [Layer(GRID_SIZE, GRID_SIZE, "Background")]
        self.current_layer_index = 0
        
        # Animation system
        self.animation_frames = [AnimationFrame(self.layers)]
        self.current_frame = 0
        self.playing_animation = False
        self.animation_timer = 0
        
        # Tools and settings
        self.current_color = BLACK
        self.brush_size = 1
        self.brush_shapes = ['square', 'circle', 'cross']
        self.current_brush_shape = 'square'
        self.tool_mode = 'paint'  # paint, fill, eyedropper, gradient
        
        # Interaction states
        self.drawing = False
        self.zoom_level = 1.0
        self.camera_x = 0
        self.camera_y = 0
        
        # Undo/Redo system
        self.history = []
        self.history_index = -1
        self.max_history = 50
        
        # Copy/Paste
        self.clipboard = None
        self.selection = None  # (x1, y1, x2, y2)
        self.selecting = False
        
        # Gradient settings
        self.gradient_start = None
        self.gradient_end = None
        self.gradient_colors = [BLACK, WHITE]
        
        # UI elements
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Save initial state
        self.save_state()
    
    def save_state(self):
        """Save current state for undo/redo"""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        state = {
            'layers': [layer.copy() for layer in self.layers],
            'current_layer': self.current_layer_index
        }
        self.history.append(state)
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
    
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.layers = [layer.copy() for layer in state['layers']]
            self.current_layer_index = state['current_layer']
    
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.layers = [layer.copy() for layer in state['layers']]
            self.current_layer_index = state['current_layer']
    
    def get_grid_pos(self, mouse_pos):
        """Convert screen coordinates to grid coordinates"""
        x, y = mouse_pos
        x = int((x - self.camera_x) / (CELL_SIZE * self.zoom_level))
        y = int((y - self.camera_y) / (CELL_SIZE * self.zoom_level))
        return x, y
    
    def get_screen_pos(self, grid_x, grid_y):
        """Convert grid coordinates to screen coordinates"""
        x = int(grid_x * CELL_SIZE * self.zoom_level + self.camera_x)
        y = int(grid_y * CELL_SIZE * self.zoom_level + self.camera_y)
        return x, y
    
    def paint_pixel(self, grid_x, grid_y, color=None):
        """Paint a pixel with the current brush"""
        if color is None:
            color = self.current_color
        
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return
        
        current_layer = self.layers[self.current_layer_index]
        
        # Apply brush size and shape
        for dy in range(-self.brush_size + 1, self.brush_size):
            for dx in range(-self.brush_size + 1, self.brush_size):
                px, py = grid_x + dx, grid_y + dy
                
                if not (0 <= px < GRID_SIZE and 0 <= py < GRID_SIZE):
                    continue
                
                # Check brush shape
                if self.current_brush_shape == 'square':
                    current_layer.pixels[py][px] = color
                elif self.current_brush_shape == 'circle':
                    if dx*dx + dy*dy <= (self.brush_size - 0.5)**2:
                        current_layer.pixels[py][px] = color
                elif self.current_brush_shape == 'cross':
                    if dx == 0 or dy == 0:
                        current_layer.pixels[py][px] = color
    
    def fill_area(self, start_x, start_y, new_color):
        """Flood fill algorithm"""
        if not (0 <= start_x < GRID_SIZE and 0 <= start_y < GRID_SIZE):
            return
        
        current_layer = self.layers[self.current_layer_index]
        original_color = current_layer.pixels[start_y][start_x]
        
        if original_color == new_color:
            return
        
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
                continue
            
            if current_layer.pixels[y][x] != original_color:
                continue
            
            current_layer.pixels[y][x] = new_color
            
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
    
    def eyedropper(self, grid_x, grid_y):
        """Pick color from pixel"""
        if not (0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE):
            return
        
        # Check layers from top to bottom
        for layer in reversed(self.layers):
            if layer.visible and layer.pixels[grid_y][grid_x] is not None:
                self.current_color = layer.pixels[grid_y][grid_x]
                return
    
    def apply_gradient(self, start_x, start_y, end_x, end_y):
        """Apply gradient between two points"""
        if start_x == end_x and start_y == end_y:
            return
        
        current_layer = self.layers[self.current_layer_index]
        
        # Calculate distance
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Apply gradient along the line
        steps = int(distance) + 1
        for i in range(steps):
            t = i / max(1, steps - 1)
            x = int(start_x + (end_x - start_x) * t)
            y = int(start_y + (end_y - start_y) * t)
            
            # Interpolate color
            r1, g1, b1 = self.gradient_colors[0]
            r2, g2, b2 = self.gradient_colors[1]
            
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            
            self.paint_pixel(x, y, (r, g, b))
    
    def copy_selection(self):
        """Copy selected area to clipboard"""
        if not self.selection:
            return
        
        x1, y1, x2, y2 = self.selection
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        
        self.clipboard = []
        current_layer = self.layers[self.current_layer_index]
        
        for y in range(y1, y2 + 1):
            row = []
            for x in range(x1, x2 + 1):
                if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                    row.append(current_layer.pixels[y][x])
                else:
                    row.append(None)
            self.clipboard.append(row)
    
    def paste_clipboard(self, start_x, start_y):
        """Paste clipboard at position"""
        if not self.clipboard:
            return
        
        current_layer = self.layers[self.current_layer_index]
        
        for y, row in enumerate(self.clipboard):
            for x, pixel in enumerate(row):
                px, py = start_x + x, start_y + y
                if 0 <= px < GRID_SIZE and 0 <= py < GRID_SIZE and pixel is not None:
                    current_layer.pixels[py][px] = pixel
    
    def export_png(self, filename):
        """Export current frame as PNG"""
        try:
            # Create image array
            img_array = np.zeros((GRID_SIZE, GRID_SIZE, 4), dtype=np.uint8)
            
            # Composite all visible layers
            for layer in self.layers:
                if not layer.visible:
                    continue
                
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        if layer.pixels[y][x] is not None:
                            r, g, b = layer.pixels[y][x]
                            a = layer.opacity
                            
                            # Alpha blending
                            existing_a = img_array[y, x, 3]
                            if existing_a == 0:
                                img_array[y, x] = [r, g, b, a]
                            else:
                                # Simple alpha compositing
                                alpha = a / 255.0
                                img_array[y, x, 0] = int(img_array[y, x, 0] * (1 - alpha) + r * alpha)
                                img_array[y, x, 1] = int(img_array[y, x, 1] * (1 - alpha) + g * alpha)
                                img_array[y, x, 2] = int(img_array[y, x, 2] * (1 - alpha) + b * alpha)
                                img_array[y, x, 3] = min(255, existing_a + a)
            
            # Convert to PIL Image and save
            img = Image.fromarray(img_array, 'RGBA')
            img.save(filename)
            print(f"Exported to {filename}")
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def export_gif(self, filename):
        """Export animation as GIF"""
        try:
            frames = []
            
            for frame in self.animation_frames:
                # Create frame image
                img_array = np.zeros((GRID_SIZE, GRID_SIZE, 4), dtype=np.uint8)
                
                for layer in frame.layers:
                    if not layer.visible:
                        continue
                    
                    for y in range(GRID_SIZE):
                        for x in range(GRID_SIZE):
                            if layer.pixels[y][x] is not None:
                                r, g, b = layer.pixels[y][x]
                                img_array[y, x] = [r, g, b, 255]
                
                img = Image.fromarray(img_array, 'RGBA')
                frames.append(img)
            
            if frames:
                durations = [frame.duration for frame in self.animation_frames]
                frames[0].save(filename, save_all=True, append_images=frames[1:], 
                             duration=durations, loop=0)
                print(f"Animation exported to {filename}")
            
        except Exception as e:
            print(f"GIF export error: {e}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    # Check if clicking in canvas area
                    canvas_width = int(GRID_SIZE * CELL_SIZE * self.zoom_level)
                    if mouse_x < canvas_width:
                        grid_x, grid_y = self.get_grid_pos(event.pos)
                        
                        if self.tool_mode == 'paint':
                            self.drawing = True
                            self.paint_pixel(grid_x, grid_y)
                            self.save_state()
                        elif self.tool_mode == 'fill':
                            self.fill_area(grid_x, grid_y, self.current_color)
                            self.save_state()
                        elif self.tool_mode == 'eyedropper':
                            self.eyedropper(grid_x, grid_y)
                        elif self.tool_mode == 'gradient':
                            if self.gradient_start is None:
                                self.gradient_start = (grid_x, grid_y)
                            else:
                                self.apply_gradient(self.gradient_start[0], self.gradient_start[1], 
                                                  grid_x, grid_y)
                                self.gradient_start = None
                                self.save_state()
                        elif self.tool_mode == 'select':
                            self.selecting = True
                            self.selection = [grid_x, grid_y, grid_x, grid_y]
                    else:
                        # UI interactions
                        self.handle_ui_click(event.pos)
                
                elif event.button == 3:  # Right click
                    if self.tool_mode == 'select' and self.selection:
                        grid_x, grid_y = self.get_grid_pos(event.pos)
                        self.paste_clipboard(grid_x, grid_y)
                        self.save_state()
                
                elif event.button == 4:  # Scroll up
                    self.zoom_level = min(4.0, self.zoom_level * 1.1)
                elif event.button == 5:  # Scroll down
                    self.zoom_level = max(0.25, self.zoom_level / 1.1)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drawing = False
                    self.selecting = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing and self.tool_mode == 'paint':
                    grid_x, grid_y = self.get_grid_pos(event.pos)
                    self.paint_pixel(grid_x, grid_y)
                elif self.selecting:
                    grid_x, grid_y = self.get_grid_pos(event.pos)
                    self.selection[2] = grid_x
                    self.selection[3] = grid_y
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard(event.key)
        
        return True
    
    def handle_keyboard(self, key):
        """Handle keyboard shortcuts"""
        keys = pygame.key.get_pressed()
        ctrl = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        
        if ctrl:
            if key == pygame.K_z:
                self.undo()
            elif key == pygame.K_y:
                self.redo()
            elif key == pygame.K_c:
                self.copy_selection()
            elif key == pygame.K_v:
                if self.selection:
                    grid_x, grid_y = self.selection[0], self.selection[1]
                    self.paste_clipboard(grid_x, grid_y)
                    self.save_state()
            elif key == pygame.K_s:
                self.save_project()
            elif key == pygame.K_o:
                self.load_project()
            elif key == pygame.K_e:
                self.export_png("pixel_art.png")
        else:
            if key == pygame.K_b:
                self.tool_mode = 'paint'
            elif key == pygame.K_f:
                self.tool_mode = 'fill'
            elif key == pygame.K_e:
                self.tool_mode = 'eyedropper'
            elif key == pygame.K_g:
                self.tool_mode = 'gradient'
            elif key == pygame.K_s:
                self.tool_mode = 'select'
            elif key == pygame.K_SPACE:
                self.playing_animation = not self.playing_animation
            elif key == pygame.K_1:
                self.brush_size = 1
            elif key == pygame.K_2:
                self.brush_size = 2
            elif key == pygame.K_3:
                self.brush_size = 3
            elif key == pygame.K_TAB:
                idx = self.brush_shapes.index(self.current_brush_shape)
                self.current_brush_shape = self.brush_shapes[(idx + 1) % len(self.brush_shapes)]
    
    def handle_ui_click(self, pos):
        """Handle UI element clicks"""
        x, y = pos
        panel_x = int(GRID_SIZE * CELL_SIZE * self.zoom_level) + 10
        
        # Color palette
        if panel_x <= x <= panel_x + 200 and 20 <= y <= 200:
            col = (x - panel_x) // 25
            row = (y - 20) // 25
            if 0 <= row < 8 and 0 <= col < 3:
                color_idx = row * 3 + col
                if color_idx < len(COLORS):
                    self.current_color = COLORS[color_idx]
        
        # Tool buttons
        tool_y = 220
        if panel_x <= x <= panel_x + 80 and tool_y <= y <= tool_y + 120:
            tool_idx = (y - tool_y) // 25
            tools = ['paint', 'fill', 'eyedropper', 'gradient', 'select']
            if 0 <= tool_idx < len(tools):
                self.tool_mode = tools[tool_idx]
        
        # Layer buttons
        layer_y = 360
        if panel_x <= x <= panel_x + 150 and layer_y <= y <= layer_y + 100:
            btn_idx = (y - layer_y) // 20
            if btn_idx == 0:  # New layer
                self.layers.append(Layer(GRID_SIZE, GRID_SIZE, f"Layer {len(self.layers)}"))
            elif btn_idx == 1 and len(self.layers) > 1:  # Delete layer
                del self.layers[self.current_layer_index]
                self.current_layer_index = min(self.current_layer_index, len(self.layers) - 1)
            elif btn_idx == 2:  # Layer up
                self.current_layer_index = max(0, self.current_layer_index - 1)
            elif btn_idx == 3:  # Layer down
                self.current_layer_index = min(len(self.layers) - 1, self.current_layer_index + 1)
    
    def update_animation(self):
        """Update animation playback"""
        if self.playing_animation and len(self.animation_frames) > 1:
            self.animation_timer += self.clock.get_time()
            current_frame_obj = self.animation_frames[self.current_frame]
            
            if self.animation_timer >= current_frame_obj.duration:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                # Load frame layers
                self.layers = [layer.copy() for layer in self.animation_frames[self.current_frame].layers]
    
    def draw(self):
        self.screen.fill(LIGHT_GRAY)
        
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                screen_x, screen_y = self.get_screen_pos(x, y)
                size = int(CELL_SIZE * self.zoom_level)
                rect = pygame.Rect(screen_x, screen_y, size, size)
                
                # Draw checker pattern for transparency
                if (x + y) % 2:
                    pygame.draw.rect(self.screen, WHITE, rect)
                else:
                    pygame.draw.rect(self.screen, LIGHT_GRAY, rect)
                
                # Draw pixels from all visible layers
                for layer in self.layers:
                    if layer.visible and layer.pixels[y][x] is not None:
                        color = layer.pixels[y][x]
                        if layer.opacity < 255:
                            # Simple alpha blending with background
                            alpha = layer.opacity / 255.0
                            bg_color = LIGHT_GRAY if (x + y) % 2 == 0 else WHITE
                            r = int(color[0] * alpha + bg_color[0] * (1 - alpha))
                            g = int(color[1] * alpha + bg_color[1] * (1 - alpha))
                            b = int(color[2] * alpha + bg_color[2] * (1 - alpha))
                            color = (r, g, b)
                        pygame.draw.rect(self.screen, color, rect)
                        break
                
                # Draw grid lines
                pygame.draw.rect(self.screen, GRAY, rect, 1)
        
        # Draw selection
        if self.selection:
            x1, y1, x2, y2 = self.selection
            sx1, sy1 = self.get_screen_pos(min(x1, x2), min(y1, y2))
            sx2, sy2 = self.get_screen_pos(max(x1, x2) + 1, max(y1, y2) + 1)
            selection_rect = pygame.Rect(sx1, sy1, sx2 - sx1, sy2 - sy1)
            pygame.draw.rect(self.screen, RED, selection_rect, 2)
        
        self.draw_ui()
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw the user interface panel"""
        panel_x = int(GRID_SIZE * CELL_SIZE * self.zoom_level) + 10
        
        # Color palette
        y_offset = 20
        for i, color in enumerate(COLORS[:24]):  # Show first 24 colors
            row = i // 3
            col = i % 3
            x = panel_x + col * 25
            y = y_offset + row * 25
            
            rect = pygame.Rect(x, y, 20, 20)
            pygame.draw.rect(self.screen, color, rect)
            
            if color == self.current_color:
                pygame.draw.rect(self.screen, WHITE, rect, 2)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Tools
        y_offset = 220
        tools = [
            ('Paint (B)', 'paint'),
            ('Fill (F)', 'fill'),
            ('Eyedropper (E)', 'eyedropper'),
            ('Gradient (G)', 'gradient'),
            ('Select (S)', 'select')
        ]
        
        for i, (name, tool) in enumerate(tools):
            color = GREEN if tool == self.tool_mode else LIGHT_GRAY
            rect = pygame.Rect(panel_x, y_offset + i * 25, 120, 20)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            text = self.small_font.render(name, True, BLACK)
            self.screen.blit(text, (panel_x + 5, y_offset + i * 25 + 3))
        
        # Brush settings
        y_offset = 360
        brush_info = [
            f"Size: {self.brush_size} (1-3)",
            f"Shape: {self.current_brush_shape} (Tab)",
            f"Zoom: {self.zoom_level:.1f}x"
        ]
        
        for i, info in enumerate(brush_info):
            text = self.small_font.render(info, True, BLACK)
            self.screen.blit(text, (panel_x, y_offset + i * 20))
        
        # Layer info
        y_offset = 420
        layer_info = [
            f"Layer: {self.current_layer_index + 1}/{len(self.layers)}",
            f"Name: {self.layers[self.current_layer_index].name}"
        ]
        
        for i, info in enumerate(layer_info):
            text = self.small_font.render(info, True, BLACK)
            self.screen.blit(text, (panel_x, y_offset + i * 20))
        
        # Animation info
        y_offset = 480
        anim_info = [
            f"Frame: {self.current_frame + 1}/{len(self.animation_frames)}",
            f"Playing: {self.playing_animation} (Space)"
        ]
        
        for i, info in enumerate(anim_info):
            text = self.small_font.render(info, True, BLACK)
            self.screen.blit(text, (panel_x, y_offset + i * 20))
        
        # Shortcuts
        y_offset = 520
        shortcuts = [
            "Ctrl+Z: Undo",
            "Ctrl+Y: Redo", 
            "Ctrl+C: Copy",
            "Ctrl+V: Paste",
            "Ctrl+S: Save",
            "Ctrl+E: Export PNG"
        ]
        
        for i, shortcut in enumerate(shortcuts):
            text = self.small_font.render(shortcut, True, BLACK)
            self.screen.blit(text, (panel_x, y_offset + i * 15))
    
    def save_project(self):
        """Save project to JSON"""
        try:
            data = {
                'layers': [],
                'animation_frames': [],
                'current_frame': self.current_frame
            }
            
            for layer in self.layers:
                layer_data = {
                    'name': layer.name,
                    'visible': layer.visible,
                    'opacity': layer.opacity,
                    'pixels': [[[r, g, b] if pixel else None for pixel in row] 
                              for row in layer.pixels]
                }
                data['layers'].append(layer_data)
            
            for frame in self.animation_frames:
                frame_data = {
                    'duration': frame.duration,
                    'layers': []
                }
                for layer in frame.layers:
                    layer_data = {
                        'name': layer.name,
                        'visible': layer.visible,
                        'opacity': layer.opacity,
                        'pixels': [[[r, g, b] if pixel else None for pixel in row] 
                                  for row in layer.pixels]
                    }
                    frame_data['layers'].append(layer_data)
                data['animation_frames'].append(frame_data)
            
            with open('pixel_project.json', 'w') as f:
                json.dump(data, f, indent=2)
            print("Project saved!")
            
        except Exception as e:
            print(f"Save error: {e}")
    
    def load_project(self):
        """Load project from JSON"""
        try:
            with open('pixel_project.json', 'r') as f:
                data = json.load(f)
            
            # Load layers
            self.layers = []
            for layer_data in data['layers']:
                layer = Layer(GRID_SIZE, GRID_SIZE, layer_data['name'])
                layer.visible = layer_data['visible']
                layer.opacity = layer_data['opacity']
                layer.pixels = [[tuple(pixel) if pixel else None for pixel in row] 
                               for row in layer_data['pixels']]
                self.layers.append(layer)
            
            # Load animation frames
            self.animation_frames = []
            for frame_data in data['animation_frames']:
                frame_layers = []
                for layer_data in frame_data['layers']:
                    layer = Layer(GRID_SIZE, GRID_SIZE, layer_data['name'])
                    layer.visible = layer_data['visible']
                    layer.opacity = layer_data['opacity']
                    layer.pixels = [[tuple(pixel) if pixel else None for pixel in row] 
                                   for row in layer_data['pixels']]
                    frame_layers.append(layer)
                
                frame = AnimationFrame(frame_layers, frame_data['duration'])
                self.animation_frames.append(frame)
            
            self.current_frame = data.get('current_frame', 0)
            print("Project loaded!")
            
        except Exception as e:
            print(f"Load error: {e}")
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_animation()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        painter = AdvancedPixelPainter()
        painter.run()
    except ImportError as e:
        print("Missing dependencies! Please install:")
        print("pip install pygame pillow numpy")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error starting application: {e}")