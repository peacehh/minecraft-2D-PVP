#Pygame Minecraft 2d PVP
import pygame, sys, os, random
if getattr(sys, 'frozen', False): application_path = os.path.dirname(sys.executable)
elif __file__: application_path = os.path.dirname(__file__)
#config_path = os.path.join(application_path, config_name)
pygame.font.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption('Minecraft 2D PVP')

class Image:
    Heart = []
    def __init__(self, path, scale = False, size = False, group = ''):
        self.surf = pygame.image.load(os.path.join(*path)).convert_alpha()
        if size:
            self.surf = pygame.transform.scale(self.surf, size)
        if scale:
            self.surf = pygame.transform.scale(self.surf, (self.surf.get_width() * scale, self.surf.get_height() * scale))
        if group == 'heart': Image.Heart.append(self)

class Player:
    group = []
    def __init__(self, midbottom, right_key, left_key, up_key, attack_key, marker_color, color, heart_color, number):
        Image.__init__(self, ('minecraftAssets', 'steve_front.png'), scale = PLAYER_SIZE)
        self.rect = self.surf.get_rect(midbottom = midbottom)
        self.vel = 0
        self.animation_time = 0
        self.walk_sound_delay = 0
        self.hit_cooldown = 0
        self.in_air = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.right_key = right_key
        self.left_key = left_key
        self.up_key = up_key
        self.attack_key = attack_key
        self.health = HEARTS
        self.marker_color = marker_color
        self.number = number
        self.color = color
        self.in_cobweb = False
        self.heart_color = heart_color
        self.direction_facing = ''
        self.knockback_direction = ''
        self.x = int((self.rect.left + BLOCKSIZE/2)//BLOCKSIZE)
        self.y = int((self.rect.bottom + BLOCKSIZE/2 - self.rect.width)//BLOCKSIZE)
        Player.group.append(self)

    def update_player(self):
        #update coordinates and in_air
        self.x = int((self.rect.left + BLOCKSIZE/2)//BLOCKSIZE)
        self.y = int((self.rect.bottom + BLOCKSIZE/2 - self.rect.width)//BLOCKSIZE)
        lower_rect = pygame.Rect((self.rect.x, self.rect.y), (self.rect.width, self.rect.height + 1))
        for block in Block.collision_group:
            block_surf, block_rect = block
            self.in_air = not lower_rect.colliderect(block_rect)
            if not self.in_air:
                break

        #check for x knockback
        if self.in_air and self.knockback_direction != '':
            if self.knockback_direction == 'left':
                self.move_left(X_KNOCKBACK_DISTANCE)
            elif self.knockback_direction == 'right':
                self.move_right(X_KNOCKBACK_DISTANCE)
        else: self.knockback_direction = ''

        #check on cobweb
        if world[self.y][self.x] == '#' or world[self.y - 1][self.x] == '#':
            self.in_cobweb = True
        else:
            self.in_cobweb = False

        #check to move in y
        if self.in_air and self.vel ==0:
            self.rect.y += 1
        if self.in_air or self.vel != 0:
            self.move_y()
        else:
            self.vel = 0

        #check on slime
        if world[self.y + 1][self.x] == 'S' and not self.in_air:
            self.vel = SLIME_VEL
            slime_jump.sound.play()

        #walk sound timer
        if self.walk_sound_delay > 0:
            self.walk_sound_delay -= 1

        #hit_cooldown
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        #check animation
        if self.left_pressed and self.right_pressed and not self.in_air:
            self.surf = player_front.surf
        elif self.left_pressed or self.right_pressed or self.in_air:
            self.animation()
        else:
            if self.direction_facing == 'left':
                self.surf = player_left.surf
            else:
                self.surf = player_right.surf
            self.animation_time = 0

    def update_keys_pressed(self):
        if keys_pressed[getattr(pygame , 'K_' + self.right_key)]:
            if self.in_cobweb:
                self.move_right(COB_MOVE_DISTANCE)
            else:
                self.move_right(X_MOVE_DISTANCE)
        else:
            self.right_pressed = False

        if keys_pressed[getattr(pygame , 'K_' + self.left_key)]:
            if self.in_cobweb:
                self.move_left(COB_MOVE_DISTANCE)
            else:
                self.move_left(X_MOVE_DISTANCE)
        else:
            self.left_pressed = False

        if keys_pressed[getattr(pygame , 'K_' + self.up_key)]:
            self.up_pressed = True
            if not self.in_air:
                self.vel = JUMP_VEL
        else:
            self.up_pressed = False

    def check_attack(self, event):
        if event.key == getattr(pygame , 'K_' + self.attack_key):
            for player in Player.group:
                if self.rect.colliderect(player.rect) and player != self and player.hit_cooldown == 0:
                    player.hit_cooldown = HIT_COOLDOWN
                    player.vel = Y_KNOCKBACK_VELOCITY
                    random.choice(SoundEffect.attack).sound.play()
                    player.health -= 1
                    if player.health == 0:
                        Player.group.remove(player)
                    if len(player.group) == 1:
                        global screen ; screen = 'game over'
                    #knockback in x
                    if self.rect.x < player.rect.x:
                        player.knockback_direction = 'right'
                    else:
                        player.knockback_direction = 'left'
                    player.rect.y -= 1

    def animation(self):
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
        self.vel -= g
        self.rect.y -= self.vel
        if self.in_cobweb:
            if self.vel > 0:
                self.vel -= 0.2
                if self.vel < 0 : self.vel = 0
            if self.vel < 0 :
                self.vel += 0.5
                if self.vel > 0 : self.vel = 0

        landed = False
        if self.is_in_block():
            if self.vel < 0:
                while self.is_in_block():
                    self.rect.y -= 1
                landed = True
            else:
                while self.is_in_block():
                    self.rect.y += 1
            self.vel = 0
        while self.rect.bottom > HEIGHT:
            self.rect.y += 1
        if landed and world[self.y + 1][self.x] != 'S':
            random.choice(SoundEffect.land).sound.play()


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
        for block in Block.collision_group:
            block_surf, block_rect = block
            if self.rect.colliderect(block_rect):
                return True
        #if player is off map
        if self.rect.right > WIDTH or self.rect.left < 0:
            return True
        return False

    def walk_sound(self):
        if (self.right_pressed or self.left_pressed) and not self.in_air:
            if self.walk_sound_delay == 0:
                random.choice(SoundEffect.walk).sound.play()
                self.walk_sound_delay = WALK_SOUND_DELAY
class Block():
    group = []
    collision_group = []
    key = {}
    entities = ['-']
    def __init__(self, path, key, kind):
        Image.__init__(self, path, size = (BLOCKSIZE, BLOCKSIZE))
        Block.key.update({key:self})
        self.key = key
        self.kind = kind
        if self.kind == 'entity': Block.entities.append(self.key)

class SoundEffect():
    land = []
    walk = []
    attack = []
    slime = []
    def __init__ (self, path, group , vol):
        if group:
            getattr(SoundEffect, group).append(self)
        self.sound = pygame.mixer.Sound(os.path.join(*path))
        self.sound.set_volume(vol)

class Cloud():
    move_delay = 0
    group = []
    def __init__(self, path, center):
        Image.__init__(self, path, scale = CLOUD_SIZE)
        self.rect = self.surf.get_rect(center = center)
        Cloud.group.append(self)

class Font:
    def __init__(self, path, size):
        self.font = pygame.font.Font(os.path.join(*path), size)

class Text:
    def __init__(self, text, color, font, rect):
        self.font = font
        self.color = color
        self.surf = font.render(text, 1, color)
        self.outer_rect = pygame.Rect(rect)
        self.rect = self.surf.get_rect(center = self.outer_rect.center)

class ButtonScreen(Text):
    def __init__(self, text, color, font, rect, action):
        self.text = Text(text, color, font, rect)
        self.pressed = False
        self.action = action

class ButtonSwitch(Text):
    def __init__(self, color, font, rect, default):
        self.text = Text('on' if default else 'off', color, font, rect)
        self.pressed = False
        self.current = default

class ButtonInput(Text):
    def __init__(self, color, font, rect, default):
        self.current_text = Text(default, color, font, rect)
        self.input = default
        self.input_text = Text(self.input, color, font, rect)
        self.active = False

def init_hearts():
    section = WIDTH / len(Player.group)
    hearts_len = HEARTSIZE * HEARTS
    left = (section - hearts_len) / 2
    for player in Player.group:
        player_num = player.number - 1
        for heart_num in range(HEARTS):
            location = (((left + heart_num * HEARTSIZE) + section * player_num), HEIGHT - 25)
            rect = empty_heart.surf.get_rect(bottomleft = location)
            Image.Heart.append((rect, heart_num, player))

def init_map():
    for col in range(COLS):
        for row in range(ROWS):
            for key, block in Block.key.items():
                if world[row][col] == key:
                    block_rect = block.surf.get_rect(topleft = (col * BLOCKSIZE, row * BLOCKSIZE))
                    Block.group.append((block.surf, block_rect))
                    if block.kind == 'solid':
                        if not (row == 0 or col == 0 or row == ROWS - 1 or col == COLS - 1):
                            if (world[row + 1][col] in Block.entities
                                or world[row - 1][col] in Block.entities
                                or world[row][col + 1] in Block.entities
                                or world[row][col - 1] in Block.entities):
                                Block.collision_group.append((block.surf, block_rect))
                        else:
                            Block.collision_group.append((block.surf, block_rect))
def blit_Player_group():
    for player in Player.group:
        if player.direction_facing == 'left':
            rect = sword_left.surf.get_rect(bottomright = player.rect.center)
            win.blit(sword_left.surf, rect)
        else:
            rect = sword_right.surf.get_rect(bottomleft = player.rect.center)
            win.blit(sword_right.surf, rect)
        win.blit(player.surf, player.rect)
        triangle = [
            (player.rect.left + 12 * SCALE, player.rect.top - 5 * SCALE),
            (player.rect.right - 12 * SCALE, player.rect.top - 5 * SCALE),
            (player.rect.centerx, player.rect.top - 12 * SCALE)]
        pygame.draw.polygon(win, player.marker_color, triangle)


def blit_Heart_group():
    for heart in Image.Heart:
        heart_rect, heart_num, player = heart
        win.blit(empty_heart.surf, heart_rect)
    for heart in Image.Heart:
        heart_rect, heart_num, player = heart
        heart = player.heart_color
        if heart_num < player.health:
            win.blit(heart.surf, heart_rect)

def blit_Block_group():
    for block in Block.group:
        block_surf, block_rect = block
        win.blit(block_surf, block_rect)

def cloud():
    if CLOUDS:
        #blit
        for cloud in Cloud.group:
            win.blit(cloud.surf, cloud.rect)
        #update
        if Cloud.move_delay == 0:
            for cloud in Cloud.group:
                cloud.rect.x += 1
                if cloud.rect.left > WIDTH:
                    cloud.rect.right = 0
            Cloud.move_delay = CLOUD_SPEED
        else:
            Cloud.move_delay -= 1

Healer_active = []
def healer():
    def cord(x, y): return (x * BLOCKSIZE - BLOCKSIZE/2, y * BLOCKSIZE)
    Healer_pos = [
        cord(1, 9),
        cord(10, 10),
        cord(13, 3),
        cord(23, 2),
        cord(22, 13),
        cord(38, 17),
        cord(34, 4),
        cord(26, 18),
        cord(40, 6),
        cord(28, 5) ]
    #update
    num = random.randint(0, 1000)
    if num == 0:
        pos = random.choice(Healer_pos)
        if pos not in Healer_active and len(Healer_active) < 5:
            Healer_active.append(pos)
    for player in Player.group:
        for pos in Healer_active:
            healer_rect = heal.surf.get_rect(midbottom = pos)
            if player.rect.colliderect(healer_rect) and player.health < 10:
                Healer_active.remove(pos)
                player.health += 1
                health_sound.sound.play()
                if player.health > HEARTS:
                    player.health = HEARTS
    #blit
    for center in Healer_active:
        healer_rect = heal.surf.get_rect(midbottom = center)
        win.blit(heal.surf, healer_rect)


def blit_backgroud():
    win.fill(SKYCOLOR)
    win.blit(sun.surf, sun_rect)
    blit_Block_group()
    cloud()
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
        for button in args:
            if button.text.outer_rect.collidepoint(mouse_pos):
                button.pressed = True

def check_mouseup_ButtonScreen(*args):
    if event.type == pygame.MOUSEBUTTONUP:
        for button_screen in args:
            button_screen.pressed = False
            if button_screen.text.outer_rect.collidepoint(mouse_pos):
                return button_screen.action
    global screen; return screen

def check_mouseup_ButtonSwitch(button_switch):
    if event.type == pygame.MOUSEBUTTONUP:
        button_switch.pressed = False
        if button_switch.text.outer_rect.collidepoint(mouse_pos):
            if button_switch.current == True:
                button_switch.text = Text('off', button_switch.text.color, button_switch.text.font, button_switch.text.outer_rect)
                button_switch.current = False
                return False
            else:
                button_switch.text = Text('on', button_switch.text.color, button_switch.text.font, button_switch.text.outer_rect)
                button_switch.current = True
                return True
    return button_switch.current

def check_mouseup_ButtonInput(button_input):
    if event.type == pygame.MOUSEBUTTONUP:
        if button_input.current_text.outer_rect.collidepoint(mouse_pos) and not button_input.active:
            button_input.active = True
        if not button_input.current_text.outer_rect.collidepoint(mouse_pos):
            button_input.active = False

    if event.type == pygame.KEYDOWN and button_input.active:
        if event.key == pygame.K_BACKSPACE:
            button_input.input = button_input.input[:-1]
        elif event.key == pygame.K_RETURN:
               button_input.active = False
        else:
            button_input.input += event.unicode
        button_input.input_text = Text(button_input.input, button_input.input_text.color, button_input.input_text.font, button_input.input_text.outer_rect)
    return button_input.input

def blit_Text(*args):
    for text in args:
        win.blit(text.surf, text.rect)

def blit_ButtonScreenSwitch(*args):
    for button in args:
        x, y, w, h = button.text.outer_rect
        X, Y, W, H = button.text.rect
        if button.pressed:
            pygame.draw.rect(win, BUTTON_COLOR , (x - BUTTON_OFFSET, y + BUTTON_OFFSET, w, h))
            win.blit(button.text.surf, (X - BUTTON_OFFSET, Y + BUTTON_OFFSET, W, H))
        else:
            pygame.draw.rect(win, BUTTON_COLOR_2 , (x - BUTTON_OFFSET, y + BUTTON_OFFSET, w, h))
            pygame.draw.rect(win, BUTTON_COLOR , button.text.outer_rect)
            win.blit(button.text.surf, button.text.rect)



def blit_ButtonInput(*args):
    for button_input in args:
        rect = button_input.current_text.outer_rect
        border_rect = (rect.left - INPUT_BORDER/2, rect.top - INPUT_BORDER/2, rect.width + INPUT_BORDER, rect.height + INPUT_BORDER)
        pygame.draw.rect(win, BLACK , border_rect)
        if button_input.active:
            pygame.draw.rect(win, BUTTON_COLOR_2 , button_input.current_text.outer_rect)
        else:
            pygame.draw.rect(win, BUTTON_COLOR , button_input.current_text.outer_rect)
        win.blit(button_input.input_text.surf, button_input.input_text.rect)

def col_y(num):
    return 250 * SCALE + num * SETTINGS_BUTTON_HEIGHT * SCALE

world_str = '''\
----------------------------------------
----------------------------------------
--------------ggg-----o#----------p-----
------l-----dddd-#------o---o--dd-gd----
-----ll------ss-----o#-----#-sdsdssds---
----llll------------------------ss------
---llwl-l------------------------------g
--l--w--------------------------------gd
-----w-----------------------------Fpgdd
@@--pwF--p------gg--------ppp-----@ggddd
ddd@ggggggSgpp-gddg--gdgggSggd@@-@dddddd
ddddddddddddgggdddd---dddddddddd-ddddsdd
sddsddddsdddsssddd----ddsdsdsdss-@dddsdd
ddssssdsssssssddds---ssssCssssd---sssssd
sssissidsdsssssssc----ss---Csd----sssssi
ssssiiissssssssssss------------------#Ci
ssssisssssssddsssssS-----------sS-----Ds
sssssssasaddaasssssaaassc--#CssssaccDDss
bbbssbsssbaabbsbbbbbbdssscccssssssssbbbs
bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\
'''
world = str_to_list(world_str)

#colors
SKYCOLOR = '#8EC0FF'
SKYCOLOR2 = '#3151d4'
BLUE = '#2b1fdb'
YELLOW = '#eaed2b'
RED = '#e84343'
GREEN = '#2ead2b'
BLACK = "#000000"
BUTTON_COLOR = '#e3e3e3'
BUTTON_COLOR_2 = '#808080'
TEXT_COLOR = '#7cb0de'

#Adjustable variables
GRAVITY = 10
MOVE_SPEED = 10
JUMP_SPEED = 10
KNOCKBACK_SPEED = 10
SLIME_SPEED = 10
CLOUDS = True
MUSIC = True
PLAYERS = 4
HEARTS = 10
COOLDOWN = 0.75

#variables
SCALE = 1
FPS = 60
WIDTH, HEIGHT= 1600 * SCALE, 800 * SCALE
SIZE = (WIDTH, HEIGHT)
COLS, ROWS = list_col_row(world)
BLOCKSIZE = (WIDTH/COLS)
PLAYER_SIZE = 0.15 * SCALE
SWORD_SIZE = 17 * SCALE
WALKING_ANIMATION_DELAY = 6
HEARTSIZE = 36 * SCALE
CLOUD_SIZE = 25 * SCALE
WALK_SOUND_DELAY = 30
SLIME_VEL = 12 * SCALE
COB_MOVE_DISTANCE = 1
CLOUD_SPEED = 5 // SCALE
SUNSIZE = 70 * SCALE
SUN_POS = (WIDTH * 0.4, HEIGHT * 0.1)
MASTER_VOLUME = 1
WALK_SOUND_VOLUME = 0.5 * MASTER_VOLUME
LAND_SOUND_VOLUME = 0.2 * MASTER_VOLUME
ATTACK_SOUND_VOLUME = 0.6 * MASTER_VOLUME
MUSIC_VOLUME = 0.5 * MASTER_VOLUME
SLIME_SOUND_VOLUME = 1 * MASTER_VOLUME
HEALTH_SOUND_VOLUME = 0.5 * MASTER_VOLUME
SETTINGS_BUTTON_HEIGHT = 75
SETTINGS_BUTTON_WIDTH = 100 * SCALE
BUTTON_WIDTH = 350 * SCALE
BUTTON_HEIGHT = 125 * SCALE
COL_1 = 200 * SCALE
COL_2 = 400 * SCALE
COL_3 = 700 * SCALE
COL_4 = 900 * SCALE
COL_5 = 1000 * SCALE
BUTTON_OFFSET = 10 * SCALE
INPUT_BORDER = 10 * SCALE
TITLE_RECT = (450 * SCALE, 200 * SCALE, 0, 0)
TITLE_FONT_SIZE = int(65 * SCALE)
PLAY_FONT_SIZE = int(50 * SCALE)
SETTINGS_FONT_SIZE = int(25 * SCALE)

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
grass = Block(('minecraftAssets', 'grass.png'), 'g', 'solid')
dirt = Block(('minecraftAssets', 'dirt.png'), 'd', 'solid')
stone = Block(('minecraftAssets', 'stone.png'), 's', 'solid')
wood = Block(('minecraftAssets', 'wood.png'), 'w', 'solid')
leaves = Block(('minecraftAssets', 'leaves.png'), 'l', 'solid')
bedrock = Block(('minecraftAssets', 'bedrock.png'), 'b', 'solid')
andesite = Block(('minecraftAssets', 'andesite.png'), 'a', 'solid')
iron_ore = Block(('minecraftAssets', 'iron_ore.png'), 'i', 'solid')
diamond_ore = Block(('minecraftAssets', 'diamond_ore.png'), 'D', 'solid')
slime = Block(('minecraftAssets', 'slime.png'), 'S', 'solid')
grass_plant = Block(('minecraftAssets', 'grass_plant.png'), 'p', 'entity')
flower_rose = Block(('minecraftAssets', 'flower_rose.png'), 'F', 'entity')
cobblestone = Block(('minecraftAssets', 'cobblestone.png'), 'c', 'solid')
cobblestone_mossy = Block(('minecraftAssets', 'cobblestone_mossy.png'), 'C', 'solid')
planks_oak = Block(('minecraftAssets', 'planks_oak.png'), 'o', 'solid')
web = Block(('minecraftAssets', 'web.png'), '#', 'entity')
coarse_dirt = Block(('minecraftAssets', 'coarse_dirt.png'), '@', 'solid')

#heart
red_heart = Image(('minecraftAssets', 'red_heart.png'), group = 'heart', size = (HEARTSIZE, HEARTSIZE))
yellow_heart = Image(('minecraftAssets', 'yellow_heart.png'), group = 'heart', size = (HEARTSIZE, HEARTSIZE))
blue_heart = Image(('minecraftAssets', 'blue_heart.png'), group = 'heart', size = (HEARTSIZE, HEARTSIZE))
green_heart = Image(('minecraftAssets', 'green_heart.png'), group = 'heart', size = (HEARTSIZE, HEARTSIZE))
empty_heart = Image(('minecraftAssets', 'empty_heart.png'), group = 'heart', size = (HEARTSIZE, HEARTSIZE))

#image
sword_right = Image(('minecraftAssets', 'sword_right.png'), size = (SWORD_SIZE, SWORD_SIZE))
sword_left =  Image(('minecraftAssets', 'sword_left.png'), size = (SWORD_SIZE, SWORD_SIZE))
sun = Image(('minecraftAssets', 'sun.png'), size = (SUNSIZE, SUNSIZE))
sun_rect = sun.surf.get_rect(center = SUN_POS)
darken = Image((('minecraftAssets', 'darken.png')), size = (WIDTH, HEIGHT))
darken_rect = darken.surf.get_rect()
keyboard = Image((('minecraftAssets', 'keyboard.png')), scale = (0.75 * SCALE))
keyboard_rect = keyboard.surf.get_rect(center = (WIDTH/2, HEIGHT * 0.6))
keyboard_arrow = Image((('minecraftAssets', 'keyboard_arrow.png')), scale = (0.75 * SCALE))
keyboard_arrow_rect = keyboard_arrow.surf.get_rect(center = (WIDTH/2, HEIGHT * 0.2))
heal = Image(('minecraftAssets', 'healer.png'), scale = (SCALE * 2))

#font
title = Font(('minecraftAssets', 'pixel_font.TTF'), TITLE_FONT_SIZE)
button = Font(('minecraftAssets', 'pixel_font.TTF'), PLAY_FONT_SIZE)
settings = Font(('minecraftAssets', 'pixel_font.TTF'), SETTINGS_FONT_SIZE)

#text
title_text = Text('Minecraft 2D PVP', TEXT_COLOR, title.font, TITLE_RECT)
controls_title_text = Text('Controls', TEXT_COLOR, title.font, TITLE_RECT)
settings_title_text = Text('Settings', TEXT_COLOR, title.font, TITLE_RECT)
about_title_text = Text('About', TEXT_COLOR, title.font, TITLE_RECT)

error_text = Text('',TEXT_COLOR, title.font, (WIDTH//2, HEIGHT * 0.9, 0, 0))
jump_text = Text('Jump',TEXT_COLOR, settings.font, (WIDTH/2, HEIGHT * 0.09, 0, 0))
left_text = Text('Left',TEXT_COLOR, settings.font, (WIDTH * 0.45, HEIGHT * 0.17, 0, 0))
right_text = Text('Right',TEXT_COLOR, settings.font, (WIDTH * 0.56, HEIGHT * 0.17, 0, 0))
attack_text = Text('Attack',TEXT_COLOR, settings.font, (WIDTH/2, HEIGHT * 0.31, 0, 0))
about_text_1= Text('By: Hamza Hafez',TEXT_COLOR, title.font, (COL_3, HEIGHT * 0.5, 0, 0))
about_text_2= Text('Made in Pygame 2.1.2',TEXT_COLOR, title.font, (COL_3, HEIGHT * 0.7, 0, 0))
about_text_3= Text('8/1/2022',TEXT_COLOR, title.font, (COL_3, HEIGHT * 0.9, 0, 0))

#ButtonScreen
play_button_screen = ButtonScreen('Play', TEXT_COLOR, button.font, (COL_1, 400 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'play')
controls_button_screen = ButtonScreen('Controls', TEXT_COLOR, button.font, (COL_5, 200 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'controls')
settings_button_screen = ButtonScreen('Settings', TEXT_COLOR, button.font, (COL_5, 400 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'settings')
about_button_screen = ButtonScreen('About', TEXT_COLOR, button.font, (COL_5, 600 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'about')

back_button_screen = ButtonScreen('Menu', TEXT_COLOR, button.font, (COL_5, 100 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'menu')
back_reset_button_screen = ButtonScreen('Menu', TEXT_COLOR, button.font, (COL_5, 100 * SCALE, BUTTON_WIDTH, BUTTON_HEIGHT), 'reset')

#settings
music_text = Text('Music:', TEXT_COLOR, settings.font, (COL_1, col_y(1), 0, 0))
music_button_switch = ButtonSwitch(TEXT_COLOR, settings.font, (COL_2, music_text.rect.top, SETTINGS_BUTTON_WIDTH , music_text.rect.height), True)
grav_text = Text("Gravity:", TEXT_COLOR, settings.font, (COL_3, col_y(1), 0, 0))
grav_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_4, grav_text.rect.top, SETTINGS_BUTTON_WIDTH , grav_text.rect.height), str(GRAVITY))
move_speed_text = Text("Move Speed:", TEXT_COLOR, settings.font, (COL_3, col_y(2), 0, 0))
move_speed_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_4, move_speed_text.rect.top, SETTINGS_BUTTON_WIDTH , move_speed_text.rect.height), str(MOVE_SPEED))
jump_speed_text = Text("Jump Speed:", TEXT_COLOR, settings.font, (COL_3, col_y(3), 0, 0))
jump_speed_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_4, jump_speed_text.rect.top, SETTINGS_BUTTON_WIDTH , jump_speed_text.rect.height), str(JUMP_SPEED))
players_text = Text("Players 2-4:", TEXT_COLOR, settings.font, (COL_1, col_y(3), 0, 0))
players_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_2, players_text.rect.top, SETTINGS_BUTTON_WIDTH , players_text.rect.height), str(PLAYERS))
clouds_text = Text('Clouds:', TEXT_COLOR, settings.font, (COL_1, col_y(2), 0, 0))
clouds_button_switch = ButtonSwitch(TEXT_COLOR, settings.font, (COL_2, clouds_text.rect.top, SETTINGS_BUTTON_WIDTH, clouds_text.rect.height), True)
hearts_text = Text('Hearts:', TEXT_COLOR, settings.font, (COL_1, col_y(4), 0, 0))
hearts_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_2, hearts_text.rect.top, SETTINGS_BUTTON_WIDTH, hearts_text.rect.height), str(HEARTS))
cooldown_text = Text('Hit Cooldown (sec):', TEXT_COLOR, settings.font, (COL_1, col_y(5), 0, 0))
cooldown_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_2, cooldown_text.rect.top, SETTINGS_BUTTON_WIDTH, cooldown_text.rect.height), str(COOLDOWN))
knockback_text = Text('Knockback Speed:', TEXT_COLOR, settings.font, (COL_3, col_y(4), 0, 0))
knockback_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_4, knockback_text.rect.top, SETTINGS_BUTTON_WIDTH, knockback_text.rect.height), str(KNOCKBACK_SPEED))
slime_text = Text('Slime Speed:', TEXT_COLOR, settings.font, (COL_3, col_y(5), 0, 0))
slime_button_input = ButtonInput(TEXT_COLOR, settings.font, (COL_4, slime_text.rect.top, SETTINGS_BUTTON_WIDTH, slime_text.rect.height), str(SLIME_SPEED))

