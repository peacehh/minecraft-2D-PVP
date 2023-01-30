#Pygame Minecraft 2d PVP
import pygame, sys, os, random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.font.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Minecraft 2D')

class Image():
    def __init__(self, path, scale = False, size = False):
        self.surf = pygame.image.load(os.path.join(*path)).convert_alpha()
        if size:
            self.surf = pygame.transform.scale(self.surf, size)
        if scale:
            self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() * scale, self.surf.get_height() * scale))

class PlayerImage():
    def __init__(self, path):
        Image.__init__(self, path, scale = PLAYER_SIZE)

class Player():
    group = []
    def __init__(self, midbottom = (0, 0), right_key = False, left_key = False, up_key = False, attack_key = False, marker_color = False):
        Image.__init__(self, ('minecraftAssets', 'steve_front.png'), scale = PLAYER_SIZE)
        self.rect = self.surf.get_rect(midbottom = midbottom)
        self.vel = 0
        self.air_time = 0
        self.animation_time = 0
        self.in_air = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.animation = False
        self.walk_sound_delay = 0
        self.right_key = right_key
        self.left_key = left_key
        self.up_key = up_key
        self.attack_key = attack_key
        self.health = HEARTS
        self.hit_cooldown = 0
        self.knockback_timer = 0
        self.direction_facing = ''
        self.knockback_direction = ''
        self.marker_color = marker_color
        self.alive = True
        Player.group.append(self)

    def update_keys_pressed(self):
        if keys_pressed[getattr(pygame , 'K_' + self.right_key)]:
            self.move_right(X_MOVE_DISTANCE)
        else:
            self.right_pressed = False
        if keys_pressed[getattr(pygame , 'K_' + self.left_key)]:
            self.move_left(X_MOVE_DISTANCE)
        else:
            self.left_pressed = False
        if keys_pressed[getattr(pygame , 'K_' + self.up_key)]:
            self.checkJump()
        else:
            self.up_pressed = False

    def check_attack(self, event):
        if event.key == getattr(pygame , 'K_' + self.attack_key):
            for player in Player.group:
                if self.rect.colliderect(player.rect) and player != self and player.hit_cooldown == 0:
                    player.hit_cooldown = HIT_COOLDOWN
                    player.vel = Y_KNOCKBACK_VELOCITY
                    random.choice(SoundEffect.attack_group).sound.play()
                    player.health -= 1
                    if player.health == 0:
                        player.alive = False
                    #knockback in x
                    player.knockback_timer = KNOCKBACK_TIME
                    if player.knockback_timer > 0:
                        if self.rect.x < player.rect.x:
                            player.knockback_direction = 'right'
                        else:
                            player.knockback_direction = 'left'

    def update_pos(self):
        lower_rect = pygame.Rect((self.rect.x, self.rect.y), (self.rect.width, self.rect.height + 1))
        for block in Block.touching_air_group:
            block_surf, block_rect = block
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
                    if self.animation_time == time * WALKING_ANIMATION_DELAY:
                        self.surf = surf
                        break
            else:
                for time, surf in walk_animation_right.items():
                    if self.animation_time == time * WALKING_ANIMATION_DELAY:
                        self.surf = surf
                        break
            if self.animation_time == len(walk_animation_left) * WALKING_ANIMATION_DELAY:
                self.animation_time = 0

    def move_y(self):
        self.vel -= g * self.air_time
        self.rect.y -= self.vel
        landed = False
        while self.is_in_block() and self.vel < 0:
            self.rect.y -= 1
            landed = True
        if landed:
            random.choice(SoundEffect.land_group).sound.play()
        while self.is_in_block():
            self.rect.y += 1
            self.vel = 0

    def checkJump(self):
        player1.up_pressed = True
        if not self.in_air:
            self.vel = JUMP_VEL

    def move_left(self, dist):
        self.walk_sound()
        self.rect.x -= dist
        while self.is_in_block():
            self.rect.x += 1
        self.left_pressed = True
        self.direction_facing = 'left'

    def move_right(self, dist):
        self.walk_sound()
        self.rect.x += dist
        while self.is_in_block():
            self.rect.x -= 1
        self.right_pressed = True
        self.direction_facing = 'right'

    def is_in_block(self):
        for block in Block.touching_air_group:
            block_surf, block_rect = block
            if self.rect.colliderect(block_rect):
                return True
        #if player is off map
        if self.rect.right > WIDTH or self.rect.left < 0:
            return True

    def walk_sound(self):
        if (self.right_pressed or self.left_pressed) and not self.in_air:
            print(self.walk_sound_delay)
            if self.walk_sound_delay == 0:
                print('sound  played')
                random.choice(SoundEffect.walk_group).sound.play()
                self.walk_sound_delay = WALK_SOUND_DELAY

    def update_timers(self):
        #walk sound timer
        if self.walk_sound_delay > 0:
            self.walk_sound_delay -= 1
        #hit_cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        #knockback timer
        if self.knockback_timer > 0:
            self.knockback_timer -= 1
            if self.knockback_direction == 'left':
                self.move_left(X_KNOCKBACK_DISTANCE)
            else:
                self.move_right(X_KNOCKBACK_DISTANCE)
