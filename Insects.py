from operator import attrgetter
from functools import reduce
from Flatworld import *

enableDraw = True

class Flower(Grass):
    def __init__(self, nest, position):
        super().__init__(position)
        self.nest = nest

    def draw(self, position):
        if enableDraw:
                super().draw(position)

    def getBitten(self):
        if self.leaves > 0:
            self.leaves -= 1
            if self.leaves <= 0:
                getOrganisms( ).remove(self)
                self.nest.replaceIndividual(self)

class Nest(object):
    def __init__(self, position, population=10):
        self.position = position
        self.score = 0
        self.individuals = [ \
            self.spawn(self.getPosition(position, i))
                            for i in range(population)]

    def getMembers(self):
        return self.individuals

    def incrementScore(self):
        self.score += 1
        
    def getScore(self):
        return self.score

    def replaceIndividual(self, thing):
        if thing in self.individuals:
            i = self.individuals.index(thing)
            position = self.getPosition(self.position, i)
            if position != None:
                self.individuals[i] = self.spawn(position)
                getOrganisms().append(self.individuals[i])

    def tick(self, secondsSinceLastFrame):
        pass

    def spawn(self, position):
        raise(NotImplementedError)
        
    def getPosition(self, center, index):
        return center

class Meadow(Nest):
    def __init__(self, position):
        super().__init__(position, 10)
        
    def getPosition(self, center, index):
        x = int(center.x)
        y = int(center.y)
        for i in range(100):
            position =  pygame.Vector2(
                                    random.randint(x - 50, x + 50),
                                    random.randint(y - 50, y + 50))
            if anyCollision(position) == None:
                return position
        return None

    def spawn(self, position):
        return Flower(self, position)

class BeeHive(Nest):
    def __init__(self, position, index, chromosome = None):
        self.speed = 500
        self.chromosome = Chromosome(chromosome)
        self.index = index
        super().__init__(position, 10)

    def spawn(self, position):
        return Bee(self, position, self.speed, self.getColor( ))

    def getColor(self):
        colors = ['gray20', 'sienna', 'lightcoral', 'tan',
                      'lightgoldenrod1', 'darkolivegreen2',
                      'deepskyblue', 'magenta3', 'gray80']
        return pygame.Color(colors[self.index])

    def tick(self, secondsSinceLastFrame):
        self.draw(self.position)

    def draw(self, position):
        if enableDraw:
            pygame.draw.circle(getField( ), self.getColor( ),
                                        position, 20, width = 3)

    def getFoodLocation(self):
        dancing = filter(lambda x: x.isDancing( ),
                                    self.individuals)

        locations = list(map(attrgetter('foodLocation'),
                                    dancing))

        return random.choice(locations) \
                                      if len(locations) > 0 else None

