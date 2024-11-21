import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weather-Influenced Flocking Simulation")

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

# Weather parameters
WIND_VECTOR = pygame.Vector2(0.5, 0.2)  # Wind blowing right and slightly down
RAIN_INTENSITY = 0.3  # Affects speed (0: no rain, 1: heavy rain)
FOG_DENSITY = 0.3  # Affects visibility (0: clear, 1: dense fog)

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

        # Weather influence
        wind_effect = self.apply_wind()
        rain_effect = self.apply_rain()

        # Adjust velocity with weather effects
        self.velocity += alignment + cohesion + separation + wind_effect + rain_effect
        self.velocity = self.velocity.normalize() * SPEED * (1 - RAIN_INTENSITY)

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

    def apply_wind(self):
        # Add wind effect to the velocity
        return WIND_VECTOR * 0.1  # Adjust weight of wind influence

    def apply_rain(self):
        # Slow down the boid slightly in rain
        return pygame.Vector2(0, 0)  # Rain directly affects speed in `update()`

    def is_in_view(self, boid):
        # Adjust view radius based on fog density
        adjusted_view_radius = VIEW_RADIUS * (1 - FOG_DENSITY)
        distance = self.position.distance_to(boid.position)
        return distance < adjusted_view_radius and boid != self

    def draw(self, screen):
        pygame.draw.circle(screen, BOID_COLOR, (int(self.position.x), int(self.position.y)), BOID_RADIUS)

# Weather Visualization
def draw_wind(screen):
    """Draw arrows to represent wind direction and strength."""
    start_pos = (WIDTH // 2, HEIGHT // 2)  # Center of the screen
    end_pos = (
        WIDTH // 2 + int(WIND_VECTOR.x * 100),  # Scaled wind vector for visualization
        HEIGHT // 2 + int(WIND_VECTOR.y * 100)
    )
    pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
    pygame.draw.polygon(screen, WHITE, [
        (end_pos[0], end_pos[1]),
        (end_pos[0] - 10, end_pos[1] - 5),
        (end_pos[0] - 10, end_pos[1] + 5)
    ])  # Arrowhead

def draw_rain(screen):
    """Draw falling raindrops."""
    for _ in range(50):  # Number of raindrops
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.line(screen, (135, 206, 250), (x, y), (x, y + 10), 2)  # Raindrop

def draw_fog(screen):
    """Overlay a semi-transparent fog layer."""
    fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog_surface.fill((255, 255, 255, int(FOG_DENSITY * 150)))  # Adjust opacity by fog density
    screen.blit(fog_surface, (0, 0))

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

    # Draw weather effects
    draw_wind(screen)
    draw_rain(screen)
    draw_fog(screen)

    # Update and draw boids
    for boid in boids:
        boid.update(boids)
        boid.draw(screen)

    # Refresh screen
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