class Block():
    group = []
    touching_air_group = []
    key = {}
    def __init__(self, path, key):
        Image.__init__(self, path, size = (BLOCKSIZE, BLOCKSIZE))
        Block.key.update({key:self})
        self.key = key



class SoundEffect():
    land_group = []
    walk_group = []
    attack_group = []
    def __init__ (self, path, group):
        self.sound = pygame.mixer.Sound(os.path.join(*path))
        if group == 'land':
            SoundEffect.land_group.append(self)
            self.sound.set_volume(LAND_SOUND_VOLUME)
        elif group == 'attack':
            SoundEffect.attack_group.append(self)
            self.sound.set_volume(ATTACK_SOUND_VOLUME)
        elif group == 'walk':
            SoundEffect.walk_group.append(self)
            self.sound.set_volume(WALK_SOUND_VOLUME)

class Heart():
    group = []
    def __init__(self, path):
        Image.__init__(self, path, size = (HEARTSIZE, HEARTSIZE))

class Cloud():
    move_delay = 0
    group = []
    def __init__(self, path, center):
        Image.__init__(self, path, scale = CLOUD_SIZE)
        self.rect = self.surf.get_rect(center = center)
        Cloud.group.append(self)

    def update_pos():
        if Cloud.move_delay == 0:
            for cloud in Cloud.group:
                cloud.rect.x += 1
                if cloud.rect.left > WIDTH:
                    cloud.rect.right = 0
            Cloud.move_delay = CLOUD_SPEED
        else:
            Cloud.move_delay -= 1
            
class Font:
    def __init__(self, path, size):
        self.font = pygame.font.Font(os.path.join(*path), size)

class Text:
    def __init__(self, text, color, font, rect, action = False):
        x, y, width, height = rect
        self.surf = font.render(text, 1, color)
        self.button_rect = pygame.Rect(rect)
        self.rect = self.surf.get_rect(center = self.button_rect.center)
        if action: self.action = action
        self.pressed = False
def init_hearts():
    section = WIDTH / len(Player.group)
    hearts_len = HEARTSIZE * HEARTS
    left = (section - hearts_len) / 2
    for player_num in range(len(Player.group)):
        for heart_num in range(HEARTS):
            location = (((left + heart_num * HEARTSIZE) + section * player_num), HEIGHT - left)
            rect = empty_heart.surf.get_rect(bottomleft = location)
            Heart.group.append((rect, Player.group[player_num], heart_num))

def init_map():
    for col in range(COLS):
        for row in range(ROWS):
            for key, block in Block.key.items():
                if world[row][col] == key:
                    block_rect = block.surf.get_rect(topleft = (col * BLOCKSIZE, row * BLOCKSIZE))
                    Block.group.append((block.surf, block_rect))
                    if not (row == 0 or col == 0 or row == ROWS - 1 or col == COLS - 1):
                        if world[row + 1][col] == "-" or world[row - 1][col] == "-" or world[row][col + 1] == "-" or world[row][col - 1] == "-":
                            Block.touching_air_group.append((block.surf, block_rect))
                    else:
                        Block.touching_air_group.append((block.surf, block_rect))     
def blit_Player_group():
    for player in Player.group:
        if player.alive:
            win.blit(player.surf, player.rect)
            triangle = [
                (player.rect.left + 14, player.rect.top - 5),
                (player.rect.right - 14, player.rect.top - 5),
                (player.rect.centerx, player.rect.top - 12), ]
            pygame.draw.polygon(win, player.marker_color, triangle)
            if player.direction_facing == 'left':
                rect = sword_left.surf.get_rect(bottomright = player.rect.center)
                win.blit(sword_left.surf, rect)
            else:
                rect = sword_right.surf.get_rect(bottomleft = player.rect.center)
                win.blit(sword_right.surf, rect)

