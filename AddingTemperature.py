import pygame
import random
import csv
import time

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
RAIN_COLOR = (135, 206, 250)  # Light blue for raindrops
FOG_COLOR = (255, 255, 255, 150)  # Semi-transparent white for fog

# Boid parameters
NUM_BOIDS = 50
BOID_RADIUS = 5
BASE_SPEED = 2  # Base speed without weather influence
VIEW_RADIUS = 50
SEPARATION_DISTANCE = 20

# Weather configurations (list of tuples: (wind_x, wind_y, rain, fog, temperature))
WEATHER_CONFIGS = [
    (0.5, 0.2, 0.3, 0.1, 15),  # Mild wind, light rain, light fog, moderate temperature
    (1.0, 0.5, 0.7, 0.5, 30),  # Strong wind, moderate rain, moderate fog, high temperature
    (0.0, 0.0, 0.0, 0.0, 5),   # No wind, no rain, no fog, low temperature
    (0.8, 0.0, 1.0, 0.9, 20),  # Strong wind, heavy rain, dense fog, moderate temperature
]

# Logging setup
log_file = open('flocking_weather_data.csv', 'w', newline='')
log_writer = csv.writer(log_file)
log_writer.writerow(["Time", "Weather_Config", "Avg Speed", "Avg Alignment", "Density", "Cohesion"])

# Font for displaying weather status
font = pygame.font.Font(None, 36)

# Boid class
class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * BASE_SPEED

    def update(self, boids, wind_vector, rain_intensity, fog_density, temperature):
        temp_factor = 1 + ((temperature - 20) / 40)  # Normalize temperature effect
        current_speed = BASE_SPEED * temp_factor

        # Compute alignment, cohesion, and separation
        alignment = self.align(boids, fog_density)
        cohesion = self.cohere(boids, fog_density)
        separation = self.separate(boids, fog_density)

        # Weather influence
        wind_effect = self.apply_wind(wind_vector, rain_intensity)  # Modified wind function
        rain_effect = self.apply_rain(rain_intensity)

        # Adjust velocity with weather effects
        self.velocity += alignment + cohesion + separation + wind_effect + rain_effect
        self.velocity = self.velocity.normalize() * max(0.1, current_speed * (1 - rain_intensity))  # Minimum speed

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

    def align(self, boids, fog_density):
        avg_velocity = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid, fog_density):
                avg_velocity += boid.velocity
                count += 1
        if count > 0:
            avg_velocity /= count
            return (avg_velocity - self.velocity) * 0.05  # Alignment weight
        return pygame.Vector2(0, 0)

    def cohere(self, boids, fog_density):
        center_of_mass = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid, fog_density):
                center_of_mass += boid.position
                count += 1
        if count > 0:
            center_of_mass /= count
            return (center_of_mass - self.position) * 0.01  # Cohesion weight
        return pygame.Vector2(0, 0)

    def separate(self, boids, fog_density):
        move_away = pygame.Vector2(0, 0)
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if self.is_in_view(boid, fog_density) and distance < SEPARATION_DISTANCE:
                move_away -= (boid.position - self.position) / distance
        return move_away * 0.1  # Separation weight

    def apply_wind(self, wind_vector, rain_intensity):
        return wind_vector * (0.1 + rain_intensity * 0.2)  # Wind scales with rain intensity

    def apply_rain(self, rain_intensity):
        return pygame.Vector2(0, 0)  # Rain directly slows down in `update()`

    def is_in_view(self, boid, fog_density):
        adjusted_view_radius = max(10, VIEW_RADIUS * (1 - fog_density))  # Minimum radius for interaction
        distance = self.position.distance_to(boid.position)
        return distance < adjusted_view_radius and boid != self

    def draw(self, screen):
        pygame.draw.circle(screen, BOID_COLOR, (int(self.position.x), int(self.position.y)), BOID_RADIUS)

def draw_wind(screen, wind_vector):
    start_pos = (WIDTH // 2, HEIGHT // 2)
    end_pos = (
        start_pos[0] + int(wind_vector.x * 100),
        start_pos[1] + int(wind_vector.y * 100)
    )
    pygame.draw.line(screen, WHITE, start_pos, end_pos, 3)
    pygame.draw.polygon(screen, WHITE, [
        (end_pos[0], end_pos[1]),
        (end_pos[0] - 10, end_pos[1] - 5),
        (end_pos[0] - 10, end_pos[1] + 5)
    ])

def draw_rain(screen, rain_intensity):
    num_raindrops = int(rain_intensity * 50)
    for _ in range(num_raindrops):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        pygame.draw.line(screen, RAIN_COLOR, (x, y), (x, y + 10), 2)

def draw_fog(screen, fog_density):
    fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fog_surface.fill((255, 255, 255, int(fog_density * 150)))  # Adjust opacity by fog density
    screen.blit(fog_surface, (0, 0))

def log_data(boids, weather_config, fog_density):
    avg_speed = sum(boid.velocity.length() for boid in boids) / len(boids)
    avg_alignment = sum(boid.velocity.angle_to(pygame.Vector2(1, 0)) for boid in boids) / len(boids)
    avg_local_density = calculate_local_density(boids, fog_density)
    cohesion = sum(boid.position.distance_to(pygame.Vector2(WIDTH / 2, HEIGHT / 2)) for boid in boids) / len(boids)
    log_writer.writerow([time.time(), weather_config, avg_speed, avg_alignment, avg_local_density, cohesion])

def calculate_local_density(boids, fog_density):
    adjusted_radius = max(10, VIEW_RADIUS * (1 - fog_density))
    total_neighbors = 0
    for boid in boids:
        neighbor_count = sum(
            1 for other_boid in boids
            if other_boid != boid and boid.position.distance_to(other_boid.position) <= adjusted_radius
        )
        total_neighbors += neighbor_count
    return total_neighbors / len(boids)

def display_weather_status(screen, config):
    wind_x, wind_y, rain, fog, temp = config
    status_text = f"Wind: ({wind_x}, {wind_y}), Rain: {rain}, Fog: {fog}, Temp: {temp}°C"
    text_surface = font.render(status_text, True, WHITE)
    screen.blit(text_surface, (10, 10))

# Main simulation loop for all weather configs
for config in WEATHER_CONFIGS:
    wind_vector = pygame.Vector2(config[0], config[1])
    rain_intensity = config[2]
    fog_density = config[3]
    temperature = config[4]

    boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]
    running = True
    clock = pygame.time.Clock()
    sim_time = 10  # Run each simulation for 10 seconds
    start_time = time.time()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if time.time() - start_time > sim_time:
            running = False

            # Clear the screen
        screen.fill(BLACK)

        # Display weather status
        display_weather_status(screen, config)

        # Draw weather effects
        draw_wind(screen, wind_vector)
        draw_rain(screen, rain_intensity)
        draw_fog(screen, fog_density)

        # Update and draw boids
        for boid in boids:
            boid.update(boids, wind_vector, rain_intensity, fog_density, temperature)
            boid.draw(screen)

        # Log data for this configuration
        log_data(boids, config, fog_density)

        # Refresh the display
        pygame.display.flip()
        clock.tick(30)

# Close log file and quit Pygame
log_file.close()
pygame.quit()
