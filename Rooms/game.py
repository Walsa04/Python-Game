"""
Welcome to the Maze Mage Game. this is the code initialazing the whole
game
"""

import sys
import pygame
import random
pygame.init()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

BOUNDS_X = (60, 1140)
BOUNDS_Y = (60, 660)

WINDOW_SIZE = (1200, 720)
WINDOW_TITLE = "GAME"

PLAYER_SIZE = ENEMY_SIZE = PARTICLES_SIZE = (72, 72)
BULLET_SIZE = (48, 48)

PARTICLES = pygame.image.load("particles.png")
ENEMY_MAX_HEALTH = 5

clock = pygame.time.Clock()
DMG = 1
REGEN_TIME = 4000
last_regen1 = last_regen2 = pygame.time.get_ticks()

RECOIL_VALUE = 300
CURSOR_MIN_SIZE = 50
CURSOR_INCREASE_EFFECT = 25
CURSOR_SHRINK_SPEED = 3
CURSOR = pygame.image.load("cursor.png")
BULLET = pygame.image.load("fireball.png")
HEART_FULL = "heart.png"
HEART_EMPTY = "heart_empty.png"
MANA_FULL = "mana.png"
MANA_EMPTY = "mana_empty.png"
BULLET_SPEED = 5
LEFTRIGHT = 1
UP = 2
DOWN = 0
FRAME_RATE = 60
ANIMATION_FRAME_RATE = 10
WINDOW = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(WINDOW_TITLE)

CLOCK = pygame.time.Clock()

FONT = pygame.font.Font(None, 36)
MAX_HEALTH = 5
MAX_MANA = 5
background = pygame.image.load("11.png")

currentroom = 40
BOSS = 44
ENEMIES_STATIC = [0, 13, 21, 31, 35, 36, 44, 50, 56, 66, 70]
bossdefeated = False

BUFFS = [8, 28, 32, 57, 73]
bullets = []
particles = []
enemies = []
objects = []
tutorial_phaze = ["tut2.png", "tut1.png"]
chests = []

rooms = ["11.png", "21.png", "31.png", "21.png", "51.png", "61.png",
         "71.png", "21.png", "51.png",
         "71.png", "12.png", "61.png", "42.png", "31.png", "62.png",
         "12.png", "82.png", "61.png",
         "82.png", "11.png", "62.png", "51.png", "11.png", "62.png",
         "31.png", "62.png", "72.png",
         "88.png", "51.png", "88.png", "21.png", "21.png", "64.png",
         "74.png", "84.png", "84.png",
         "82.png", "11.png", "12.png", "82.png", "start.png", "61.png",
         "84.png", "71.png", "end.png",
         "82.png", "61.png", "71.png", "64.png", "31.png", "72.png",
         "61.png", "82.png", "61.png",
         "88.png", "72.png", "84.png", "11.png", "21.png", "12.png",
         "42.png", "62.png", "12.png",
         "84.png", "88.png", "21.png", "74.png", "84.png", "61.png",
         "71.png", "72.png", "61.png",
         "11.png", "12.png", "84.png", "42.png", "31.png", "64.png",
         "64.png", "64.png", "12.png",
         "theend.png"]

player_input = {"left": False, "right": False, "up": False,
                "down": False}


