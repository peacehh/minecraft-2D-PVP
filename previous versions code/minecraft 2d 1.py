#setup
import pygame, sys, os
pygame.init()
pygame.font.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
clock = pygame.time.Clock()

class Player():
    def __init__(self, path, midbottom, scale = 0):
        self.image = pygame.image.load(path).convert_alpha()
        width = self.image.get_width()
        height = self.image.get_height()
        if scale != 0: self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(midbottom = midbottom)
        self.vel = 0
        self.air_time = 0
        self.in_air = False

    def update_in_air(self):
        lower_rect = pygame.Rect((self.rect.x, self.rect.y), (self.rect.width, self.rect.height + 1))
        self.in_air = not lower_rect.colliderect(floor_rect)
        if self.in_air or self.vel > 0:
            self.air_time += 1
            self.move_y()
        else:
            self.air_time = 0
            self.vel = 0

    def move_y(self):
        self.vel -= g * self.air_time
        self.rect.y -= self.vel
        while self.rect.colliderect(floor_rect):
            self.rect.y -= 1

    def checkJump(self):
        if not self.in_air:
            self.vel = 15

    def moveleft(self): self.rect.x -= 5

    def moveright(self): self.rect.x += 5

class Block():
    pass
#settings
g = .15
WIDTH, HEIGHT= 1000, 500
SIZE = (WIDTH, HEIGHT)
BGCOLOR = '#a3bce6'
GRASS_COLOR = '#2bb54e'
RECT_COLOR = '#4260db'
#screen
screen = pygame.display.set_mode(SIZE)
screen_rect = screen.get_rect()

#background
background_surf = pygame.Surface(SIZE)
background_surf.fill(BGCOLOR)
background_rect = background_surf.get_rect()

#floor
floor_surf = pygame.Surface((WIDTH, 100))
floor_surf.fill(GRASS_COLOR)
floor_rect = floor_surf.get_rect(bottomleft = (0, HEIGHT))

#sprites
player_blue = Player(os.path.join('minecraftAssets', 'steve_front.png'), (200, floor_rect.top - 100), 0.2)
player_pink = Player(os.path.join('minecraftAssets', 'steve_front.png'), (400, floor_rect.top), 0.2)

while True:
    keys_pressed = pygame.key.get_pressed()
    clock.tick(60)

    player_blue.update_in_air()
    player_pink.update_in_air()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player_blue.checkJump()
            if event.key == pygame.K_o:
                player_pink.checkJump()



    if keys_pressed[pygame.K_d]: player_blue.moveright()
    if keys_pressed[pygame.K_a]: player_blue.moveleft()

    if keys_pressed[pygame.K_SEMICOLON]: player_pink.moveright()
    if keys_pressed[pygame.K_k]: player_pink.moveleft()

    screen.blit(background_surf, background_rect)


    screen.blit(player_blue.image, player_blue.rect)
    screen.blit(player_pink.image, player_pink.rect)

    screen.blit(floor_surf, floor_rect)

    pygame.display.update()
