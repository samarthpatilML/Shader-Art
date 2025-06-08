import pygame
import numpy as np
import math
import random
import time
from typing import List, Tuple

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60
NUM_PARTICLES = 150

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255),
    (255, 255, 100), (255, 100, 255), (100, 255, 255),
    (255, 150, 50), (150, 255, 50), (50, 150, 255)
]

class Particle:
    def __init__(self, x: float, y: float, z: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y  
        self.z = z
        self.original_x = x
        self.original_y = y
        self.original_z = z
        self.color = color
        self.size = 3
        self.trail = []
        self.max_trail_length = 20
        
    def update_position(self, new_x: float, new_y: float, new_z: float):
        # Add current position to trail
        if len(self.trail) >= self.max_trail_length:
            self.trail.pop(0)
        self.trail.append((self.x, self.y, self.z))
        
        self.x = new_x
        self.y = new_y
        self.z = new_z
    
    def project_2d(self, camera_distance: float = 300) -> Tuple[int, int, int]:
        """Project 3D coordinates to 2D screen coordinates"""
        if self.z + camera_distance == 0:
            return WIDTH//2, HEIGHT//2, 1
            
        scale = camera_distance / (self.z + camera_distance)
        screen_x = int(WIDTH//2 + self.x * scale)
        screen_y = int(HEIGHT//2 + self.y * scale)
        projected_size = max(1, int(self.size * scale))
        
        return screen_x, screen_y, projected_size

class SonicOrbs:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Interactive Sonic Orbs")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Animation variables
        self.angle = 0
        self.pattern = 0
        self.patterns = [
            "Orbital Dance", "Spiral Galaxy", "Wave Motion", 
            "Flower Bloom", "Chaos Storm", "DNA Helix"
        ]
        
        # Audio simulation variables
        self.audio_energy = 0
        self.bass_energy = 0
        self.mid_energy = 0
        self.high_energy = 0
        self.beat_detected = False
        self.last_beat_time = 0
        
        # Settings
        self.auto_mode = False
        self.show_trails = True
        self.rainbow_mode = False
        self.beat_flash = True
        self.paused = False
        self.speed = 1.0
        self.sensitivity = 1.0
        self.camera_distance = 300
        self.rotation_x = 0
        self.rotation_y = 0
        
        # Create particles
        self.particles = self.create_particles()
        
        # Font for UI
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Flash effect
        self.flash_intensity = 0
        
    def create_particles(self) -> List[Particle]:
        particles = []
        for i in range(NUM_PARTICLES):
            angle = (i / NUM_PARTICLES) * 2 * math.pi
            x = math.sin(angle) * 100
            y = math.cos(angle) * 100
            z = 0
            color = COLORS[i % len(COLORS)]
            particles.append(Particle(x, y, z, color))
        return particles
    
    def simulate_audio(self):
        """Simulate audio input with mathematical functions"""
        current_time = time.time()
        
        # Generate fake audio energy based on time
        self.bass_energy = abs(math.sin(current_time * 0.5)) * 100
        self.mid_energy = abs(math.sin(current_time * 1.2)) * 80
        self.high_energy = abs(math.sin(current_time * 2.5)) * 60
        self.audio_energy = (self.bass_energy + self.mid_energy + self.high_energy) / 3
        
        # Simulate beat detection
        if self.audio_energy > 70 and current_time - self.last_beat_time > 0.5:
            self.beat_detected = True
            self.last_beat_time = current_time
            if self.beat_flash:
                self.flash_intensity = 255
    
    def update_pattern_0(self, i: int, particle: Particle):
        """Orbital Dance"""
        theta = self.angle + i * 0.1
        radius = (self.audio_energy * self.sensitivity / 2) + 50 + math.sin(theta * 3) * 20
        particle.update_position(
            math.sin(theta) * radius,
            math.cos(theta) * radius,
            math.sin(theta * 0.5) * (self.audio_energy * self.sensitivity / 5)
        )
    
    def update_pattern_1(self, i: int, particle: Particle):
        """Spiral Galaxy"""  
        theta = self.angle + i * 0.05
        spiral_r = (i / NUM_PARTICLES) * (self.audio_energy * self.sensitivity / 2 + 50)
        particle.update_position(
            math.sin(theta) * spiral_r,
            math.cos(theta) * spiral_r,
            math.sin(self.angle + i * 0.2) * (self.audio_energy * self.sensitivity / 4)
        )
    
    def update_pattern_2(self, i: int, particle: Particle):
        """Wave Motion"""
        wave_x = i * 4 - NUM_PARTICLES * 2
        wave_y = math.sin(self.angle * 2 + i * 0.3) * (self.audio_energy * self.sensitivity / 2 + 30)
        wave_z = math.cos(self.angle + i * 0.1) * (self.audio_energy * self.sensitivity / 4)
        particle.update_position(wave_x, wave_y, wave_z)
    
    def update_pattern_3(self, i: int, particle: Particle):
        """Flower Bloom"""
        petal_angle = self.angle + (i / NUM_PARTICLES) * 12 * math.pi
        petal_r = (self.audio_energy * self.sensitivity / 3 + 40) * (1 + math.sin(petal_angle * 6) * 0.5)
        particle.update_position(
            math.sin(petal_angle) * petal_r,
            math.cos(petal_angle) * petal_r,
            math.sin(self.angle * 2 + i * 0.1) * (self.audio_energy * self.sensitivity / 6)
        )
    
    def update_pattern_4(self, i: int, particle: Particle):
        """Chaos Storm"""
        chaos_x = math.sin(self.angle * 3 + i) * (self.audio_energy * self.sensitivity / 2 + 60)
        chaos_y = math.cos(self.angle * 2 + i * 1.5) * (self.audio_energy * self.sensitivity / 2 + 60)
        chaos_z = math.sin(self.angle + i * 0.7) * (self.audio_energy * self.sensitivity / 3)
        particle.update_position(chaos_x, chaos_y, chaos_z)
    
    def update_pattern_5(self, i: int, particle: Particle):
        """DNA Helix"""
        helix_angle = self.angle + i * 0.2
        radius = 50 + self.audio_energy * self.sensitivity / 4
        height = i * 3 - NUM_PARTICLES * 1.5
        
        if i % 2 == 0:
            x = math.sin(helix_angle) * radius
            y = math.cos(helix_angle) * radius
        else:
            x = math.sin(helix_angle + math.pi) * radius
            y = math.cos(helix_angle + math.pi) * radius
            
        particle.update_position(x, y, height)
    
    def update_particles(self):
        """Update all particles based on current pattern"""
        if self.paused:
            return
            
        pattern_functions = [
            self.update_pattern_0, self.update_pattern_1, self.update_pattern_2,
            self.update_pattern_3, self.update_pattern_4, self.update_pattern_5
        ]
        
        for i, particle in enumerate(self.particles):
            pattern_functions[self.pattern](i, particle)
            
            # Update particle size based on audio
            particle.size = 3 + int(self.bass_energy / 30)
            
            # Rainbow mode
            if self.rainbow_mode:
                hue = (self.angle + i * 0.1) % (2 * math.pi)
                r = int(127 * (1 + math.sin(hue)))
                g = int(127 * (1 + math.sin(hue + 2*math.pi/3)))
                b = int(127 * (1 + math.sin(hue + 4*math.pi/3)))
                particle.color = (r, g, b)
    
    def apply_rotation(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Apply 3D rotation to coordinates"""
        # Rotation around Y axis
        cos_y, sin_y = math.cos(self.rotation_y), math.sin(self.rotation_y)
        new_x = x * cos_y - z * sin_y
        new_z = x * sin_y + z * cos_y
        
        # Rotation around X axis  
        cos_x, sin_x = math.cos(self.rotation_x), math.sin(self.rotation_x)
        new_y = y * cos_x - new_z * sin_x
        final_z = y * sin_x + new_z * cos_x
        
        return new_x, new_y, final_z
    
    def draw_particle_trails(self, particle: Particle):
        """Draw particle trails"""
        if not self.show_trails or len(particle.trail) < 2:
            return
            
        for i in range(len(particle.trail) - 1):
            x1, y1, z1 = self.apply_rotation(*particle.trail[i])
            x2, y2, z2 = self.apply_rotation(*particle.trail[i + 1])
            
            # Project to 2D
            if z1 + self.camera_distance > 0 and z2 + self.camera_distance > 0:
                scale1 = self.camera_distance / (z1 + self.camera_distance)
                scale2 = self.camera_distance / (z2 + self.camera_distance)
                
                screen_x1 = int(WIDTH//2 + x1 * scale1)
                screen_y1 = int(HEIGHT//2 + y1 * scale1)
                screen_x2 = int(WIDTH//2 + x2 * scale2)
                screen_y2 = int(HEIGHT//2 + y2 * scale2)
                
                # Fade trail
                alpha = (i / len(particle.trail)) * 128
                trail_color = (*particle.color, int(alpha))
                
                if 0 <= screen_x1 < WIDTH and 0 <= screen_y1 < HEIGHT and \
                   0 <= screen_x2 < WIDTH and 0 <= screen_y2 < HEIGHT:
                    pygame.draw.line(self.screen, particle.color[:3], 
                                   (screen_x1, screen_y1), (screen_x2, screen_y2), 1)
    
    def draw(self):
        """Main drawing function"""
        # Clear screen with flash effect
        if self.flash_intensity > 0:
            flash_color = (self.flash_intensity//4, self.flash_intensity//4, self.flash_intensity//4)
            self.screen.fill(flash_color)
            self.flash_intensity = max(0, self.flash_intensity - 15)
        else:
            self.screen.fill(BLACK)
        
        # Draw particles and trails
        particles_2d = []
        
        for particle in self.particles:
            # Draw trails first
            self.draw_particle_trails(particle)
            
            # Apply rotation and project to 2D
            rotated_x, rotated_y, rotated_z = self.apply_rotation(particle.x, particle.y, particle.z)
            
            if rotated_z + self.camera_distance > 0:
                scale = self.camera_distance / (rotated_z + self.camera_distance)
                screen_x = int(WIDTH//2 + rotated_x * scale)
                screen_y = int(HEIGHT//2 + rotated_y * scale)
                size = max(1, int(particle.size * scale))
                
                particles_2d.append((screen_x, screen_y, size, particle.color, rotated_z))
        
        # Sort by z-depth for proper rendering
        particles_2d.sort(key=lambda p: p[4], reverse=True)
        
        # Draw particles
        for screen_x, screen_y, size, color, _ in particles_2d:
            if 0 <= screen_x < WIDTH and 0 <= screen_y < HEIGHT:
                # Draw glow effect
                glow_size = size * 3
                glow_color = (color[0]//3, color[1]//3, color[2]//3)
                if glow_size > 2:
                    pygame.draw.circle(self.screen, glow_color, (screen_x, screen_y), glow_size)
                
                # Draw main particle
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)
                
                # Add highlight
                highlight_color = (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
                if size > 2:
                    pygame.draw.circle(self.screen, highlight_color, 
                                     (screen_x - size//3, screen_y - size//3), max(1, size//3))
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw user interface"""
        y_offset = 10
        
        # Title
        title = self.font.render("Interactive Sonic Orbs", True, WHITE)
        self.screen.blit(title, (10, y_offset))
        y_offset += 30
        
        # Current pattern
        pattern_text = self.small_font.render(f"Pattern: {self.patterns[self.pattern]}", True, WHITE)
        self.screen.blit(pattern_text, (10, y_offset))
        y_offset += 20
        
        # Audio info
        audio_text = self.small_font.render(f"Audio Energy: {self.audio_energy:.1f}", True, WHITE)
        self.screen.blit(audio_text, (10, y_offset))
        y_offset += 20
        
        # Status
        status = []
        if self.paused: status.append("PAUSED")
        if self.auto_mode: status.append("AUTO")
        if self.show_trails: status.append("TRAILS")
        if self.rainbow_mode: status.append("RAINBOW")
        
        if status:
            status_text = self.small_font.render(" | ".join(status), True, (100, 255, 100))
            self.screen.blit(status_text, (10, y_offset))
        y_offset += 30
        
        # Controls
        controls = [
            "Controls:",
            "1-6: Change patterns",
            "SPACE: Pause/Resume", 
            "A: Auto mode",
            "T: Toggle trails",
            "R: Rainbow mode",
            "F: Beat flash",
            "Mouse: Rotate view",
            "Wheel: Zoom",
            "+/-: Speed",
            "ESC: Exit"
        ]
        
        for i, control in enumerate(controls):
            color = WHITE if i == 0 else (150, 150, 150)
            control_text = self.small_font.render(control, True, color)
            self.screen.blit(control_text, (10, y_offset))
            y_offset += 18
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_a:
                    self.auto_mode = not self.auto_mode
                elif event.key == pygame.K_t:
                    self.show_trails = not self.show_trails
                elif event.key == pygame.K_r:
                    self.rainbow_mode = not self.rainbow_mode
                elif event.key == pygame.K_f:
                    self.beat_flash = not self.beat_flash
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.speed = min(3.0, self.speed + 0.1)
                elif event.key == pygame.K_MINUS:
                    self.speed = max(0.1, self.speed - 0.1)
                elif pygame.K_1 <= event.key <= pygame.K_6:
                    self.pattern = event.key - pygame.K_1
                    self.auto_mode = False
            
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    dx, dy = event.rel
                    self.rotation_y += dx * 0.01
                    self.rotation_x += dy * 0.01
                    self.rotation_x = max(-math.pi/2, min(math.pi/2, self.rotation_x))
            
            elif event.type == pygame.MOUSEWHEEL:
                self.camera_distance = max(100, min(800, self.camera_distance - event.y * 20))
    
    def run(self):
        """Main game loop"""
        print("Interactive Sonic Orbs Started!")
        print("Use keys 1-6 to change patterns, Space to pause, Mouse to rotate view")
        
        last_pattern_change = time.time()
        
        while self.running:
            self.handle_events()
            
            # Auto pattern switching
            if self.auto_mode and time.time() - last_pattern_change > 5:
                self.pattern = (self.pattern + 1) % len(self.patterns)
                last_pattern_change = time.time()
            
            # Update simulation
            self.simulate_audio()
            self.angle += 0.02 * self.speed
            self.update_particles()
            
            # Draw everything
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    app = SonicOrbs()
    app.run()