class Insect(Organism):
    def __init__(self, nest, position, speed, color):
        super().__init__(position)
        self.nest = nest
        self.nestLocation = position
        self.speed = speed
        self.direction = pygame.Vector2()
        self.color = color
        self.size = 10

    def draw(self, position):
        if enableDraw:
            from Flatworld import draw_triangle_shadow
            
            v = self.direction if self.direction.length() > 0.1 \
                                        else pygame.Vector2([1,0])

            p1 = pygame.Vector2(v)
            p2 = pygame.Vector2(v)
            p3 = pygame.Vector2(v)
            p2 = p2.rotate(135)
            p3 = p3.rotate(-135)

            p1.scale_to_length(self.size)
            p2.scale_to_length(self.size)
            p3.scale_to_length(self.size)
            p1 += position
            p2 += position
            p3 += position
            
            triangle_points = [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)]
            
            # Draw triangular shadow first (offset down-right)
            draw_triangle_shadow(getField(), triangle_points, shadow_offset=(5, 6))
            
            # Draw extruded 3D triangular prism
            if isinstance(self.color, str):
                base_color = pygame.Color(self.color)
            else:
                base_color = pygame.Color(self.color)
            
            light_color = pygame.Color(
                min(255, base_color.r + 50),
                min(255, base_color.g + 50),
                min(255, base_color.b + 50)
            )
            dark_color = pygame.Color(
                max(0, base_color.r - 80),
                max(0, base_color.g - 80),
                max(0, base_color.b - 80)
            )
            side_color = pygame.Color(
                max(0, base_color.r - 60),
                max(0, base_color.g - 60),
                max(0, base_color.b - 60)
            )
            
            shadow_offset = (5, 6)
            
            # Draw three side faces of the prism (connecting top to bottom)
            bottom_p1 = (p1.x + shadow_offset[0], p1.y + shadow_offset[1])
            bottom_p2 = (p2.x + shadow_offset[0], p2.y + shadow_offset[1])
            bottom_p3 = (p3.x + shadow_offset[0], p3.y + shadow_offset[1])
            
            # Side face 1 (p1 to p2)
            pygame.draw.polygon(getField(), side_color, [
                (p1.x, p1.y), (p2.x, p2.y), bottom_p2, bottom_p1
            ])
            
            # Side face 2 (p2 to p3)
            pygame.draw.polygon(getField(), side_color, [
                (p2.x, p2.y), (p3.x, p3.y), bottom_p3, bottom_p2
            ])
            
            # Side face 3 (p3 to p1) - might be less visible
            pygame.draw.polygon(getField(), dark_color, [
                (p3.x, p3.y), (p1.x, p1.y), bottom_p1, bottom_p3
            ])
            
            # Draw top triangle (brighter, main visible face) - drawn last so it's on top
            # Add highlight on upper-left vertex
            highlight_points = [
                (p1.x - 2, p1.y - 2),  # Slightly offset for highlight
                (p2.x, p2.y),
                (p3.x, p3.y)
            ]
            pygame.draw.polygon(getField(), base_color, [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)])
            
            # Add edge lines for definition
            pygame.draw.polygon(getField(), dark_color, [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)], 1)

    def moveTo(self, newPosition):
        if newPosition.x < 0:
            newPosition.x = 0

        if newPosition.x >= getWidth():
            newPosition.x = getWidth() - 1

        if newPosition.y < 0:
            newPosition.y = 0

        if newPosition.y >= getHeight():
            newPosition.y = getHeight() - 1

        organism = anyCollision(newPosition,
                                           ignore=self,
                                           ignoreType=Insect)

        if organism != None:
            return organism
        else:   
            self.position = newPosition
            return None

    def tick(self, secondsSinceLastFrame):
        self.direction = self.moveDirection()
        if self.direction.length() > 0.1:
            # Add particle trail for insects
            from Flatworld import add_particle
            import random
            if not hasattr(self, 'last_position'):
                self.last_position = pygame.Vector2(self.position)
            
            movement = (self.position - self.last_position).length()
            if movement > 1:
                trail_color = pygame.Color(self.color)
                trail_color.a = 80
                for _ in range(1):
                    offset = pygame.Vector2(
                        random.uniform(-2, 2),
                        random.uniform(-2, 2)
                    )
                    dir_normalized = self.direction.normalize() if self.direction.length() > 0.1 else pygame.Vector2()
                    velocity = -dir_normalized * 40 + offset * 15
                    add_particle(self.position + offset, velocity, trail_color,
                               lifetime=0.25, size=2)
            
            self.direction.scale_to_length(self.speed *
                                                secondsSinceLastFrame)

        newPosition = self.position + self.direction
        blocker = self.moveTo(newPosition)
        if blocker != None:
            self.hit(blocker)
        
        self.last_position = pygame.Vector2(self.position)
        super().tick(secondsSinceLastFrame)

    def hit(self, blocker):
        pass
    
    def moveDirection(self):
                raise(NotImplementedError)

class Chromosome:
    def __init__(self, chromosome=None):
        self.gene=[0]*5
        if chromosome == None:
            for i in range(5):
                self.gene[i] = random.randint(10, 100)*1.0
        else:
            self.gene = list(chromosome.gene)

    def exhaustionPeriod(self): return self.gene[0] * 7
    def restPeriod(self): return self.gene[1] * 2
    def fidgetChance(self): return self.gene[2]
    def concentrateTarget(self): return self.gene[3]
    def concentrateHome(self): return self.gene[4]

    def mutate(self):
        x = random.randint(0,4)
        self.gene[x] = max(5.0, min(100.0,
                self.gene[x] * random.randint(70, 130) / 100.0))
        return self

    def mate(self, other):
        child = Chromosome( )
        for i in range(len(self.gene)):
            child.gene[i] = random.choice(
                                           [self.gene[i], other.gene[i]])
        return child

    def __str__(self):
        s = '<'
        for i in range(5):
            s = s + '{0}:{1:5.1f}'.format(
                                ['Ep', 'Rp', 'F%', 'T%', 'H%'][i],
                                self.gene[i]) + ' '
        s = s[:-1] + '>'
        return s

def vectorTo(position, target):
    return position - target

def distanceFrom(position, target):
    return (position - target).length()

