import pygame
import random
import time

# Initialize Pygame
pygame.init()

# experiment
experiment = True
start_time = None
ex1stage = False
ex2stage = False
ex3stage = False
ex4stage = False

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weather-Influenced Flocking Simulation")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BOID_COLOR = (0, 200, 255)
SNOW_COLOR = (200, 200, 255)
FOG_COLOR = (255, 255, 255, 150)

# Boid parameters
NUM_BOIDS = 50
BOID_RADIUS = 5
BASE_SPEED = 2
VIEW_RADIUS = 50
SEPARATION_DISTANCE = 20
CROWD_THRESHOLD = 5  # Maximum number of boids in the local area before moving away
CROWD_RADIUS = 30  # Radius to check for crowding

# Weather levels
LEVELS = [0.0, 0.3, 0.6, 1.0]
LEVEL_NAMES = ["None", "Light", "Medium", "Strong"]

# Initial weather states
wind_level = 0  # Index in LEVELS
snow_level = 0  # Index in LEVELS
fog_level = 0  # Index in LEVELS
weather_enabled = True

# Font for displaying weather status
font = pygame.font.Font(None, 36)

# Button parameters
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
button_color = (50, 50, 50)
button_hover_color = (100, 100, 100)
button_text_color = WHITE

# Define button positions
buttons = {
    "Toggle": pygame.Rect(10, HEIGHT - 7 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Wind +": pygame.Rect(10, HEIGHT - 6 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Wind -": pygame.Rect(120, HEIGHT - 6 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Snow +": pygame.Rect(10, HEIGHT - 5 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Snow -": pygame.Rect(120, HEIGHT - 5 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Fog +": pygame.Rect(10, HEIGHT - 4 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
    "Fog -": pygame.Rect(120, HEIGHT - 4 * (BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT),
}

# Stick controller parameters
stick_center = pygame.Vector2(WIDTH - 150, HEIGHT - 150)  # Vị trí trung tâm stick
stick_radius = 50  # Bán kính stick
stick_knob_radius = 15  # Bán kính nút kéo
stick_knob_position = stick_center.copy()  # Vị trí hiện tại của nút
wind_vector = pygame.Vector2(0, 0)

dragging_stick = False  # Trạng thái kéo stick


# Boid class
class Boid:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * BASE_SPEED

    def update(self, boids, wind_vector, snow_intensity, fog_density):
        # Compute alignment, cohesion, separation, and crowd avoidance
        alignment = self.align(boids, fog_density)
        cohesion = self.cohere(boids, fog_density)
        separation = self.separate(boids)
        crowd_avoidance = self.avoid_crowding(boids)

        # Weather influence
        wind_effect = wind_vector * LEVELS[wind_level] if weather_enabled else pygame.Vector2(0, 0)

        # Adjust velocity with weather effects and boid behaviors
        self.velocity += alignment + cohesion + separation + crowd_avoidance + wind_effect
        slow_factor = 1 - (0.5 * snow_intensity) if weather_enabled else 1.0  # Reduce speed by up to 50% for heavy snow
        self.velocity = self.velocity.normalize() * max(0.1, BASE_SPEED * slow_factor)

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
            return (avg_velocity - self.velocity) * 0.05
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
            return (center_of_mass - self.position) * 0.01
        return pygame.Vector2(0, 0)

    def separate(self, boids):
        move_away = pygame.Vector2(0, 0)
        for boid in boids:
            distance = self.position.distance_to(boid.position)
            if distance < SEPARATION_DISTANCE and boid != self:
                move_away -= (boid.position - self.position) / distance
        return move_away * 0.1

    def avoid_crowding(self, boids):
        neighbors = [boid for boid in boids if self.position.distance_to(boid.position) < CROWD_RADIUS and boid != self]
        if len(neighbors) > CROWD_THRESHOLD:
            avg_position = sum((boid.position for boid in neighbors), pygame.Vector2(0, 0)) / len(neighbors)
            return (self.position - avg_position) * 0.05
        return pygame.Vector2(0, 0)

    def is_in_view(self, boid, fog_density):
        adjusted_view_radius = max(10, VIEW_RADIUS * (1 - fog_density))
        distance = self.position.distance_to(boid.position)
        return distance < adjusted_view_radius and boid != self

    def draw(self, screen):
        # Change color based on snow and fog levels
        if snow_level > 0 and fog_level > 0 and weather_enabled:
            # Blend SNOW_COLOR and FOG_COLOR
            blended_color = (
                (SNOW_COLOR[0] + FOG_COLOR[0]) // 2,
                (SNOW_COLOR[1] + FOG_COLOR[1]) // 2,
                (SNOW_COLOR[2] + FOG_COLOR[2]) // 2
            )
            color = blended_color
        elif snow_level > 0 and weather_enabled:
            color = SNOW_COLOR
        elif fog_level > 0 and weather_enabled:
            color = FOG_COLOR
        else:
            color = BOID_COLOR
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), BOID_RADIUS)


def draw_buttons(screen):
    for label, rect in buttons.items():
        mouse_pos = pygame.mouse.get_pos()
        color = button_hover_color if rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(screen, color, rect)
        text = font.render(label, True, button_text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


# Draw stick controller
def draw_stick(screen):
    pygame.draw.circle(screen, (100, 100, 100), (int(stick_center.x), int(stick_center.y)), stick_radius, 2)
    pygame.draw.circle(screen, (200, 200, 200), (int(stick_knob_position.x), int(stick_knob_position.y)),
                       stick_knob_radius)


# Draw wind direction
def draw_wind_direction(screen):
    if weather_enabled and wind_vector.length() > 0:
        arrow_start = stick_center
        arrow_end = stick_center + (wind_vector * 100)  # Scale wind vector for visibility
        pygame.draw.line(screen, WHITE, arrow_start, arrow_end, 2)
        pygame.draw.circle(screen, WHITE, (int(arrow_end.x), int(arrow_end.y)), 5)

        # Tách thành 2 dòng
        direction_text = f"Wind Direction: ({wind_vector.x:.2f}, {wind_vector.y:.2f})"
        intensity_text = f"Wind Intensity: {LEVELS[wind_level]}"

        # Render từng dòng text
        direction_surface = font.render(direction_text, True, WHITE)
        intensity_surface = font.render(intensity_text, True, WHITE)

        # Hiển thị từng dòng với khoảng cách
        screen.blit(direction_surface, (stick_center.x - 150, stick_center.y + 70))
        screen.blit(intensity_surface, (stick_center.x - 150, stick_center.y + 100))


# Update wind vector from stick position
def update_wind_from_stick():
    global wind_vector
    if not weather_enabled:
        wind_vector = pygame.Vector2(0, 0)
    else:
        direction = stick_knob_position - stick_center
        if direction.length() > stick_radius:
            direction = direction.normalize() * stick_radius
        wind_vector = direction / stick_radius  # Normalize hướng gió
        wind_vector *= LEVELS[wind_level]

# Handle stick events
def handle_stick_event(event):
    global dragging_stick, stick_knob_position
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if (stick_knob_position - pygame.Vector2(event.pos)).length() <= stick_knob_radius:
            dragging_stick = True
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        dragging_stick = False
        stick_knob_position = stick_center.copy()  # Reset về trung tâm khi thả
        update_wind_from_stick()
    elif event.type == pygame.MOUSEMOTION and dragging_stick:
        stick_knob_position = pygame.Vector2(event.pos)
        update_wind_from_stick()


def handle_button_click(event):
    global wind_level, snow_level, fog_level, weather_enabled
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for label, rect in buttons.items():
            if rect.collidepoint(event.pos):
                if label == "Toggle":
                    weather_enabled = not weather_enabled
                    update_wind_from_stick()
                elif label == "Wind +" and weather_enabled and wind_level < 3:
                    wind_level += 1
                elif label == "Wind -" and weather_enabled and wind_level > 0:
                    wind_level -= 1
                elif label == "Snow +" and weather_enabled and snow_level < 3:
                    snow_level += 1
                elif label == "Snow -" and weather_enabled and snow_level > 0:
                    snow_level -= 1
                elif label == "Fog +" and weather_enabled and fog_level < 3:
                    fog_level += 1
                elif label == "Fog -" and weather_enabled and fog_level > 0:
                    fog_level -= 1


def display_weather_status(screen):
    status_text = f"Weather: {'On' if weather_enabled else 'Off'}, Wind: {LEVEL_NAMES[wind_level] if weather_enabled else 'None'}, Snow: {LEVEL_NAMES[snow_level] if weather_enabled else 'None'}, Fog: {LEVEL_NAMES[fog_level] if weather_enabled else 'None'}"
    text_surface = font.render(status_text, True, WHITE)
    screen.blit(text_surface, (10, 10))


# Main simulation loop
boids = [Boid(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_BOIDS)]
running = True
clock = pygame.time.Clock()

while running:
    # experiment
    if experiment:

        current_time = time.time()
        if start_time == None:
            start_time = current_time
            weather_enabled = not weather_enabled
        elif (current_time - start_time >= 10) and not (ex1stage):
            print("10 second passed")
            weather_enabled = not weather_enabled
            fog_level += 1
            # wind_level += 1
            snow_level += 1
            ex1stage = True
        elif (current_time - start_time >= 20) and not (ex2stage):
            print("20 second passed")
            fog_level = 2
            wind_level = 3
            snow_level = 3
            ex2stage = True
        elif (current_time - start_time >= 30) and not (ex3stage):
            print("30 second passed")
            fog_level = 0
            wind_level = 0
            snow_level = 0
            ex3stage = True

            weather_enabled = not weather_enabled


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        handle_button_click(event)
        handle_stick_event(event)

    # Clear the screen
    screen.fill(BLACK)

    # Draw buttons
    draw_buttons(screen)

    # Display weather status
    display_weather_status(screen)

    # Draw and update the wind stick
    draw_stick(screen)
    draw_wind_direction(screen)

    # Update and draw boids
    snow_intensity = LEVELS[snow_level] if weather_enabled else 0
    fog_density = LEVELS[fog_level] if weather_enabled else 0

    for boid in boids:
        boid.update(boids, wind_vector, snow_intensity, fog_density)
        boid.draw(screen)

    # Refresh display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()