class Object:
    """
    This is the basic class of object with:
    -coordinates
    -image
    -speed
    """
    def __init__(self, x, y, width, height, image, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.velocity = [0, 0]
        self.speed = speed
        self.collider = [width, height]

        objects.append(self)

    def draw(self):
        WINDOW.blit(pygame.transform.scale(self.image,
                    (self.width, self.height)), (self.x, self.y))

    def update(self):
        """
        This function enable moving by checking if there was any move
        """
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.draw()

    def get_center(self):
        return self.x + self.width / 2, self.y + self.height / 2


class Entity(Object):
    """
    This is the upgraded class of object, that can be animated, addet features:
    -animation
    """
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.speed = speed
        self.tileset = load_tileset(tileset, 16, 16)
        self.direction = 0
        self.flipX = False
        self.frame = 0
        self.frames = [0, 1, 0, 2]
        self.frame_timer = 0

    def change_direction(self):
        """
        This function changes direction of
        """
        if self.velocity[0] < 0:
            self.direction = LEFTRIGHT
            self.flipX = True
        elif self.velocity[0] > 0:
            self.direction = LEFTRIGHT
            self.flipX = False
        elif self.velocity[1] < 0:
            self.direction = UP
        elif self.velocity[1] > 0:
            self.direction = DOWN

    def draw(self):
        """
        This is upgraded function of drawing object
        """
        image = pygame.transform.scale(self.tileset[self.frames
                                       [self.frame]][self.direction],
                                       (self.width, self.height))
        self.change_direction()
        image = pygame.transform.flip(image, self.flipX, False)
        WINDOW.blit(image, (self.x, self.y))

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.frame = 0
            return

        self.frame_timer += 1

        if self.frame_timer < ANIMATION_FRAME_RATE:
            return

        self.frame += 1
        if self.frame >= len(self.frames):
            self.frame = 0

        self.frame_timer = 0

    def update(self):
        self.x += self.velocity[0] * self.speed
        self.y += self.velocity[1] * self.speed
        self.draw()


class Player(Entity):
    """
    This is a player class with unique statistic:
    -mana
    """
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.health = self.max_health = MAX_HEALTH
        self.mana = self.max_mana = MAX_MANA

    def get_center(self):
        return self.x + self.width / 2, self.y + self.height / 2


class Enemy(Entity):
    """
    This is a player class with unique statistic:
    -growing
    -collisions
    """

    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        enemies.append(self)
        self.m_width = width
        self.m_height = height
        self.width = 0
        self.height = 0
        self.grow_speed = 2

        self.collider = [width, height]
        self.health = ENEMY_MAX_HEALTH

    def update(self):
        """
        This function makes this class move to a player
        """
        if self.width < self.m_width:
            self.width += self.grow_speed
        if self.height < self.m_height:
            self.height += self.grow_speed

        player_center = player.get_center()
        self.velocity = [player_center[0] - self.x, player_center[1] - self.y]
        length = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.velocity = [self.velocity[0] / length, self.velocity[1] / length]
        self.velocity = [self.velocity[0] * self.speed,
                         self.velocity[1] * self.speed]

        super().update()

    def change_direction(self):
        """
        This function has improved changing direction
        """
        if self.velocity[0] < 0:
            self.direction = LEFTRIGHT
            self.flipX = True
        elif self.velocity[0] > 0:
            self.direction = LEFTRIGHT
            self.flipX = False

        if self.velocity[1] > self.velocity[0] > 0:
            self.direction = DOWN
        elif self.velocity[1] < self.velocity[0] < 0:
            self.direction = UP

    def take_damage(self, damage):
        """
        This function enables to check health of enemy
        """
        self.health -= damage
        if currentroom != BOSS:
            if self.health > 0:
                return
            if self.health <= 0:
                self.destroy()
        if currentroom == BOSS:
            if self.health > 0:
                return
            if self.health <= 0:
                global bossdefeated
                bossdefeated = True
                self.destroy()

    def destroy(self):
        """
        This function ackowlege that enemy was defeated
        """
        objects.remove(self)
        enemies.remove(self)
        spawn_particles(self.x, self.y)
        ENEMIES.remove(currentroom)

    def remove(self):
        """
        This function makes enemy disappear when player changes room
        """
        objects.remove(self)
        enemies.remove(self)


def load_tileset(filename, width, height):
    """
    This function enables animation by dividing image into 9 parts
    """
    image = pygame.image.load(filename).convert_alpha()
    image_width, image_height = image.get_size()
    tileset = []
    for tile_x in range(0, image_width // width):
        line = []
        tileset.append(line)
        for tile_y in range(0, image_height // height):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tileset


def render_text(text, color, position):
    """
    This function renders simple text
    """
    rendered_text = FONT.render(text, True, color)
    WINDOW.blit(rendered_text, position)


def input(key, value):
    """
    This function controls "WSAD" keys
    """
    if key == pygame.K_w:
        player_input["up"] = value
    elif key == pygame.K_s:
        player_input["down"] = value
    elif key == pygame.K_a:
        player_input["left"] = value
    elif key == pygame.K_d:
        player_input["right"] = value


def check_collisions(obj1, obj2):
    """
    This function checks collisions
    """
    if obj1.x + obj1.collider[0] > obj2.x and \
       obj1.x < obj2.x + obj2.collider[0]:
        return obj1.y + obj1.collider[1] > obj2.y and \
               obj1.y < obj2.y + obj2.collider[1]
    return False


def shoot():
    """
    This function summon firebal that can damage enemies and removes
    player's mana
    """
    if player.mana > 0:
        player_center = player.get_center()
        bullet = Entity(player_center[0], player_center[1],
                        BULLET_SIZE[0], BULLET_SIZE[1], "fireball.png",
                        BULLET_SPEED)
        bullet.velocity = [target.x - bullet.x, target.y - bullet.y]

        length = (bullet.velocity[0] ** 2 +
                  bullet.velocity[1] ** 2) ** 0.5

        bullet.velocity = [bullet.velocity[0] /
                           length, bullet.velocity[1] / length]
        bullet.velocity = [bullet.velocity[0] *
                           BULLET_SPEED, bullet.velocity[1] *
                           BULLET_SPEED]

        bullets.append(bullet)

        target.width += CURSOR_INCREASE_EFFECT
        target.height += CURSOR_INCREASE_EFFECT

        player.mana -= 1


def spawn():
    """
    This function spawns the enemy
    """
    if currentroom in ENEMIES:
        if len(enemies) == 0 and len(particles) == 0:
            enemy = Enemy(random.randint(BOUNDS_X[0], BOUNDS_X[1]),
                          random.randint(BOUNDS_Y[0], BOUNDS_Y[1]),
                          100, 100, "enemy.png", 1)


def boss_spawn():
    """
    This function spawns the boss of the dungeon
    """
    if currentroom == BOSS and bossdefeated is False:
        if len(enemies) == 0 and len(particles) == 0:
            enemy = Enemy(100, 100, 100, 100, "boss.png", 2)
            enemy.health = enemy.max_health = 5 * ENEMY_MAX_HEALTH


def spawn_particles(x, y):
    """
    This function spawns particles representing corps
    """
    particle = Object(x, y, PARTICLES_SIZE[0], PARTICLES_SIZE[1],
                      PARTICLES, 0)
    particles.append(particle)
    objects.append(particle)


def display_stats():
    """
    This function show player's mana and health
    """
    for i in range(player.max_health):
        img = pygame.image.load(HEART_EMPTY if i >=
                                player.health else HEART_FULL)
        img = pygame.transform.scale(img, (50, 50))
        WINDOW.blit(img, (i * 50 + WINDOW_SIZE[0] - WINDOW_SIZE[0] / 9
                    - player.max_health * 25, 5))

    for i in range(player.max_mana):
        img = pygame.image.load(MANA_EMPTY if i >= player.mana else MANA_FULL)
        img = pygame.transform.scale(img, (50, 50))
        WINDOW.blit(img, (i * 50 + WINDOW_SIZE[0] / 9 -
                          player.max_health * 25, 5))


def recoil():
    """
    This function makes player move if he was damaged by enemy
    """
    if player.x > BOUNDS_X[1] - RECOIL_VALUE:
        player.x -= RECOIL_VALUE
    elif player.x < RECOIL_VALUE:
        player.x += RECOIL_VALUE
    else:
        roll = random.randint(1, 2)
        if roll == 1:
            player.x -= RECOIL_VALUE
        else:
            player.x += RECOIL_VALUE

    if player.y > BOUNDS_Y[1] - RECOIL_VALUE:
        player.y -= RECOIL_VALUE
    elif player.y < RECOIL_VALUE:
        player.y += RECOIL_VALUE
    else:
        roll = random.randint(1, 2)
        if roll == 1:
            player.y -= RECOIL_VALUE
        else:
            player.y += RECOIL_VALUE


def game():
    """
    This is the Main game function
    """
    global last_regen1, last_regen2, currentroom, ENEMIES, buffs
    global player, target
    player = Player(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2,
                    75, 75, "player.png", 10)
    target = Object(100, 100, CURSOR_MIN_SIZE,
                    CURSOR_MIN_SIZE, CURSOR, 10)
    main_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 300, 200, 50)
    currentroom = 40
    ENEMIES = ENEMIES_STATIC
    DMG = 1
    buffs = BUFFS
    player.health = MAX_HEALTH
    player.mana = MAX_MANA
    while True:
        current_time1 = pygame.time.get_ticks()
        current_time2 = pygame.time.get_ticks()
        if player.mana < player.max_mana:
            if current_time1 - last_regen1 >= REGEN_TIME:
                player.mana += 1
                last_regen1 = current_time1
        else:
            last_regen1 = current_time1

        if player.health < player.max_health:
            if current_time2 - last_regen2 >= REGEN_TIME:
                player.health += 1
                last_regen2 = current_time2
        else:
            last_regen2 = current_time2

        fps = CLOCK.get_fps()
        WINDOW.blit(pygame.image.load(rooms[currentroom]), (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    pause_menu()
                input(event.key, True)
            elif event.type == pygame.KEYUP:
                input(event.key, False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                shoot()

        if target.width > CURSOR_MIN_SIZE:
            target.width -= CURSOR_SHRINK_SPEED
        if target.height > CURSOR_MIN_SIZE:
            target.height -= CURSOR_SHRINK_SPEED

        for e in enemies:
            if (currentroom in ENEMIES) is False:
                e.remove()
            if check_collisions(e, player):
                player.health -= 1
                recoil()
            for b in bullets:
                if check_collisions(e, b):
                    e.take_damage(DMG)
                    bullets.remove(b)
                    objects.remove(b)

        if player.health == 0:
            fail()

        mousepos = pygame.mouse.get_pos()
        target.x = mousepos[0] - target.width / 2
        target.y = mousepos[1] - target.height / 2
        player.velocity[0] = player_input["right"] - player_input["left"]
        player.velocity[1] = player_input["down"] - player_input["up"]

        if WINDOW.get_at((int(player.x),
                          int(player.y))) == (127, 127, 127, 255) or \
           WINDOW.get_at((int(player.x) + player.width,
                          int(player.y) + player.height)) \
           == (127, 127, 127, 255):

            player.x = max(BOUNDS_X[0], min(player.x, BOUNDS_X[1]
                           - player.width))
            player.y = max(BOUNDS_Y[0], min(player.y, BOUNDS_Y[1]
                           - player.height))

        if currentroom != BOSS:
            if player.y <= 10:
                currentroom -= 9
                player.y = 570
            if player.y >= WINDOW_SIZE[1] - 85:
                currentroom += 9
                player.y = 70
            if player.x <= 10:
                currentroom -= 1
                player.x = 1100
            if player.x >= WINDOW_SIZE[0] - 85:
                currentroom += 1
                player.x = 80
            if currentroom in ENEMIES and currentroom != BOSS:
                spawn()
            if currentroom in buffs:
                buffs.remove(currentroom)
                chest = Object(50, 50, 100, 100,
                               pygame.image.load("chest.png"), 0)
                chests.append(chest)

        else:
            boss_spawn()
            if bossdefeated is False:
                player.x = max(BOUNDS_X[0],
                               min(player.x, BOUNDS_X[1] - player.width))
                player.y = max(BOUNDS_Y[0],
                               min(player.y, BOUNDS_Y[1] - player.height))
            if player.x <= 10:
                currentroom -= 1
                player.x = 1100
            if bossdefeated is True:
                if WINDOW.get_at((int(player.x), int(player.y))) \
                 == (127, 127, 127, 255) \
                 or WINDOW.get_at((int(player.x) + player.width,
                                  int(player.y) + player.height)) \
                 == (127, 127, 127, 255):

                    player.x = max(BOUNDS_X[0], min(player.x,
                                                    BOUNDS_X[1] -
                                                    player.width))
                    player.y = max(BOUNDS_Y[0], min(player.y,
                                                    BOUNDS_Y[1] -
                                                    player.height))
                if player.x >= WINDOW_SIZE[0] - 100:
                    currentroom += 37

        for b in bullets:
            if BOUNDS_X[0] <= b.x <= BOUNDS_X[1] and \
             BOUNDS_Y[0] <= b.y <= BOUNDS_Y[1]:
                continue
            bullets.remove(b)
            objects.remove(b)

        for p in particles:
            if p.image.get_alpha() > 0:
                p.image.set_alpha(p.image.get_alpha() - 5)
                if p.image.get_alpha() <= 0:
                    objects.remove(p)
                    particles.remove(p)
            else:
                p.image.set_alpha(100)

        for obj in objects:
            obj.update()

        for c in chests:
            if player.x <= 150 and player.y <= 150:
                DMG *= 2
                chests.remove(c)
                objects.remove(c)

        if currentroom == 81:
            player.x = max(BOUNDS_X[0], min(player.x, BOUNDS_X[1]
                                            - player.width))
            player.y = max(BOUNDS_Y[0], min(player.y, BOUNDS_Y[1]
                                            - player.height))
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        main_menu()

        display_stats()
        render_text(f"FPS: {int(fps)}", (0, 0, 0), (10, WINDOW_SIZE[1] - 40))
        CLOCK.tick(FRAME_RATE)
        pygame.display.update()


def draw_text(text, color, x, y, size=1):
    """
    This function Draws more complex text
    """
    font_size = int(36 * size)
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    WINDOW.blit(text_surface, text_rect)


def main_menu():
    """
    This is main Menu function
    """
    pygame.mouse.set_visible(True)
    start_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 200, 200, 50)
    quit_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 300, 200, 50)
    tutor_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 400, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    game()
                    return
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif tutor_rect.collidepoint(event.pos):
                    tutorial()

        WINDOW.blit(pygame.image.load(rooms[currentroom]), (0, 0))
        draw_text("Main Menu", BLACK, WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 6)

        if start_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, start_rect, 2)
            draw_text("Start", BLACK, WINDOW_SIZE[0]/2, 225, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, start_rect, 2)
            draw_text("Start", BLACK, WINDOW_SIZE[0]/2, 225)

        if quit_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, quit_rect, 2)
            draw_text("Quit", BLACK, WINDOW_SIZE[0]/2, 325, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, quit_rect, 2)

            draw_text("Quit", BLACK, WINDOW_SIZE[0]/2, 325)

        if tutor_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, tutor_rect, 2)
            draw_text("Tutorial", BLACK, WINDOW_SIZE[0]/2, 425, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, tutor_rect, 2)
            draw_text("Tutorial", BLACK, WINDOW_SIZE[0]/2, 425)

        pygame.display.flip()


