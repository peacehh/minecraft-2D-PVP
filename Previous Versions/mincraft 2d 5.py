#Pygame Physics
import pygame, sys, os, random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.font.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Minecraft 2D')


class Player():
    group = []
    def __init__(self, path = False, midbottom = (0, 0), right_key = False, left_key = False, up_key = False):
        if not path:
            self.surf = pygame.image.load(os.path.join('minecraftAssets', 'steve_front.png')).convert_alpha()
            Player.group.append(self)
        else:
            self.surf = pygame.image.load(path).convert_alpha()
        width = self.surf.get_width()
        height = self.surf.get_height()
        self.surf = pygame.transform.scale(self.surf, (width * PLAYER_SIZE, height * PLAYER_SIZE))
        self.rect = self.surf.get_rect(midbottom = midbottom)
        self.vel = 0
        self.air_time = 0
        self.animation_time = 0
        self.in_air = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.animation = False
        self.walk_sound_time = WALK_SOUND_DELAY
        self.direction_facing = 'left'
        self.right_key = right_key
        self.left_key = left_key
        self.up_key = up_key

    def get_motion(self):
        if keys_pressed[getattr(pygame , 'K_' + self.right_key)]:
            self.moveright()
        else:
            self.right_pressed = False
        if keys_pressed[getattr(pygame , 'K_' + self.left_key)]:
            self.moveleft()
        else:
            self.left_pressed = False
        if keys_pressed[getattr(pygame , 'K_' + self.up_key)]:
            self.checkJump()
        else:
            self.up_pressed = False

    def walk_sound(self):
        if (self.right_pressed or self.left_pressed) and not self.in_air:
            if self.walk_sound_time == WALK_SOUND_DELAY:
                random.choice(SoundEffect.walk_group).sound.play()
            elif self.walk_sound_time == 0:
                self.walk_sound_time = WALK_SOUND_DELAY + 1
            self.walk_sound_time -=1

    def update_pos(self):
        lower_rect = pygame.Rect((self.rect.x, self.rect.y), (self.rect.width, self.rect.height + 1))
        for block in Block.group:
            block_rect, block_surf = block
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
        for block in Block.group:
            block_rect, block_surf = block
            if self.rect.colliderect(block_rect): return True
        if self.rect.right > WIDTH or self.rect.left < 0: return True

    def move_y(self):
        self.vel -= g * self.air_time
        self.rect.y -= self.vel
        landed = False
        while self.is_in_block() and self.vel < 0:
            self.rect.y -= 1
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
    key = {}
    def __init__(self, path, key):
        self.surf = pygame.image.load(path).convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (BLOCKSIZE, BLOCKSIZE))
        Block.key.update({key:self})
    def init_map():
        for col in range(COLS):
            for row in range(ROWS):
                for key, block in Block.key.items():
                    if world[row][col] == key:
                        rect = block.surf.get_rect(topleft = (col * BLOCKSIZE, row * BLOCKSIZE))
                        Block.group.append((rect, block.surf))

def blit_Block_group():
    for block in Block.group:
        block_rect, block_surf = block
        screen.blit(block_surf, block_rect)

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

class HealthBar():
    def __init__(self, path):
        self.surf = pygame.image.load(path).convert_alpha()
        self.surf = pygame.transform.scale(self.surf, (HEARTSIZE, HEARTSIZE))
        self.rect = self.surf.get_rect(topleft = (100, 100))

def blit_Player_group():
    for player in Player.group:
        screen.blit(player.surf, player.rect)



def str_to_list(string):
    array = []
    str_list = string.split('\n')
    for line in str_list:
        char_list = [char for char in line]
        array.append(char_list)
    return array

def list_col_row(array):
    row = 0
    col = 0
    for line in array: row +=1
    for space in array[0]: col += 1
    return col, row

world_str = '''\
----------------------------------------
-------------S--------------------------
----------------------------------------
------l---------------------------gdd---
-----ll-----------s--------s----ddssds--
----llll-----s-------s-------------s----
---llwl-l---------------s---------------
--l--w-------------------d------------gg
-----w----------------------w--------gdd
gg---w----------ggg------------ggggggddd
ddgggggggggggddddddg----gggggggddddddddd
ddddddddddddddsdddd----gdddddddddddddsdd
sdddddddddddsssddd----ddddsdsdssdddddsdd
ddssssdddsssssddd----ssdssssssdddssssssd
sssissidsdsssssss-----sds--ssd----sssssi
ssssiiissssssssssss-------------------si
ssssisssssssddssssss-----------ss-----ss
sssssssssaddddsssssaaaDss---sssssaass-ss
bbbssbsssbssbbsbbbbbbdDDssssssssssssb-bs
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb-bb\
'''

world = str_to_list(world_str)