#music
pygame.mixer.music.load(os.path.join('minecraftAssets', 'minecraft_music.ogg'))
pygame.mixer.music.set_volume(MUSIC_VOLUME)

#sounds
land_1 = SoundEffect(('minecraftAssets', 'land_1.mp3'), 'land', LAND_SOUND_VOLUME)
land_2 = SoundEffect(('minecraftAssets', 'land_2.mp3'), 'land', LAND_SOUND_VOLUME)
land_3 = SoundEffect(('minecraftAssets', 'land_3.mp3'), 'land', LAND_SOUND_VOLUME)
land_4 = SoundEffect(('minecraftAssets', 'land_4.mp3'), 'land', LAND_SOUND_VOLUME)
walk_1 = SoundEffect(('minecraftAssets', 'walk_1.mp3'), 'walk', WALK_SOUND_VOLUME)
walk_2 = SoundEffect(('minecraftAssets', 'walk_2.mp3'), 'walk', WALK_SOUND_VOLUME)
walk_3 = SoundEffect(('minecraftAssets', 'walk_3.mp3'), 'walk', WALK_SOUND_VOLUME)
walk_4 = SoundEffect(('minecraftAssets', 'walk_4.mp3'), 'walk', WALK_SOUND_VOLUME)
attack_1 = SoundEffect(('minecraftAssets', 'attack_1.mp3'), 'attack', ATTACK_SOUND_VOLUME)
attack_2 = SoundEffect(('minecraftAssets', 'attack_2.mp3'), 'attack', ATTACK_SOUND_VOLUME)
attack_3 = SoundEffect(('minecraftAssets', 'attack_3.mp3'), 'attack', ATTACK_SOUND_VOLUME)
slime_jump = SoundEffect(('minecraftAssets', 'slime_jump.mp3'), 'slime', SLIME_SOUND_VOLUME)
health_sound = SoundEffect(('minecraftAssets', 'health_sound.mp3'), 'slime', HEALTH_SOUND_VOLUME)