def pause_menu():
    """
    This is pause function
    """
    pygame.mouse.set_visible(True)
    resume_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 200, 200, 50)
    quit_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 400, 200, 50)
    main_rect = pygame.Rect(WINDOW_SIZE[0]/2 - 100, 300, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if resume_rect.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    return
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif main_rect.collidepoint(event.pos):
                    main_menu()

        WINDOW.blit(pygame.image.load(rooms[currentroom]), (0, 0))
        draw_text("Pause Menu", BLACK, WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 6)

        if resume_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, resume_rect, 2)
            draw_text("Resume", BLACK, WINDOW_SIZE[0] / 2, 225, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, resume_rect, 2)
            draw_text("Resume", BLACK, WINDOW_SIZE[0] / 2, 225)

        if main_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, main_rect, 2)
            draw_text("Main Menu", BLACK, WINDOW_SIZE[0] / 2, 325, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, main_rect, 2)
            draw_text("Main Menu", BLACK, WINDOW_SIZE[0] / 2, 325)

        if quit_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WINDOW, BLACK, quit_rect, 2)
            draw_text("Quit", BLACK, WINDOW_SIZE[0] // 2, 425, size=1.2)
        else:
            pygame.draw.rect(WINDOW, BLACK, quit_rect, 2)
            draw_text("Quit", BLACK, WINDOW_SIZE[0] // 2, 425)

        pygame.display.flip()


def tutorial():
    """
    This is tutorial function
    """
    tut = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if tut == len(tutorial_phaze) - 1:
                        main_menu()
                        tut = 0
                    else:
                        tut += 1

        WINDOW.blit(pygame.image.load(tutorial_phaze[tut]), (0, 0))
        pygame.display.flip()


def fail():
    """
    This function appears when player dies
    """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main_menu()

        WINDOW.blit(pygame.image.load("fail.png"), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main_menu()
