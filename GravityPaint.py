import pygame
import random
import math
import sys

# Init
pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🌀 Gravity Paint")
clock = pygame.time.Clock()

# Particle class
class Particle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = (255, 255, 255)
        self.radius = 1

    def update(self, gravity_points):
        for gx, gy in gravity_points:
            dx = gx - self.x
            dy = gy - self.y
            dist_sq = dx * dx + dy * dy
            if dist_sq < 2: continue  # prevent division by zero
            force = min(1000 / dist_sq, 0.5)
            angle = math.atan2(dy, dx)
            self.vx += math.cos(angle) * force
            self.vy += math.sin(angle) * force

        self.x += self.vx
        self.y += self.vy

        # wrap around screen
        if self.x < 0: self.x = WIDTH
        if self.x > WIDTH: self.x = 0
        if self.y < 0: self.y = HEIGHT
        if self.y > HEIGHT: self.y = 0

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)

# Gravity Paint Engine
particles = [Particle() for _ in range(300)]
gravity_points = []
bg = pygame.Surface((WIDTH, HEIGHT))
bg.fill((0, 0, 10))

# Main loop
running = True
while running:
    screen.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Add gravity points on mouse click
    if pygame.mouse.get_pressed()[0]:
        pos = pygame.mouse.get_pos()
        gravity_points.append(pos)

    # Update and draw particles
    for p in particles:
        p.update(gravity_points)
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
# End of Gravity Paint
# This code creates a simple particle system where particles are attracted to gravity points created by mouse clicks.