#player images
player_front = Image(('minecraftAssets', 'steve_front.png'), scale = PLAYER_SIZE)
player_left = Image(('minecraftAssets', 'steve_left.png'), scale = PLAYER_SIZE)
player_right = Image(('minecraftAssets', 'steve_right.png'), scale = PLAYER_SIZE)
player_walk_left_front = Image(('minecraftAssets', 'steve_walk_left_front.png'), scale = PLAYER_SIZE)
player_walk_left_back = Image(('minecraftAssets', 'steve_walk_left_back.png'), scale = PLAYER_SIZE)
player_walk_right_front = Image(('minecraftAssets', 'steve_walk_right_front.png'), scale = PLAYER_SIZE)
player_walk_right_back = Image(('minecraftAssets', 'steve_walk_right_back.png'), scale = PLAYER_SIZE)
player_walk_left_front_mid = Image(('minecraftAssets', 'steve_walk_left_front_mid.png'), scale = PLAYER_SIZE)
player_walk_left_back_mid = Image(('minecraftAssets', 'steve_walk_left_back_mid.png'), scale = PLAYER_SIZE)
player_walk_right_front_mid = Image(('minecraftAssets', 'steve_walk_right_front_mid.png'), scale = PLAYER_SIZE)
player_walk_right_back_mid = Image(('minecraftAssets', 'steve_walk_right_back_mid.png'), scale = PLAYER_SIZE)

