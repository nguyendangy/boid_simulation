# This code implements a flocking simulation influenced by weather conditions
# with adjustable parameters such as wind, snow, and fog. Some concepts or
# logic in this code are inspired by examples and resources found on GitHub:
# https://github.com/pramodaya/GeneticAlgorithms

#import important
import pygame

#import random
import random

#inport time
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

# Set boid_screen 
Width_screen, Height_screen = 1200, 800
#set mode
boid_screen = pygame.display.set_mode((Width_screen, Height_screen))
# display caption
pygame.display.set_caption("Weather-Influenced Flocking Simulation")

# Set more color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BOID_COLOR = (0, 200, 255)
SNOW_COLOR = (200, 200, 255)
FOG_COLOR = (255, 255, 255, 150)


# Set Boid parameters
NUM_BOIDS = 50
BOID_RADIUS = 5
BASE_SPEED = 2
ENTITY_VIEW_RADIUS = 50
ENTITY_SEPARATION_DIST = 20
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
BUTTON_Width_screen = 100
BUTTON_Height_screen = 40
BUTTON_MARGIN = 10
button_color = (50, 50, 50)
button_hover_color = (100, 100, 100)
button_text_color = WHITE

# Define button locations
buttons = {
    "Toggle": pygame.Rect(10, Height_screen - 7 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Wind +": pygame.Rect(10, Height_screen - 6 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Wind -": pygame.Rect(120, Height_screen - 6 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Snow +": pygame.Rect(10, Height_screen - 5 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Snow -": pygame.Rect(120, Height_screen - 5 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Fog +": pygame.Rect(10, Height_screen - 4 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
    "Fog -": pygame.Rect(120, Height_screen - 4 * (BUTTON_Height_screen + BUTTON_MARGIN), BUTTON_Width_screen, BUTTON_Height_screen),
}

# Stick controller parameters
stick_center = pygame.Vector2(Width_screen - 150, Height_screen - 150)  # Vị trí trung tâm stick
stick_radius = 50  # Bán kính stick
stick_knob_radius = 15  # Bán kính nút kéo
stick_knob_location = stick_center.copy()  # Vị trí hiện tại của nút
wind_vector = pygame.Vector2(0, 0)

dragging_stick = False  # Trạng thái kéo stick


# Boid class
class Boid:
    def __init__(self, x, y):
        self.location = pygame.Vector2(x, y)  # Tọa độ vị trí
        self.movement = pygame.Vector2(random.uniform(-1, 1),
                                       random.uniform(-1, 1)).normalize() * BASE_SPEED  # Tốc độ di chuyển

    def update(self, boids, wind_vector, snow_intensity, fog_density):
        # Compute alignment, cohesion, separation, and crowd avoidance
        alignment = self.align(boids, fog_density)
        cohesion = self.cohere(boids, fog_density)
        separation = self.separate(boids)
        crowd_avoidance = self.avoid_crowding(boids)

        # Weather influence
        wind_effect = wind_vector * LEVELS[wind_level] if weather_enabled else pygame.Vector2(0, 0)

        # Adjust movement with weather effects and boid behaviors
        self.movement += alignment + cohesion + separation + crowd_avoidance + wind_effect
        slow_factor = 1 - (0.5 * snow_intensity) if weather_enabled else 1.0  # Reduce speed by up to 50% for heavy snow
        self.movement = self.movement.normalize() * max(0.1, BASE_SPEED * slow_factor)

        # Update location
        self.location += self.movement

        # Wrap around boid_screen edges
        if self.location.x < 0:
            self.location.x = Width_screen
        elif self.location.x > Width_screen:
            self.location.x = 0
        if self.location.y < 0:
            self.location.y = Height_screen
        elif self.location.y > Height_screen:
            self.location.y = 0

    def align(self, boids, fog_density):
        avg_movement = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid, fog_density):
                avg_movement += boid.movement
                count += 1
        if count > 0:
            avg_movement /= count
            return (avg_movement - self.movement) * 0.05
        return pygame.Vector2(0, 0)

    def cohere(self, boids, fog_density):
        center_of_mass = pygame.Vector2(0, 0)
        count = 0
        for boid in boids:
            if self.is_in_view(boid, fog_density):
                center_of_mass += boid.location
                count += 1
        if count > 0:
            center_of_mass /= count
            return (center_of_mass - self.location) * 0.01
        return pygame.Vector2(0, 0)

    def separate(self, boids):
        move_away = pygame.Vector2(0, 0)
        for boid in boids:
            distance = self.location.distance_to(boid.location)
            if distance < ENTITY_SEPARATION_DIST and boid != self:
                move_away -= (boid.location - self.location) / distance
        return move_away * 0.1

    def avoid_crowding(self, boids):
        neighbors = [boid for boid in boids if self.location.distance_to(boid.location) < CROWD_RADIUS and boid != self]
        if len(neighbors) > CROWD_THRESHOLD:
            avg_location = sum((boid.location for boid in neighbors), pygame.Vector2(0, 0)) / len(neighbors)
            return (self.location - avg_location) * 0.05
        return pygame.Vector2(0, 0)

    def is_in_view(self, boid, fog_density):
        adjusted_view_radius = max(10, ENTITY_VIEW_RADIUS * (1 - fog_density))
        distance = self.location.distance_to(boid.location)
        return distance < adjusted_view_radius and boid != self

    def draw(self, boid_screen):
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
        pygame.draw.circle(boid_screen, color, (int(self.location.x), int(self.location.y)), BOID_RADIUS)


def draw_buttons(boid_screen):
    for label, rect in buttons.items():
        mouse_pos = pygame.mouse.get_pos()
        color = button_hover_color if rect.collidepoint(mouse_pos) else button_color
        pygame.draw.rect(boid_screen, color, rect)
        text = font.render(label, True, button_text_color)
        text_rect = text.get_rect(center=rect.center)
        boid_screen.blit(text, text_rect)


# Draw stick controller
def draw_stick(boid_screen):
    pygame.draw.circle(boid_screen, (100, 100, 100), (int(stick_center.x), int(stick_center.y)), stick_radius, 2)
    pygame.draw.circle(boid_screen, (200, 200, 200), (int(stick_knob_location.x), int(stick_knob_location.y)),
                       stick_knob_radius)


# Draw wind direction
def draw_wind_direction(boid_screen):
    if weather_enabled and wind_vector.length() > 0:
        arrow_start = stick_center
        arrow_end = stick_center + (wind_vector * 100)  # Scale wind vector for visibility
        pygame.draw.line(boid_screen, WHITE, arrow_start, arrow_end, 2)
        pygame.draw.circle(boid_screen, WHITE, (int(arrow_end.x), int(arrow_end.y)), 5)

        # Tách thành 2 dòng
        direction_text = f"Wind Direction: ({wind_vector.x:.2f}, {wind_vector.y:.2f})"
        intensity_text = f"Wind Intensity: {LEVELS[wind_level]}"

        # Render từng dòng text
        direction_surface = font.render(direction_text, True, WHITE)
        intensity_surface = font.render(intensity_text, True, WHITE)

        # Hiển thị từng dòng với khoảng cách
        boid_screen.blit(direction_surface, (stick_center.x - 150, stick_center.y + 70))
        boid_screen.blit(intensity_surface, (stick_center.x - 150, stick_center.y + 100))


# Update wind vector from stick location
def update_wind_from_stick():
    global wind_vector
    if not weather_enabled:
        wind_vector = pygame.Vector2(0, 0)
    else:
        direction = stick_knob_location - stick_center
        if direction.length() > stick_radius:
            direction = direction.normalize() * stick_radius
        wind_vector = direction / stick_radius  # Normalize hướng gió
        wind_vector *= LEVELS[wind_level]

# Handle stick events
def handle_stick_event(event):
    global dragging_stick, stick_knob_location
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if (stick_knob_location - pygame.Vector2(event.pos)).length() <= stick_knob_radius:
            dragging_stick = True
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        dragging_stick = False
        stick_knob_location = stick_center.copy()  # Reset về trung tâm khi thả
        update_wind_from_stick()
    elif event.type == pygame.MOUSEMOTION and dragging_stick:
        stick_knob_location = pygame.Vector2(event.pos)
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


def display_weather_status(boid_screen):
    status_text = f"Weather: {'On' if weather_enabled else 'Off'}, Wind: {LEVEL_NAMES[wind_level] if weather_enabled else 'None'}, Snow: {LEVEL_NAMES[snow_level] if weather_enabled else 'None'}, Fog: {LEVEL_NAMES[fog_level] if weather_enabled else 'None'}"
    text_surface = font.render(status_text, True, WHITE)
    boid_screen.blit(text_surface, (10, 10))


# Main simulation loop
boids = [Boid(random.randint(0, Width_screen), random.randint(0, Height_screen)) for _ in range(NUM_BOIDS)]
#set running = true
running = True
#set clock by pygame
clock_time = pygame.time.Clock()

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

    # Event handling loop
    for event in pygame.event.get():  # Iterate through all events in the event queue
        if event.type == pygame.QUIT:  # Check if the user closes the window
            running = False  # Set running to False to exit the game loop
            # Check if a mouse button is pressed or released
        handle_button_click(event)  # Call the function to handle button-related events
            # Check if a key is pressed or released
        handle_stick_event(event)  # Call the function to handle stick-related (keyboard) events

    # Clear the boid_screen
    boid_screen.fill(BLACK)

    # Draw buttons
    draw_buttons(boid_screen)

    # Display weather status
    display_weather_status(boid_screen)

    # Draw and update the wind stick
    draw_stick(boid_screen)
    draw_wind_direction(boid_screen)

    # Update and draw boids
    snow_intensity = LEVELS[snow_level] if weather_enabled else 0
    fog_density = LEVELS[fog_level] if weather_enabled else 0

    for boid in boids:
        boid.update(boids, wind_vector, snow_intensity, fog_density)
        boid.draw(boid_screen)

    # Refresh display
    pygame.display.flip()
    clock_time.tick(30)

pygame.quit()