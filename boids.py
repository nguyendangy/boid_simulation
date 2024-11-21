import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boid Flocking Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BOID_COLOR = (0, 200, 255)

# Boid parameters
NUM_BOIDS = 50
BOID_RADIUS = 5
SPEED = 2
VIEW_RADIUS = 50
SEPARATION_DISTANCE = 20

# Boid class
class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * SPEED

    def update(self, boids):
        # Compute alignment, cohesion, and separation
        alignment = self.align(boids)
        cohesion = self.cohere(boids)
        separation = self.separate(boids)

        # Adjust velocity
        self.velocity += alignment + cohesion + separation
        self.velocity = self.velocity.normalize() * SPEED

        # Update position
        self.position += self.velocity

        # Wrap around screen edges
        if self.position.x < 0:
            self.position.x = WIDTH
        elif self.position.x > WIDTH:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = HEIGHT
        elif self.position.y > HEIGHT:
            self.position.y = 0

    def align(self, boids):
        avg_velocity = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid):
                avg_velocity += boid.velocity
                count += 1
        if count > 0:
            avg_velocity /= count
            return (avg_velocity - self.velocity) * 0.05  # Alignment weight
        return pygame.Vector2(0, 0)

    def cohere(self, boids):
        center_of_mass = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid):
                center_of_mass += boid.position
                count += 1
        if count > 0:
            center_of_mass /= count
            return (center_of_mass - self.position) * 0.01  # Cohesion weight
        return pygame.Vector2(0, 0)

    def separate(self, boids):
        move_away = pygame.Vector2(0, 0)
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if self.is_in_view(boid) and distance < SEPARATION_DISTANCE:
                move_away -= (boid.position - self.position) / distance
        return move_away * 0.1  # Separation weight

    def is_in_view(self, boid):
        distance = self.position.distance_to(boid.position)
        return distance < VIEW_RADIUS and boid != self

    def draw(self, screen):
        pygame.draw.circle(screen, BOID_COLOR, (int(self.position.x), int(self.position.y)), BOID_RADIUS)

# Create boids
boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]

# Simulation loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill(BLACK)

    # Update and draw boids
    for boid in boids:
        boid.update(boids)
        boid.draw(screen)

    # Refresh screen
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
