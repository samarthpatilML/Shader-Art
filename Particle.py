import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Particle System")

# Clock for FPS control
clock = pygame.time.Clock()

# Particle class
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(2, 4)
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
        self.life = 100

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        # Add gravity
        self.vy += 0.05

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Particle system
particles = []

# Main loop
running = True
while running:
    screen.fill((10, 10, 30))  # Dark background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Add new particles at mouse position
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        for _ in range(5):  # Emit multiple particles per frame
            particles.append(Particle(mx, my))

    # Update and draw particles
    for p in particles[:]:
        p.update()
        p.draw(screen)
        if p.life <= 0:
            particles.remove(p)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
