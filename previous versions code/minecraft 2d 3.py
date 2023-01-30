#Pygame Physics
import pygame, sys, os, random
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.font.init()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
clock = pygame.time.Clock()
pygame.display.set_caption('Minecraft 2D')


class Player():
    group = []
    def __init__(self, path, scale = None, midbottom = (0, 0), main = False):
        self.surf = pygame.image.load(path).convert_alpha()
        width = self.surf.get_width()
        height = self.surf.get_height()
        if scale != None:
            self.surf = pygame.transform.scale(self.surf, (width * scale, height * scale))
        if main == True:
           Player.group.append(self)
        self.rect = self.surf.get_rect(midbottom = midbottom)
        self.vel = 0
        self.air_time = 0
        self.walk_sound_time = WALK_SOUND_DELAY
        self.animation_time = 0
        self.in_air = False
        self.left_pressed = False
        self.right_pressed = False
        self.direction_facing = 'left'
        self.up_pressed = False
        self.animation = False

    def walk_sound(self):
        if (self.right_pressed or self.left_pressed) and not self.in_air:
            if self.walk_sound_time == WALK_SOUND_DELAY:
                random.choice(SoundEffect.walk_group).sound.play()
            elif self.walk_sound_time == 0:
                self.walk_sound_time = WALK_SOUND_DELAY + 1
            self.walk_sound_time -=1

    def update_pos(self):
        lower_rect = pygame.Rect((self.rect.x, self.rect.y), (self.rect.width, self.rect.height + 1))
        for block_rect in Block.group:
            self.in_air = not lower_rect.colliderect(block_rect)
            if not self.in_air:
                break
        if self.in_air or self.vel > 0:
            self.air_time += 1
            self.move_y()
        else:
            self.air_time = 0
            self.vel = 0


    def update_surf(self):
        if self.left_pressed and self.right_pressed and not self.in_air:
            self.surf = player_front.surf
            self.animation = False
            self.animation_time = 0
        elif self.left_pressed or self.right_pressed or self.in_air:
            self.animation = True
        else:
            if self.direction_facing == 'left':
                self.surf = player_left.surf
            else:
                self.surf = player_right.surf
            self.animation = False
            self.animation_time = 0

        if self.animation:
            self.animation_time += 1
            if self.direction_facing == 'left':
                for time, surf in walk_animation_left.items():
                    if self.animation_time == time * WALKING_ANIMATION_SPEED:
                        self.surf = surf
                        break
            else:
                for time, surf in walk_animation_right.items():
                    if self.animation_time == time * WALKING_ANIMATION_SPEED:
                        self.surf = surf
                        break
            if self.animation_time == len(walk_animation_left) * WALKING_ANIMATION_SPEED:
                self.animation_time = 0

    def is_in_block(self):
        for block_rect in Block.group:
            if self.rect.colliderect(block_rect):
                return True
        if self.rect.right > WIDTH or self.rect.left < 0:
            return True

    def move_y(self):
        self.vel -= g * self.air_time
        self.rect.y -= self.vel
        landed = False
        while self.is_in_block() and self.vel < 0:
            self.rect.y -= 1
            #land sound
            landed = True
        if landed:
            random.choice(SoundEffect.land_group).sound.play()
            landed = False
        while self.is_in_block():
            self.rect.y += 1
            self.vel = 0

    def checkJump(self):
        player1.up_pressed = True
        if not self.in_air:
            self.vel = JUMP_VEL

    def moveleft(self):
        self.walk_sound()
        self.rect.x -= X_VEL
        while self.is_in_block():
            self.rect.x += 1
        self.left_pressed = True
        self.direction_facing = 'left'

    def moveright(self):
        self.walk_sound()
        self.rect.x += X_VEL
        while self.is_in_block():
            self.rect.x -= 1
        self.right_pressed = True
        self.direction_facing = 'right'


class Block():
    group = []
    def __init__(self, path):
        self.surf = pygame.image.load(path).convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (SQUARESIZE, SQUARESIZE))

    def make_rect(self, col, row):
        self.rect = self.surf.get_rect(topleft = (col * SQUARESIZE, row * SQUARESIZE))
        Block.group.append(self.rect)

class SoundEffect():
    land_group = []
    walk_group = []
    def __init__ (self, path, group):
        self.sound = pygame.mixer.Sound(path)
        if group == 'land':
            SoundEffect.land_group.append(self)
            self.sound.set_volume(LAND_SOUND_VOLUME)
        elif group == 'walk':
            SoundEffect.walk_group.append(self)
            self.sound.set_volume(WALK_SOUND_VOLUME)

def update_Player_group():
    for player in Player.group:
        player.update_pos()
        player.update_surf()

def blit_Player_group():
    for player in Player.group:
        screen.blit(player.surf, player.rect)

def blit_Block_group():
    Block.group = []
    for col in range(COLS):
        for row in range(ROWS):
            for key, block in KEYS.items():
                if world[row][col] == key:
                    block.make_rect(col, row)
                    screen.blit(block.surf, (col * SQUARESIZE, row * SQUARESIZE))

#settings
SCALE = 1.5
FPS = 30
g = 0.07 * SCALE
COLS, ROWS = 20, 10
JUMP_VEL = 9 * SCALE
X_VEL = 5 * SCALE
WIDTH, HEIGHT= 1000 * SCALE, 500 * SCALE
SIZE = (WIDTH, HEIGHT)
SQUARESIZE = 50 * SCALE
PLAYER_SIZE = 0.2 * SCALE
SKYCOLOR = '#8EC0FF'
SKYCOLOR2 = '#3151d4'
WALKING_ANIMATION_SPEED = 3
WALK_SOUND_DELAY = 15
WALK_SOUND_VOLUME = 0.1
LAND_SOUND_VOLUME = 0.2