walk_animation_left = {
    1: player_walk_left_back_mid.surf,
    2: player_walk_left_back.surf,
    3: player_walk_left_back_mid.surf,
    4: player_left.surf,
    5: player_walk_left_front_mid.surf,
    6: player_walk_left_front.surf,
    7: player_walk_left_front_mid.surf,
    8: player_left.surf,}

walk_animation_right = {
    1: player_walk_right_back_mid.surf,
    2: player_walk_right_back.surf,
    3: player_walk_right_back_mid.surf,
    4: player_right.surf,
    5: player_walk_right_front_mid.surf,
    6: player_walk_right_front.surf,
    7: player_walk_right_front_mid.surf,
    8: player_right.surf,}

if __name__ == "__main__":
    screen = 'menu'
    init_map()
    while True:
        if MUSIC and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        if not MUSIC and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(0)
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        clock.tick(FPS)
        pygame.display.flip()

        if screen == 'reset':
            Player.group.clear()
            Image.Heart.clear()
            Healer_active.clear()
            if PLAYERS > len(Player.group): player1 = Player((WIDTH * 0.2, 0), 'd', 'a', 'w','s', BLUE, 'blue', blue_heart, 1)
            if PLAYERS > len(Player.group): player2 = Player((WIDTH * 0.4, 0), 'SEMICOLON','k', 'o', 'l', RED, 'red', red_heart, 2)
            if PLAYERS > len(Player.group): player3 = Player((WIDTH * 0.6, 0), 'RIGHT', 'LEFT', 'UP', 'DOWN', YELLOW, 'yellow', yellow_heart, 3)
            if PLAYERS > len(Player.group): player4 = Player((WIDTH * 0.8, 0), 'KP6', 'KP4', 'KP8', 'KP5', GREEN, 'green', green_heart, 4)
            g = GRAVITY * 0.02 * SCALE
            JUMP_VEL = JUMP_SPEED * 0.7 * SCALE
            X_MOVE_DISTANCE = MOVE_SPEED * 0.3 * SCALE
            X_KNOCKBACK_DISTANCE = KNOCKBACK_SPEED * 0.1 * SCALE
            Y_KNOCKBACK_VELOCITY =  KNOCKBACK_SPEED * 0.2 * SCALE
            HIT_COOLDOWN = int(60 * COOLDOWN)
            SLIME_VEL = 1.1 * SLIME_SPEED * SCALE

            init_hearts()
            screen = 'play'

        elif screen == 'menu':
            for event in pygame.event.get():
                check_quit()
                check_mousedown(play_button_screen, settings_button_screen, controls_button_screen, about_button_screen)
                screen = check_mouseup_ButtonScreen(play_button_screen, settings_button_screen, controls_button_screen, about_button_screen)
            blit_backgroud()
            blit_ButtonScreenSwitch(play_button_screen, settings_button_screen, controls_button_screen, about_button_screen)
            blit_Text(title_text)
            if screen == 'play':
                screen = 'reset'

        elif screen == 'controls':
            for event in pygame.event.get():
                check_quit()
                check_mousedown(back_button_screen)
                screen = check_mouseup_ButtonScreen(back_button_screen)
            blit_backgroud()
            blit_ButtonScreenSwitch(back_button_screen)
            blit_Text(controls_title_text, jump_text, left_text, right_text, attack_text)
            win.blit(keyboard.surf, keyboard_rect)
            win.blit(keyboard_arrow.surf, keyboard_arrow_rect)

        elif screen == 'about':
            for event in pygame.event.get():
                check_quit()
                check_mousedown(back_button_screen)
                screen = check_mouseup_ButtonScreen(back_button_screen)
            blit_backgroud()
            blit_ButtonScreenSwitch(back_button_screen)
            blit_Text(about_title_text, about_text_1, about_text_2, about_text_3)

        elif screen == 'settings':
            for event in pygame.event.get():
                check_quit()
                check_mousedown(back_button_screen, music_button_switch, clouds_button_switch)
                screen = check_mouseup_ButtonScreen(back_button_screen)
                MUSIC = check_mouseup_ButtonSwitch(music_button_switch)
                CLOUDS = check_mouseup_ButtonSwitch(clouds_button_switch)
                GRAVITY = check_mouseup_ButtonInput(grav_button_input)
                MOVE_SPEED = check_mouseup_ButtonInput(move_speed_button_input)
                JUMP_SPEED = check_mouseup_ButtonInput(jump_speed_button_input)
                PLAYERS = check_mouseup_ButtonInput(players_button_input)
                HEARTS  =  check_mouseup_ButtonInput(hearts_button_input)
                COOLDOWN =  check_mouseup_ButtonInput(cooldown_button_input)
                KNOCKBACK_SPEED = check_mouseup_ButtonInput(knockback_button_input)
                SLIME_SPEED = check_mouseup_ButtonInput(slime_button_input)
            blit_backgroud()
            blit_ButtonScreenSwitch(back_button_screen, music_button_switch, clouds_button_switch)
            blit_ButtonInput(
                grav_button_input,
                move_speed_button_input,
                jump_speed_button_input,
                players_button_input,
                hearts_button_input,
                cooldown_button_input,
                knockback_button_input,
                slime_button_input)
            blit_Text(
                settings_title_text,
                grav_text,
                clouds_text,
                music_text,
                jump_speed_text,
                move_speed_text,
                players_text,
                hearts_text,
                cooldown_text,
                knockback_text,
                error_text,
                slime_text)
            if screen != 'settings':
                try:
                    GRAVITY = float(GRAVITY)
                    MOVE_SPEED = float(MOVE_SPEED)
                    JUMP_SPEED = float(JUMP_SPEED)
                    COOLDOWN = float(COOLDOWN)
                    KNOCKBACK_SPEED = float(KNOCKBACK_SPEED)
                    HEARTS = int(float(HEARTS))
                    PLAYERS = int(float(PLAYERS))
                    SLIME_SPEED = float(SLIME_SPEED)
                    if PLAYERS > 5 or PLAYERS < 2:
                        error_text = Text('Players Must be 2-4', TEXT_COLOR, title.font, (WIDTH//2, HEIGHT * 0.9, 0, 0))
                        screen = 'settings'
                    if HEARTS < 1:
                        error_text = Text('Hearts Must be More than 0', TEXT_COLOR, title.font, (WIDTH//2, HEIGHT * 0.9, 0, 0))
                        screen = 'settings'
                except ValueError:
                    error_text = Text('Enter a Number',TEXT_COLOR, title.font, (WIDTH//2, HEIGHT * 0.9, 0, 0))
                    screen = 'settings'
            if screen != 'settings':
                error_text = Text('',TEXT_COLOR, title.font, (WIDTH//2, HEIGHT * 0.9, 0, 0))

        elif screen == 'game over':
            for event in pygame.event.get():
                check_quit()
                check_mousedown(back_button_screen)
                screen = check_mouseup_ButtonScreen(back_button_screen)
            winner_text = Text(f'PLAYER {Player.group[0].color.upper()} WINS!', TEXT_COLOR, title.font, TITLE_RECT)
            blit_backgroud()
            blit_ButtonScreenSwitch(back_button_screen)
            blit_Text(winner_text)

        elif screen == 'play':
            for event in pygame.event.get():
                check_quit()
                if event.type == pygame.KEYDOWN:
                    for player in Player.group:
                        player.check_attack(event)

            for player in Player.group:
                player.update_player()
                player.update_keys_pressed()

            win.fill(SKYCOLOR)
            win.blit(sun.surf, sun_rect)
            healer()
            blit_Player_group()
            blit_Block_group()
            blit_Heart_group()
            cloud()
