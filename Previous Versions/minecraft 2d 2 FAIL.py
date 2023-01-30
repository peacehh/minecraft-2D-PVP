#setup
import pygame, sys, os
pygame.init()
pygame.font.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    instancelist = []
    def __init__(self, path, midbottom, scale = 0):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        width = self.image.get_width()
        height = self.image.get_height()
        if scale != 0: self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.path = path
        self.rect = self.image.get_rect(midbottom = midbottom)
        self.vel = 0
        self.air_time = 0
        self.in_air = False
        Player.instancelist.append(self)


    def update_in_air(self, space = False):
        #update in air
        self_lower = Player(self.path, (self.rect.x, self.rect.bottom +1), 1)
        player_group.add(self_lower)
        self.in_air = self_lower.rect.bottom > 500 or len(pygame.sprite.spritecollide(self_lower, block_group, False)) > 0
        player_group.remove(self_lower)

        print(self.air_time)
        if self.in_air and self.air_time > 0:
            self.update_y()
        elif space and not self.in_air:
            time = 0
            self.vel = 15
            self.update_y()
        elif not self.in_air and self.air_time == 0:
            self.vel == 0
            self.update_y()

        while self.checkTouching():
            self.rect.bottom -= 1
            self.vel = 0

    def checkTouching(self):
        return self.rect.bottom > 500 or len(pygame.sprite.spritecollide(self, block_group, False)) > 0

    def startJump(self):
        if self.in_air:
            self.air_time = 0
            self.vel = 15

    def startFall(self):
        self.air_time = 0
        self.vel = 0

    def update_y(self):
        self.air_time += 1
        self.vel -= g * self.air_time
        self.rect.y -= self.vel
        #stop jump


    def moveleft(self):
        self.rect.x -= 5

    def moveright(self):
        self.rect.x += 5

class Block(pygame.sprite.Sprite):
    def __init__(self, path, midbottom, scale = 0):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        width = self.image.get_width()
        height = self.image.get_height()
        if scale != 0: self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(midbottom = midbottom)

#settings
g = .15
WIDTH, HEIGHT= 1000, 500
SIZE = (WIDTH, HEIGHT)
BGCOLOR = '#a3bce6'
PLAYER_MOVED = pygame.USEREVENT + 1

#screen
screen = pygame.display.set_mode(SIZE)
screen_rect = screen.get_rect()

#background
background_surf = pygame.Surface(SIZE)
background_surf.fill(BGCOLOR)
background_rect = background_surf.get_rect()

#Player sprites
player_blue = Player(os.path.join('minecraftAssets', 'steve_front.png'), (200, 500), 1)
player_pink = Player(os.path.join('minecraftAssets', 'steve_front.png'), (800, 500), 1)
# Player group
player_group = pygame.sprite.Group()
player_group.add(player_blue, player_pink)

#Block sprites
grass_block = Block(os.path.join('minecraftAssets', 'grass.png'), (500, 500), 1)
#Block group
block_group = pygame.sprite.Group()
block_group.add(grass_block)

while True:
    keys_pressed = pygame.key.get_pressed()
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player_blue.update_in_air(space = True)
            if event.key == pygame.K_o:
                player_pink.update_in_air(space = True)

        if event.type == PLAYER_MOVED:
            pass

    if keys_pressed[pygame.K_d]:
        player_blue.moveright()
    if keys_pressed[pygame.K_a]:
        player_blue.moveleft()

    if keys_pressed[pygame.K_SEMICOLON]:
        player_pink.moveright()
    if keys_pressed[pygame.K_k]:
        player_pink.moveleft()

    player_blue.update_in_air()
    player_pink.update_in_air()


    screen.blit(background_surf, background_rect)
    player_group.draw(screen)
    block_group.draw(screen)
    pygame.display.update()