#settings
SCALE = 1
WIDTH, HEIGHT= 1600 * SCALE, 800 * SCALE
SIZE = (WIDTH, HEIGHT)
COLS, ROWS = list_col_row(world)
BLOCKSIZE = (WIDTH/COLS)
FPS = 30
g = 0.05 * SCALE**(1/2)
JUMP_VEL = 9 * SCALE
X_VEL = 4 * SCALE
PLAYER_SIZE = 0.17 * SCALE
SKYCOLOR = '#8EC0FF'
SKYCOLOR2 = '#3151d4'
WALKING_ANIMATION_SPEED = 3
WALK_SOUND_DELAY = 15
WALK_SOUND_VOLUME = 0.1
LAND_SOUND_VOLUME = 0.2
MUSIC = True
HEARTSIZE = 18 * SCALE
#screen
screen = pygame.display.set_mode(SIZE)
screen_rect = screen.get_rect()

#block sprites
grass = Block(os.path.join('minecraftAssets', 'grass.png'), 'g')
dirt = Block(os.path.join('minecraftAssets', 'dirt.png'), 'd')
stone = Block(os.path.join('minecraftAssets', 'stone.png'), 's')
wood = Block(os.path.join('minecraftAssets', 'wood.png'), 'w')
leaves = Block(os.path.join('minecraftAssets', 'leaves.png'), 'l')
sun = Block(os.path.join('minecraftAssets', 'sun.png'), 'S')
bedrock = Block(os.path.join('minecraftAssets', 'bedrock.png'), 'b')
andesite = Block(os.path.join('minecraftAssets', 'andesite.png'), 'a')
iron_ore = Block(os.path.join('minecraftAssets', 'iron_ore.png'), 'i')
diamond_ore = Block(os.path.join('minecraftAssets', 'diamond_ore.png'), 'D')

#health
health_heart = HealthBar(os.path.join('minecraftAssets', 'red_heart.png'))
health_heart_empty = HealthBar(os.path.join('minecraftAssets', 'empty_heart.png'))

#music
if MUSIC:
    pygame.mixer.music.load(os.path.join('minecraftAssets', 'minecraft_music.ogg'))
    pygame.mixer.music.set_volume(.5)
    pygame.mixer.music.play(-1)

#sounds
land_1 = SoundEffect(os.path.join('minecraftAssets', 'land_1.mp3'), 'land')
land_2 = SoundEffect(os.path.join('minecraftAssets', 'land_2.mp3'), 'land')
land_3 = SoundEffect(os.path.join('minecraftAssets', 'land_3.mp3'), 'land')
land_4 = SoundEffect(os.path.join('minecraftAssets', 'land_4.mp3'), 'land')
walk_1 = SoundEffect(os.path.join('minecraftAssets', 'walk_1.mp3'), 'walk')
walk_2 = SoundEffect(os.path.join('minecraftAssets', 'walk_2.mp3'), 'walk')
walk_3 = SoundEffect(os.path.join('minecraftAssets', 'walk_3.mp3'), 'walk')
walk_4 = SoundEffect(os.path.join('minecraftAssets', 'walk_4.mp3'), 'walk')

#player  sprites
player_front = Player(os.path.join('minecraftAssets', 'steve_front.png'))
player_left = Player(os.path.join('minecraftAssets', 'steve_left.png'))
player_right = Player(os.path.join('minecraftAssets', 'steve_right.png'))
player_walk_left_front = Player(os.path.join('minecraftAssets', 'steve_walk_left_front.png'))
player_walk_left_back = Player(os.path.join('minecraftAssets', 'steve_walk_left_back.png'))
player_walk_right_front = Player(os.path.join('minecraftAssets', 'steve_walk_right_front.png'))
player_walk_right_back = Player(os.path.join('minecraftAssets', 'steve_walk_right_back.png'))
player_walk_left_front_mid = Player(os.path.join('minecraftAssets', 'steve_walk_left_front_mid.png'))
player_walk_left_back_mid = Player(os.path.join('minecraftAssets', 'steve_walk_left_back_mid.png'))
player_walk_right_front_mid = Player(os.path.join('minecraftAssets', 'steve_walk_right_front_mid.png'))
player_walk_right_back_mid = Player(os.path.join('minecraftAssets', 'steve_walk_right_back_mid.png'))
player1 = Player(midbottom = (WIDTH * 0.2, 0), right_key = 'd', left_key = 'a', up_key = 'w')
player2 = Player(midbottom = (WIDTH * 0.4, 0), right_key = 'SEMICOLON', left_key = 'k', up_key = 'o')
player3 = Player(midbottom = (WIDTH * 0.6, 0), right_key = 'RIGHT', left_key = 'LEFT', up_key = 'UP')
player4 = Player(midbottom = (WIDTH * 0.8, 0), right_key = 'KP6', left_key = 'KP4', up_key = 'KP8')

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
Block.init_map()
while True:
    clock.tick(FPS)
    keys_pressed = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for player in Player.group:
        player.update_pos()
        player.update_surf()
        player.get_motion()

    screen.fill(SKYCOLOR)
    blit_Player_group()
    blit_Block_group()
    screen.blit(health_heart.surf, health_heart.rect)
    screen.blit(health_heart_empty.surf, health_heart_empty.rect)
    pygame.display.update()