#music
#pygame.mixer.music.load()

#screen
screen = pygame.display.set_mode(SIZE)
screen_rect = screen.get_rect()

#background
background_surf = pygame.Surface(SIZE)
background_surf.fill(SKYCOLOR)
background_rect = background_surf.get_rect()

#sounds
land_1 = SoundEffect(os.path.join('minecraftAssets', 'land_1.mp3'), 'land')
land_2 = SoundEffect(os.path.join('minecraftAssets', 'land_2.mp3'), 'land')
land_3 = SoundEffect(os.path.join('minecraftAssets', 'land_3.mp3'), 'land')
land_4 = SoundEffect(os.path.join('minecraftAssets', 'land_4.mp3'), 'land')
walk_1 = SoundEffect(os.path.join('minecraftAssets', 'walk_1.mp3'), 'walk')
walk_2 = SoundEffect(os.path.join('minecraftAssets', 'walk_2.mp3'), 'walk')
walk_3 = SoundEffect(os.path.join('minecraftAssets', 'walk_3.mp3'), 'walk')
walk_4 = SoundEffect(os.path.join('minecraftAssets', 'walk_4.mp3'), 'walk')

#block sprites
grass = Block(os.path.join('minecraftAssets', 'grass.png'))
dirt = Block(os.path.join('minecraftAssets', 'dirt.png'))
stone = Block(os.path.join('minecraftAssets', 'stone.png'))
wood = Block(os.path.join('minecraftAssets', 'wood.png'))
leaves = Block(os.path.join('minecraftAssets', 'leaves.png'))
sun = Block(os.path.join('minecraftAssets', 'sun.png'))

#player sprites
player_front = Player(os.path.join('minecraftAssets', 'steve_front.png'), PLAYER_SIZE)
player_left = Player(os.path.join('minecraftAssets', 'steve_left.png'), PLAYER_SIZE)
player_right = Player(os.path.join('minecraftAssets', 'steve_right.png'), PLAYER_SIZE)
player_walk_left_front = Player(os.path.join('minecraftAssets', 'steve_walk_left_front.png'), PLAYER_SIZE)
player_walk_left_back = Player(os.path.join('minecraftAssets', 'steve_walk_left_back.png'), PLAYER_SIZE)
player_walk_right_front = Player(os.path.join('minecraftAssets', 'steve_walk_right_front.png'), PLAYER_SIZE)
player_walk_right_back = Player(os.path.join('minecraftAssets', 'steve_walk_right_back.png'), PLAYER_SIZE)
player_walk_left_front_mid = Player(os.path.join('minecraftAssets', 'steve_walk_left_front_mid.png'), PLAYER_SIZE)
player_walk_left_back_mid = Player(os.path.join('minecraftAssets', 'steve_walk_left_back_mid.png'), PLAYER_SIZE)
player_walk_right_front_mid = Player(os.path.join('minecraftAssets', 'steve_walk_right_front_mid.png'), PLAYER_SIZE)
player_walk_right_back_mid = Player(os.path.join('minecraftAssets', 'steve_walk_right_back_mid.png'), PLAYER_SIZE)
player1 = Player(os.path.join('minecraftAssets', 'steve_left.png'), PLAYER_SIZE, (WIDTH//4, 0), main = True)
player2 = Player(os.path.join('minecraftAssets', 'steve_left.png'), PLAYER_SIZE, (WIDTH//(4/3), 0), main = True)

walk_animation_left = {
    1: player_walk_left_back_mid.surf,
    2: player_walk_left_back.surf,
    3: player_walk_left_back_mid.surf,
    4: player_left.surf,
    5: player_walk_left_front_mid.surf,
    6: player_walk_left_front.surf,
    7: player_walk_left_front_mid.surf,
    8: player_left.surf,
}

walk_animation_right = {
    1: player_walk_right_back_mid.surf,
    2: player_walk_right_back.surf,
    3: player_walk_right_back_mid.surf,
    4: player_right.surf,
    5: player_walk_right_front_mid.surf,
    6: player_walk_right_front.surf,
    7: player_walk_right_front_mid.surf,
    8: player_right.surf,
}


world = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0],
[3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
[1, 1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
[0, 0, 0, 0, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2, 1, 1, 1],
[2, 0, 0, 3, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 3],
[1, 2, 3, 3, 1, 1, 3, 3, 3, 1, 1, 3, 3, 1, 3, 3, 1, 1, 3, 3],
[1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 1, 3, 3],
]

KEYS = {1: dirt, 2: grass, 3: stone, 4: wood, 5:leaves, 6:sun}

while True:
    clock.tick(FPS)
    keys_pressed = pygame.key.get_pressed()
    update_Player_group()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #player1
    if keys_pressed[pygame.K_d]:
        player1.moveright()
    else:
        player1.right_pressed = False
    if keys_pressed[pygame.K_a]:
        player1.moveleft()
    else:
        player1.left_pressed = False
    if keys_pressed[pygame.K_w]:
        player1.checkJump()
    else:
        player1.up_pressed = False

    #player 2
    if keys_pressed[pygame.K_SEMICOLON]:
        player2.moveright()
    else:
        player2.right_pressed = False
    if keys_pressed[pygame.K_k]:
        player2.moveleft()
    else:
        player2.left_pressed = False
    if keys_pressed[pygame.K_o]:
        player2.checkJump()
    else:
        player2.up_pressed = False

    screen.blit(background_surf, background_rect)
    blit_Player_group()
    blit_Block_group()

    pygame.display.update()