def blit_Heart_group():
    for heart in Heart.group:
        heart_rect, heart_player, heart_num = heart
        win.blit(empty_heart.surf, heart_rect)
    for player in Player.group:
        for heart in Heart.group:
            heart_rect, heart_player, heart_num = heart
            if heart_player == player and heart_num < player.health:
                if player.marker_color == BLUE:
                    win.blit(blue_heart.surf, heart_rect)
                elif player.marker_color == RED:
                    win.blit(red_heart.surf, heart_rect)
                elif player.marker_color == YELLOW:
                    win.blit(yellow_heart.surf, heart_rect)
                elif player.marker_color == GREEN:
                    win.blit(green_heart.surf, heart_rect)

def blit_Text_group(*args):
    for text in args:
        x, y, w, h = text.button_rect
        X, Y, W, H = text.rect
        pygame.draw.rect(win, BUTTON_COLOR_2 , (x - 5 * SCALE, y + 5 * SCALE, w, h))
        if text.pressed:
            pygame.draw.rect(win, BUTTON_COLOR , (x - 5 * SCALE, y + 5 * SCALE, w, h))
            win.blit(text.surf, (X - 5 * SCALE, Y + 5 * SCALE, W, H))
        else:
            pygame.draw.rect(win, BUTTON_COLOR , text.button_rect)
            win.blit(text.surf, text.rect)

def blit_Block_group():
    for block in Block.group:
        block_surf, block_rect = block
        win.blit(block_surf, block_rect)

def blit_Cloud_group():
    for cloud in Cloud.group:
        win.blit(cloud.surf, cloud.rect)

def blit_backgroud():
    win.fill(SKYCOLOR)
    win.blit(sun.surf, sun_rect)
    blit_Cloud_group()
    blit_Block_group()
    win.blit(darken.surf, darken_rect)

def str_to_list(string):
    array = []
    str_list = string.split('\n')
    for line in str_list:
        char_list = [char for char in line]
        array.append(char_list)
    return array

def list_col_row(array):
    col, row = 0, 0
    for line in array: row +=1
    for space in array[0]: col += 1
    return col, row

def check_quit():
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def check_mousedown(*args):
    if event.type == pygame.MOUSEBUTTONDOWN:
        for text in args:
            if text.button_rect.collidepoint(mouse_pos):
                text.pressed = True 
def check_mouseup(*args):
    if event.type == pygame.MOUSEBUTTONUP:
        for text in args:
            text.pressed = False
            if text.button_rect.collidepoint(mouse_pos):
                return text.action
    global screen; return screen

