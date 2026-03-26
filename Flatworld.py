import random
import pygame
from math import *

# Global particle system for visual effects
particles = []

def draw_radial_gradient(surface, center, radius, color1, color2):
    """Draw a radial gradient circle from color1 (center) to color2 (edge)."""
    if radius <= 0:
        return
    
    # Create a temporary surface for the gradient
    size = int(radius * 2) + 2
    temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Draw concentric circles with interpolated colors
    for r in range(int(radius), 0, -1):
        ratio = r / radius
        # Interpolate between color1 and color2
        r_val = int(color1.r * ratio + color2.r * (1 - ratio))
        g_val = int(color1.g * ratio + color2.g * (1 - ratio))
        b_val = int(color1.b * ratio + color2.b * (1 - ratio))
        a_val = int(color1.a * ratio + color2.a * (1 - ratio)) if hasattr(color1, 'a') else 255
        
        color = pygame.Color(r_val, g_val, b_val, a_val)
        pygame.draw.circle(temp_surface, color, (size // 2, size // 2), r)
    
    # Blit the gradient surface onto the main surface
    surface.blit(temp_surface, (center.x - size // 2, center.y - size // 2))

def draw_shadow(surface, center, radius, shadow_offset=(5, 6), shape_type='circle'):
    """Draw a drop shadow. Light source is upper left, so shadow goes down-right.
    shape_type: 'circle' for circular shadows, 'triangle' for triangular shadows"""
    # Subtly darker pink shadow
    shadow_color = pygame.Color(200, 150, 160, 60)  # Semi-transparent darker pink
    shadow_pos = pygame.Vector2(center.x + shadow_offset[0], 
                                 center.y + shadow_offset[1])
    if shape_type == 'triangle':
        # Draw triangular shadow - need triangle points
        # This will be called with triangle points separately
        pass
    else:
        # Circular shadow
        pygame.draw.circle(surface, shadow_color, shadow_pos, radius)

def draw_triangle_shadow(surface, triangle_points, shadow_offset=(5, 6)):
    """Draw a triangular shadow offset down-right from the triangle."""
    shadow_color = pygame.Color(200, 150, 160, 60)
    shadow_points = [(p[0] + shadow_offset[0], p[1] + shadow_offset[1]) for p in triangle_points]
    pygame.draw.polygon(surface, shadow_color, shadow_points)

def add_particle(position, velocity, color, lifetime=1.0, size=3):
    """Add a particle to the particle system."""
    particles.append({
        'position': pygame.Vector2(position),
        'velocity': pygame.Vector2(velocity),
        'color': color,
        'lifetime': lifetime,
        'max_lifetime': lifetime,
        'size': size
    })

def update_particles(secondsSinceLastFrame):
    """Update and remove expired particles."""
    global particles
    new_particles = []
    for p in particles:
        p['lifetime'] -= secondsSinceLastFrame
        if p['lifetime'] > 0:
            p['position'] += p['velocity'] * secondsSinceLastFrame
            p['velocity'] *= 0.95  # Friction
            new_particles.append(p)
    particles = new_particles

def draw_particles(surface):
    """Draw all active particles."""
    for p in particles:
        alpha = int(255 * (p['lifetime'] / p['max_lifetime']))
        color = pygame.Color(p['color'].r, p['color'].g, p['color'].b, alpha)
        size = int(p['size'] * (p['lifetime'] / p['max_lifetime']))
        if size > 0:
            pygame.draw.circle(surface, color, (int(p['position'].x), int(p['position'].y)), size)

def draw_background(surface, width, height):
    """Draw a subtle background pattern for depth."""
    # Light stylish pastel pink background
    surface.fill(pygame.Color(255, 230, 240))

def mainLoop(initialSpawns, spawnInterval, 
                     periodicSpawns, boardSize, playerType):
    global organisms, field
    
    field = pygame.display.set_mode(boardSize)
    clock = pygame.time.Clock( )
    running = True
    organisms = [ ]
    doSpawns(initialSpawns)
    tickCounter = 0

    while any([isinstance(organism, playerType) \
                       for organism in organisms]) \
            and running:
        tickCounter += 1
        secondsSinceLastFrame  = clock.tick(60) / 1000
        
        for event in pygame.event.get( ):
            if event.type == pygame.QUIT:
                running = False

        # Draw background
        draw_background(field, field.get_width(), field.get_height())
        
        # Update particles
        update_particles(secondsSinceLastFrame)
        draw_particles(field)

        for organism in organisms:
            organism.tick(secondsSinceLastFrame)

        if tickCounter % spawnInterval == 0:
            doSpawns(periodicSpawns)

        pygame.display.flip( )
    
    return tickCounter

def doSpawns(spawns):
    global organisms

    for sort in spawns:
        for i in range(spawns[sort]):
            organisms.append(sort(randomDrop( )))

def randomDrop():
    w = field.get_width( )
    h = field.get_height( )
    while True:
        position = pygame.Vector2(random.random( ) * w,
                                            random.random( ) * h)
        organism = anyCollision(position)
        if organism == None:
            return position

def anyCollision(position, ignore = None ,
                        ignoreType = type(None)):
    for organism in organisms:
        if organism != ignore and \
                    not isinstance(organism, ignoreType):
            if (organism.position - position).length() < 20:
                return organism
    return None

class Organism:
    def __init__(self, position):
        self.position = position

    def tick(self, secondsSinceLastFrame):
        self.draw(self.position)

    def getBitten(self):
        pass

    def bearing(self, other):
        return (other.position - self.position).as_polar( )

    def moveTo(self, newPosition):
        if newPosition.x < 0:
            newPosition.x = 0

        if newPosition.x >= field.get_width( ):
            newPosition.x = field.get_width( ) - 1

        if newPosition.y < 0:
            newPosition.y = 0

        if newPosition.y >= field.get_height( ):
            newPosition.y = field.get_height( ) - 1

        organism = anyCollision(newPosition, ignore=self)

        if organism != None:
            return organism
        else:   
            self.position = newPosition
            return None
            
class Creature(Organism):
    def __init__(self, position, speed, color):
        super( ).__init__(position)
        self.speed = speed
        self.color = color
        self.last_position = pygame.Vector2(position)
        self.radius = 10
    
    def draw(self, position):
        # Convert color string to Color object if needed
        if isinstance(self.color, str):
            base_color = pygame.Color(self.color)
        else:
            base_color = pygame.Color(self.color)
        
        # Create colors for 3D shading
        light_color = pygame.Color(
            min(255, base_color.r + 50),
            min(255, base_color.g + 50),
            min(255, base_color.b + 50)
        )
        dark_color = pygame.Color(
            max(0, base_color.r - 100),
            max(0, base_color.g - 100),
            max(0, base_color.b - 100)
        )
        side_color = pygame.Color(
            max(0, base_color.r - 60),
            max(0, base_color.g - 60),
            max(0, base_color.b - 60)
        )
        
        # Draw extruded 3D cylinder (isometric view)
        shadow_offset = (5, 6)
        
        # Bottom circle (shadow/base) - offset down-right
        bottom_center = pygame.Vector2(position.x + shadow_offset[0], position.y + shadow_offset[1])
        shadow_color = pygame.Color(200, 150, 160, 60)
        pygame.draw.circle(field, shadow_color, bottom_center, self.radius)
        
        # Draw visible side edges of cylinder (connecting top to bottom)
        # Draw arcs on the visible side (bottom-right portion)
        for angle in range(135, 315, 10):  # Bottom-right half
            rad = radians(angle)
            top_x = position.x + self.radius * cos(rad)
            top_y = position.y + self.radius * sin(rad)
            bottom_x = top_x + shadow_offset[0]
            bottom_y = top_y + shadow_offset[1]
            pygame.draw.line(field, side_color, (top_x, top_y), (bottom_x, bottom_y), 2)
        
        # Top circle (brighter, main visible face) - drawn last so it's on top
        temp_size = int(self.radius * 2.5)
        temp_surface = pygame.Surface((temp_size, temp_size), pygame.SRCALPHA)
        center_x, center_y = temp_size // 2, temp_size // 2
        
        # Draw top circle with gradient
        for r in range(int(self.radius), 0, -1):
            ratio = r / self.radius
            r_val = int(base_color.r * (0.7 + 0.3 * ratio) + dark_color.r * (1 - ratio))
            g_val = int(base_color.g * (0.7 + 0.3 * ratio) + dark_color.g * (1 - ratio))
            b_val = int(base_color.b * (0.7 + 0.3 * ratio) + dark_color.b * (1 - ratio))
            color = pygame.Color(r_val, g_val, b_val)
            pygame.draw.circle(temp_surface, color, (center_x, center_y), r)
        
        # Add highlight on upper left
        highlight_size = int(self.radius * 0.4)
        highlight_pos = (center_x - int(self.radius * 0.3), center_y - int(self.radius * 0.3))
        pygame.draw.circle(temp_surface, light_color, highlight_pos, highlight_size)
        
        field.blit(temp_surface, (int(position.x - temp_size // 2), int(position.y - temp_size // 2)))
        
        # Draw direction indicator if moving
        if hasattr(self, 'direction') and self.direction.length() > 0.1:
            dir_vec = self.direction.normalize() * (self.radius + 3)
            indicator_pos = position + dir_vec
            pygame.draw.circle(field, pygame.Color(255, 255, 255, 200), 
                             indicator_pos, 3)

    def tick(self, secSinceLast):
        vector = self.moveDirection( )
        r, angle = vector.as_polar( )
        
        # Store direction for drawing
        if r != 0:
            self.direction = pygame.Vector2(vector).normalize()
            vector.scale_to_length(self.speed * secSinceLast)
        else:
            self.direction = pygame.Vector2()
        
        # Add particle trail when moving
        if r > 0.1 and hasattr(self, 'last_position'):
            movement = (self.position - self.last_position).length()
            if movement > 1:
                # Add trailing particles
                trail_color = pygame.Color(self.color)
                trail_color.a = 100
                for _ in range(2):
                    offset = pygame.Vector2(
                        random.uniform(-3, 3),
                        random.uniform(-3, 3)
                    )
                    velocity = -self.direction * 50 + offset * 20
                    add_particle(self.position + offset, velocity, trail_color, 
                               lifetime=0.3, size=2)
        
        newPosition = self.position + vector
        blocker = self.moveTo(newPosition)
        if blocker != None:
            self.hit(blocker)
        
        self.last_position = pygame.Vector2(self.position)
        super( ).tick(secSinceLast)

    def hit(self, blocker):
        pass
    
    def moveDirection(self):
        return pygame.Vector2( )

class Grass(Organism):
    def __init__(self, position):
        super( ).__init__(position)
        self.leaves = 5

    def getBitten(self):
        if self.leaves > 0:
            self.leaves -= 1
            if self.leaves <= 0:
                organisms.remove(self)

    def draw(self, position):
        # Draw shadow (light from upper left, shadow down-right)
        draw_shadow(field, position, 8, shadow_offset=(4, 5))
        
        a = int(position.x - 10)
        b = int(position.x + 10)
        c = int(position.x)

        top = int(position.y - 10)
        bottom = int(position.y + 10)

        s = 20 // max(1, self.leaves)
        
        # Health affects color intensity
        health_ratio = self.leaves / 5.0
        base_green = pygame.Color(34, 139, 34)  # Forest green
        light_green = pygame.Color(
            min(255, int(34 + (100 * health_ratio))),
            min(255, int(139 + (100 * health_ratio))),
            min(255, int(34 + (50 * health_ratio)))
        )
        dark_green = pygame.Color(
            max(0, int(34 - 20)),
            max(0, int(139 - 20)),
            max(0, int(34 - 10))
        )

        for x in range(a + s // 2, b, s):
            # Draw gradient line for each leaf
            start_pos = (c, bottom)
            end_pos = (x, top)
            
            # Draw multiple lines with gradient effect
            for i in range(3):
                offset = i - 1
                line_start = (start_pos[0] + offset, start_pos[1])
                line_end = (end_pos[0] + offset, end_pos[1])
                
                # Interpolate color based on position along leaf
                if i == 1:  # Center line - brightest
                    color = light_green
                else:  # Edge lines - darker
                    color = dark_green
                
                pygame.draw.line(field, color, line_start, line_end, 2)
            
class Blue(Creature):
    def __init__(self, position):
        super().__init__(position, 300, 'blue')

    def getBitten(self):
        global creatures
        organisms.remove(self)

    def tick(self, secondsSinceLastFrame):
        self.speed *= 0.9999
        super().tick(secondsSinceLastFrame)

    def hit(self, blocker):
        if isinstance(blocker, Grass):
            self.speed += 1
            # Add eating effect particles
            for _ in range(5):
                offset = pygame.Vector2(
                    random.uniform(-5, 5),
                    random.uniform(-5, 5)
                )
                velocity = offset * 30
                green_color = pygame.Color(34, 139, 34, 150)
                add_particle(blocker.position + offset, velocity, green_color,
                           lifetime=0.4, size=3)
            blocker.getBitten( )

class Player(Blue):
    def moveDirection(self):
        keys = pygame.key.get_pressed( )
        vector = pygame.Vector2( )
        if keys[pygame.K_w]:
            vector.y = -1
        if keys[pygame.K_s]:
            vector.y = 1
        if keys[pygame.K_a]:
            vector.x = -1
        if keys[pygame.K_d]:
            vector.x = 1

        return vector

class Red(Creature):
    def __init__(self, position):
        super().__init__(position, 200, 'red')

    def moveDirection(self):
        nearestDist = 2000.0
        nearestCreature = None
        for organism in organisms:
            if isinstance(organism, Blue):
                r,angle = self.bearing(organism)
                if r < nearestDist:
                    nearestDist = r
                    nearestCreature = organism

        if nearestCreature:
            return nearestCreature.position - self.position
        else:
            return pygame.Vector2( )

    def hit(self, blocker):
        if isinstance(blocker, Blue):
            # Add attack effect particles
            for _ in range(8):
                offset = pygame.Vector2(
                    random.uniform(-8, 8),
                    random.uniform(-8, 8)
                )
                velocity = offset * 40
                red_color = pygame.Color(200, 0, 0, 180)
                add_particle(blocker.position + offset, velocity, red_color,
                           lifetime=0.3, size=4)
            blocker.getBitten()

def getHeight( ):     return field.get_height( )
def getWidth( ):     return field.get_width( )
def getOrganisms( ):     return organisms
def getField( ):     return field
def setOrganisms(o):
     global organisms
     organisms = o
def setField(f):
     global field
     field = f