class Bee(Insect):
    def __init__(self, nest, position, speed, color):
        super().__init__(nest, position, 500, color)
        self.carryingFood = False
        self.goingHome = False
        self.foodLocation = None
        self.targetLocation = None
        self.awayFromHomeCounter = 0
        self.atHomeCounter = 0

    def hit(self, blocker):
        if isinstance(blocker, Grass):
            if not self.carryingFood:
                blocker.getBitten( )
                self.carryingFood = True
                self.goingHome = True
                self.foodLocation = self.position
                self.atHomeCounter = \
                   self.nest.chromosome.restPeriod( )

    def isHome(self):
        return distanceFrom(self.position,
                                    self.nestLocation) < 10

    def isDancing(self):
        return self.isHome( ) and self.foodLocation != None

    def moveDirection(self):
        self.awayFromHomeCounter += 1
        if self.goingHome:
            if self.isHome( ):
                if self.atHomeCounter > 0:
                    self.atHomeCounter -= 1
                    return pygame.Vector2( )

                else:
                    self.atHomeCounter = \
                                  self.nest.chromosome.restPeriod( )
                    self.awayFromHomeCounter = 0
                    self.goingHome = False
                    if self.carryingFood:
                        self.carryingFood = False
                        self.nest.incrementScore( )
                        self.targetLocation = \
                                           self.nest.getFoodLocation( )
                        self.foodLocation = None

        else:
            if self.targetLocation != None and \
                    distanceFrom(self.position,
                                       self.targetLocation) < 10:
                self.targetLocation = None

        if self.awayFromHomeCounter > \
           self.nest.chromosome.exhaustionPeriod( ):

            self.goingHome = True

        if random.randint(0, 100) < \
                             self.nest.chromosome.fidgetChance( ):

           if self.goingHome and random.randint(0, 100) < \
                    self.nest.chromosome.concentrateHome( ):

                return vectorTo(self.nestLocation, self.position)

           if self.targetLocation != None and \
              random.randint(0, 100) < \
                      self.nest.chromosome.concentrateTarget( ):
                return vectorTo(self.targetLocation,
                                      self.position)

           else:
                x = random.randint(-1, 1)
                y = random.randint(-1, 1)
                self.direction = pygame.Vector2(x,y)

        return self.direction

def displayText(text, field, position):
    font = pygame.font.SysFont('arial', 24)
    surface = font.render(text, True, pygame.Color(0,0,0))
    rect = surface.get_rect().move(10,10)
    field.blit(surface, rect)

def OneRepeat(clock, chromosomes, generation):
    global organisms, nests, field, enableDraw
    field = getField()
    organisms = [ ]
    setOrganisms(organisms)
    nests = [ ]
    frameDecimation = 300

    for meadow in range(3):
        spawn = Meadow(randomDrop())
        organisms += spawn.getMembers()
        nests.append(spawn)

    i = 0
    for chromosome in chromosomes:
        spawn = BeeHive(randomDrop(), i, chromosome)
        organisms += spawn.getMembers()
        nests.append(spawn)
        i += 1

    # Default to slower mode (drawing enabled)
    enableDraw = True
    
    for tickCounter in range(5000):
        secondsSinceLastFrame  = 1/60.0
        
        # Update particles
        from Flatworld import update_particles, draw_particles, draw_background
        update_particles(secondsSinceLastFrame)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

        keys = pygame.key.get_pressed()
        # Holding spacebar = faster mode (no drawing), default = slower mode (with drawing)
        if keys[pygame.K_SPACE]:
            enableDraw = False
        else:
            enableDraw = True

        if enableDraw:
            clock.tick(15)  # Quarter speed: 15 FPS instead of 60 FPS
            # Draw background
            draw_background(field, field.get_width(), field.get_height())
            # Draw particles
            draw_particles(field)
            displayText('Generation: ' + str(generation) +
                            ' Frame: ' + str(tickCounter),
                            getField( ), pygame.Vector2(0,0))

        for organism in organisms:
            organism.tick(secondsSinceLastFrame)

        for nest in nests:
            nest.tick(secondsSinceLastFrame)

        if enableDraw:
            pygame.display.flip()

    return list(filter(lambda x: isinstance(x, BeeHive), nests))

def insectMainLoop(boardSize):
    global field

    field = pygame.display.set_mode(boardSize)
    setField(field)

    chromosomes = [Chromosome( ) for i in range(9)]

    clock = pygame.time.Clock()
    score = 0

    for generation in range(1, 1000):
        nests = OneRepeat(clock, chromosomes, generation)
        if nests == None:
            return

        print('\nGeneration', generation)
        for i in range(len(chromosomes)):
            print(chromosomes[i], 'Score:', nests[i].score)

        nests = sorted(nests,
                             key=attrgetter('score'),
                             reverse=True)

        chromosomes = [nests[0].chromosome,
                nests[1].chromosome,
                nests[2].chromosome,
                nests[0].chromosome.mate( \
                                  nests[1].chromosome).mutate( ),
                nests[0].chromosome.mate( \
                                  nests[2].chromosome).mutate( ),
                nests[1].chromosome.mate( \
                                  nests[2].chromosome).mutate( ),
                nests[0].chromosome.mate( \
                                  nests[3].chromosome).mutate( ),
                nests[1].chromosome.mate( \
                                  nests[4].chromosome).mutate( ),
                nests[2].chromosome.mate( \
                                  nests[5].chromosome).mutate( )]

if __name__ == '__main__':
    pygame.init()

    insectMainLoop(boardSize=(700,500))

    pygame.quit()