world_str = '''\
----------------------------------------
----------------------------------------
----------------------------------------
------l---------------------------gd----
-----ll------------------------ddssds---
----llll--------------------------------
---llwl-l------------------------------g
--l--w--------------------------------gd
-----w-------------------------------gdd
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
SKYCOLOR = '#8EC0FF'
SKYCOLOR2 = '#3151d4'
BLUE = '#2b1fdb'
YELLOW = '#eaed2b'
RED = '#e84343'
GREEN = '#2ead2b'
BLACK = '#000000'
WHITE = '#ffffff'
BUTTON_COLOR = '#e3e3e3'
BUTTON_COLOR_2 = '#808080'


SCALE = 0.5
#unchangable varibles
WIDTH, HEIGHT= 1600 * SCALE, 800 * SCALE
SIZE = (WIDTH, HEIGHT)
COLS, ROWS = list_col_row(world)
BLOCKSIZE = (WIDTH/COLS)
PLAYER_SIZE = 0.17 * SCALE
SWORD_SIZE = 20 * SCALE
WALKING_ANIMATION_DELAY = 3
TITLE_FONT_SIZE = int(65 * SCALE)
PLAY_FONT_SIZE = int(50 * SCALE)
HEARTSIZE = 36 * SCALE
CLOUD_SIZE = 25 * SCALE
WALK_SOUND_DELAY = 15
HIT_COOLDOWN = 20
CLOUD_SPEED = 10 // SCALE
SUNSIZE = 70 * SCALE
SUN_POS = (WIDTH * 0.4, HEIGHT * 0.1)

#changable variables
FPS = 30
g = 0.05 * SCALE**(1/2)
JUMP_VEL = 9 * SCALE
X_MOVE_DISTANCE = 6 * SCALE
X_KNOCKBACK_DISTANCE = 3 * SCALE
KNOCKBACK_TIME = 15
Y_KNOCKBACK_VELOCITY =  3 * SCALE
HEARTS = 10

MUSIC = True
MASTER_VOLUME = 1
WALK_SOUND_VOLUME = 0.5 * MASTER_VOLUME
LAND_SOUND_VOLUME = 0.2 * MASTER_VOLUME
ATTACK_SOUND_VOLUME = 0.6 * MASTER_VOLUME
MUSIC_VOLUME = 0.2 * MASTER_VOLUME

#win
win = pygame.display.set_mode(SIZE)
win_rect = win.get_rect()

#cloud
cloud_1 = Cloud(('minecraftAssets', 'cloud_1.png'), (WIDTH * 0, HEIGHT/3))
cloud_2 = Cloud(('minecraftAssets', 'cloud_2.png'), (WIDTH * .25, HEIGHT/8))
cloud_3 = Cloud(('minecraftAssets', 'cloud_3.png'), (WIDTH * .5, HEIGHT/5))
cloud_4 = Cloud(('minecraftAssets', 'cloud_4.png'), (WIDTH * .75, HEIGHT/16))
cloud_5 = Cloud(('minecraftAssets', 'cloud_4.png'), (WIDTH * 1, HEIGHT/8))

#blocks
grass = Block(('minecraftAssets', 'grass.png'), 'g')
dirt = Block(('minecraftAssets', 'dirt.png'), 'd')
stone = Block(('minecraftAssets', 'stone.png'), 's')
wood = Block(('minecraftAssets', 'wood.png'), 'w')
leaves = Block(('minecraftAssets', 'leaves.png'), 'l')
bedrock = Block(('minecraftAssets', 'bedrock.png'), 'b')
andesite = Block(('minecraftAssets', 'andesite.png'), 'a')
iron_ore = Block(('minecraftAssets', 'iron_ore.png'), 'i')
diamond_ore = Block(('minecraftAssets', 'diamond_ore.png'), 'D')

#heart
red_heart = Heart(('minecraftAssets', 'red_heart.png'))
yellow_heart = Heart(('minecraftAssets', 'yellow_heart.png'))
blue_heart = Heart(('minecraftAssets', 'blue_heart.png'))
green_heart = Heart(('minecraftAssets', 'green_heart.png'))
empty_heart = Heart(('minecraftAssets', 'empty_heart.png'))

#image
sword_right = Image(('minecraftAssets', 'sword_right.png'), size = (SWORD_SIZE, SWORD_SIZE))
sword_left =  Image(('minecraftAssets', 'sword_left.png'), size = (SWORD_SIZE, SWORD_SIZE))
sun = Image(('minecraftAssets', 'sun.png'), size = (SUNSIZE, SUNSIZE))
sun_rect = sun.surf.get_rect(center = SUN_POS)
darken = Image((('minecraftAssets', 'darken.png')), size = (WIDTH, HEIGHT))
darken_rect = darken.surf.get_rect()

#font
title = Font(('minecraftAssets', 'pixel_font.TTF'),TITLE_FONT_SIZE)
button = Font(('minecraftAssets', 'pixel_font.TTF'), PLAY_FONT_SIZE)

#text
title_text = Text('Minecraft 2D PVP', '#7cb0de', title.font, (400 * SCALE, 200 * SCALE, 0, 0))
controls_title_text = Text('Controls', '#7cb0de', button.font, (400 * SCALE, 200 * SCALE, 0, 0))
settings_title_text = Text('Settings', '#7cb0de', button.font, (400 * SCALE, 200 * SCALE, 0, 0))
play_text = Text('Play', '#7cb0de', button.font, (1000 * SCALE, 200 * SCALE, 350 * SCALE, 100 * SCALE), 'play')
controls_text = Text('Controls', '#7cb0de', button.font, (1000 * SCALE, 400 * SCALE, 350 * SCALE, 100 * SCALE), 'controls')
settings_text = Text('Settings', '#7cb0de', button.font, (1000 * SCALE, 600 * SCALE, 350 * SCALE, 100 * SCALE), 'settings')
back_text = Text('Menu', '#7cb0de', button.font, (1050 * SCALE, 100 * SCALE, 350 * SCALE, 100 * SCALE), 'menu')

#music
if MUSIC:
    pygame.mixer.music.load(os.path.join('minecraftAssets', 'minecraft_music.ogg'))
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(-1)

#sounds
land_1 = SoundEffect(('minecraftAssets', 'land_1.mp3'), 'land')
land_2 = SoundEffect(('minecraftAssets', 'land_2.mp3'), 'land')
land_3 = SoundEffect(('minecraftAssets', 'land_3.mp3'), 'land')
land_4 = SoundEffect(('minecraftAssets', 'land_4.mp3'), 'land')
walk_1 = SoundEffect(('minecraftAssets', 'walk_1.mp3'), 'walk')
walk_2 = SoundEffect(('minecraftAssets', 'walk_2.mp3'), 'walk')
walk_3 = SoundEffect(('minecraftAssets', 'walk_3.mp3'), 'walk')
walk_4 = SoundEffect(('minecraftAssets', 'walk_4.mp3'), 'walk')
attack_1 = SoundEffect(('minecraftAssets', 'attack_1.mp3'), 'attack')
attack_2 = SoundEffect(('minecraftAssets', 'attack_2.mp3'), 'attack')
attack_3 = SoundEffect(('minecraftAssets', 'attack_3.mp3'), 'attack')

#player images
player_front = PlayerImage(('minecraftAssets', 'steve_front.png'))
player_left = PlayerImage(('minecraftAssets', 'steve_left.png'))
player_right = PlayerImage(('minecraftAssets', 'steve_right.png'))
player_walk_left_front = PlayerImage(('minecraftAssets', 'steve_walk_left_front.png'))
player_walk_left_back = PlayerImage(('minecraftAssets', 'steve_walk_left_back.png'))
player_walk_right_front = PlayerImage(('minecraftAssets', 'steve_walk_right_front.png'))
player_walk_right_back = PlayerImage(('minecraftAssets', 'steve_walk_right_back.png'))
player_walk_left_front_mid = PlayerImage(('minecraftAssets', 'steve_walk_left_front_mid.png'))
player_walk_left_back_mid = PlayerImage(('minecraftAssets', 'steve_walk_left_back_mid.png'))
player_walk_right_front_mid = PlayerImage(('minecraftAssets', 'steve_walk_right_front_mid.png'))
player_walk_right_back_mid = PlayerImage(('minecraftAssets', 'steve_walk_right_back_mid.png'))

#players
player1 = Player(midbottom = (WIDTH * 0.2, 0), right_key = 'd', left_key = 'a', up_key = 'w', attack_key = 's', marker_color = BLUE)
player2 = Player(midbottom = (WIDTH * 0.4, 0), right_key = 'SEMICOLON', left_key = 'k', up_key = 'o', attack_key = 'l', marker_color = RED)
player3 = Player(midbottom = (WIDTH * 0.6, 0), right_key = 'RIGHT', left_key = 'LEFT', up_key = 'UP', attack_key = 'DOWN', marker_color = YELLOW)
player4 = Player(midbottom = (WIDTH * 0.8, 0), right_key = 'KP6', left_key = 'KP4', up_key = 'KP8', attack_key = 'KP5', marker_color = GREEN)

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

init_hearts()
init_map()
screen = 'menu'

while True:
    if screen == 'menu':
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            check_quit()
            check_mousedown(play_text, settings_text, controls_text)                       
            screen = check_mouseup(play_text, settings_text, controls_text)  
        Cloud.update_pos()
        blit_backgroud()
        blit_Text_group(title_text,play_text, settings_text, controls_text)
        pygame.display.update()

    elif screen == 'controls':
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            check_quit()
            check_mousedown(back_text)
            screen = check_mouseup(back_text)
        Cloud.update_pos()
        blit_backgroud()
        blit_Text_group(controls_title_text, back_text)
        pygame.display.update()

    elif screen == 'settings':
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            check_quit()
            check_mousedown(back_text)
            screen = check_mouseup(back_text) 
        Cloud.update_pos()
        blit_backgroud()
        blit_Text_group(settings_title_text, back_text)
        pygame.display.update()

    elif screen == 'play':
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            check_quit()
            if event.type == pygame.KEYDOWN:
                for player in Player.group:
                    player.check_attack(event)

        for player in Player.group:
            if player.alive:
                player.update_timers()
                player.update_pos()
                player.update_surf()
                player.update_keys_pressed()
                
        Cloud.update_pos()
        win.fill(SKYCOLOR)
        win.blit(sun.surf, sun_rect)
        blit_Cloud_group()
        blit_Player_group()
        blit_Block_group()
        blit_Heart_group()
        pygame.display.update()