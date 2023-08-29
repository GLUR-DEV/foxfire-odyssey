# Import for modules I use
import pygame
import pymunk
import sys
import pymunk.pygame_util
import numpy
import random
from mapdata import tile_map_1, tile_map_2, tile_map_3

# Constants (for quality of life)
# Block
NATIVE_BLOCK_DIMENSIONS = 16
BLOCK_DIMENSIONS = 48

# Screen
SCREEN_BLOCK_WIDTH = 17
SCREEN_BLOCK_HEIGHT = 13

# Collisions
SIDE_COLLISION_TOLERANCE = 44

# Player
PLAYER_DIMENSION = 44
SPEED_MULT = 3
JUMP_MULT = 550
# ------------------------------

# Game Variables ---------------
# Timer
timer = 0

# Inputs
l_pressed = False
r_pressed = False
mouse_down = False
space_pressed = False
is_grounded = False

# Counters
level = 1
gem_count = 0
current_sprite = 0

# Check for unlocks
level_unlock = False
level_unlock1 = False
level_unlock2 = False
level_unlock3 = False

# Init
mainmenu_init = False
credits_init = False
settings_init = False
death_init = False
level1_init = False
level2_init = False
level3_init = False
gem_init = True

# Levels
delevel = False
state = "MainMenu"
top_level = 0
level_changed = False

# Animate
animate_teleport = False
animate_death = False

# Settings
music_state = True
SFX_state = True
Trees_state = False

# Sound
music_init = False
SFX_init = False
start_time = 0
prev_terrain = 0

# Difficulty
difficulty = 0
# ------------------------------

# Terrain creation off Tilemap
def check_block(layer, block, x_pos, tile_data):

    # Get current tile off tilemap
    tile = tile_data[layer][block]
    
    # Iterate through each possible block, then create a terrain object at the correct x and y, with graphics assigned from tilemap
    if 0 <= tile < 6:
        return Terrain(tile,x_pos,screen_height - (BLOCK_DIMENSIONS * (layer+ 0.5)),space)
    
    # Else (-1) return None
    return None

# Handles playing different music at different times
def music_handler():
    # Globals
    global music_init, start_time, state
    
    # Timer to check when music needs to restart
    if timer >= start_time+81:
        game_music.stop()
        main_menu_music.stop()
        music_init = False

    # If music is toggled by player
    if music_state:

        # If music has not been init yet
        if not music_init:
            # Setting timer each time music is init
            start_time = timer

            # If in menus play menu music and stop all other music
            if state == "MainMenu" or state == "Credits" or state == "Settings":
                game_music.stop()

                main_menu_music.set_volume(1.0)
                main_menu_music.play()

            # If in game play game music and stop all other music
            if state == "Level1" or state == "Level2" or state == "Level3":
                main_menu_music.stop()

                game_music.set_volume(1.0)
                game_music.play()

            # Music has init
            music_init = True
    
    # If music is not toggled stop all music
    else:
        main_menu_music.stop()
        game_music.stop()

# Handles playing various SFX
def SFX_handler():
    # Globals
    global state, SFX_init, prev_terrain

    sound_to_play = 0

    # Declaring terrain blocks I want to add SFX for
    grass = pygame.transform.scale(pygame.image.load("Assets\\Enviroment\\Blocks\\grass.png"), (BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))
    sky_grass = pygame.transform.scale(pygame.image.load("Assets\\Enviroment\\Blocks\\sky_grass.png"), (BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))
    stone = pygame.transform.scale(pygame.image.load("Assets\\Enviroment\\Blocks\\stone.png"), (BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))
    snow_grass = pygame.transform.scale(pygame.image.load("Assets\\Enviroment\\Blocks\\snow_grass.png"), (BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))
    snow_stone = pygame.transform.scale(pygame.image.load("Assets\\Enviroment\\Blocks\\snow_stone.png"), (BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))

    # Creating a pixel map for each block
    grass_pixels = pygame.surfarray.array2d(grass)
    sky_grass_pixels = pygame.surfarray.array2d(sky_grass)
    stone_pixels = pygame.surfarray.array2d(stone)
    snow_grass_pixels = pygame.surfarray.array2d(snow_grass)
    snow_stone_pixels = pygame.surfarray.array2d(snow_stone)

    # If in the game
    if state == "Level1" or state == "Level2" or state == "Level3":

        # Iterating through terrain and player group
        for terrain in terrain_group:
            for player in player_group:

                # Getting the terrain block below the player
                if terrain.rect.x < player.rect.x+24 < terrain.rect.x+48:
                    if terrain.rect.y-48 < player.rect.y+24 < terrain.rect.y:

                        # Check whether the previous terrain block the player was standing on is the same, if not un-init SFX
                        if prev_terrain != terrain:
                            SFX_init = False
                        
                        # Setting previous terrain variable
                        prev_terrain = terrain

                        # Creating a pixel map for terrain we're standing on
                        terrain_pixels = pygame.surfarray.array2d(terrain.image)

                        # Matching terrain block pixel map with our pixel maps above, when a match is found we specify which sound to play
                        if (terrain_pixels == grass_pixels).all() or (terrain_pixels == sky_grass_pixels).all():
                            sound_to_play = 0
                        if (terrain_pixels == stone_pixels).all():
                            sound_to_play = 1
                        if (terrain_pixels == snow_stone_pixels).all() or (terrain_pixels == snow_grass_pixels).all():
                            sound_to_play = 2

                        # If SFX is not init
                        if not SFX_init:

                            # Play a random sound from the sound group specified above (grass, stone, snow)
                            if sound_to_play == 0:
                                used_sound = random.randint(0,3)
                                grass_SFX[used_sound].set_volume(0.5)
                                grass_SFX[used_sound].play()
                            if sound_to_play == 1:
                                used_sound = random.randint(0,3)
                                stone_SFX[used_sound].set_volume(0.5)
                                stone_SFX[used_sound].play()
                            if sound_to_play == 2:
                                used_sound = random.randint(0,3)
                                snow_SFX[used_sound].set_volume(0.5)
                                snow_SFX[used_sound].play()

                            # SFX has init
                            SFX_init = True

# Handles game states/scenes
class GameState():

# Init
    def __init__(self):
        # Globals
        global state

        # Init State
        state = "Start"

# Start state
    def Start(self):
        # Globals
        global state, timer, music_init

        # Event handler
        for event in pygame.event.get():

            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Set mouse to invisible
        pygame.mouse.set_visible(False)

        # Show the start screen for 5 seconds then switch to the main menu and init music
        if timer >= 5:
            state = "MainMenu"
            music_init = False

        # Draw our start screen
        screen.blit(loading_skybox, (0,0))

        # Update display every frame
        pygame.display.update()

# Main menu state
    def MainMenu(self):
        # Globals
        global current_sprite, mouse_down, music_init, mainmenu_init

        # Event Handler
        for event in pygame.event.get():

            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # If main menu sprites have not init
        if not mainmenu_init:
            UI_group.add(UI(408, 192, 2)) # Play button
            UI_group.add(UI(408, 242, 3)) # Settings button
            UI_group.add(UI(408, 292, 8)) # Quit button
            UI_group.add(UI(730, 25, 9))  # Credits button

            # Main menu init
            mainmenu_init = True

        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw our main menu background
        screen.blit(main_menu_skybox,(0,0))

        # Draw fake character that animates each frame
        right_idle = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\player\\idle\\player-idle-{i + 1}.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION)) for i in range(4)]
        image = right_idle[int(current_sprite) % len(right_idle)]
        current_sprite += 0.1
        screen.blit(image,(384,389))

        # Draw and update UI
        UI_group.draw(screen)
        UI_group.update()

        # Update screen per frame
        pygame.display.update()

# Credits state
    def Credits(self):
        # Globals
        global credits_init, mouse_down

        # Event Handler
        for event in pygame.event.get():

            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # If sprites for credits hasnt init
        if not credits_init:
            UI_group.add(UI(85, 595, 7)) # Back button

            # Credits have init
            credits_init = True  

        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw Skybox
        screen.blit(credits_skybox,(0,0))

        # Draws and updates UI
        UI_group.draw(screen)
        UI_group.update()

        # Update screen per frame
        pygame.display.update()     

# Settings state
    def Settings(self):
        # Globals
        global settings_init, mouse_down

        # Event Handler
        for event in pygame.event.get():

            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False   

        # If settings sprites havnt init
        if not settings_init:
            UI_group.add(UI(408, 150, 4))  # Music toggle
            UI_group.add(UI(408, 225, 5))  # SFX toggle
            UI_group.add(UI(408, 300, 6))  # Trees toggle
            UI_group.add(UI(408, 375, 12)) # Difficulty toggle
            UI_group.add(UI(85, 29, 7))   # Back button

            # Settings have init
            settings_init = True

        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw Skybox
        screen.blit(settings_skybox,(0,0))

        # Draws and updates UI
        UI_group.draw(screen)
        UI_group.update()

        # Updates display every frame
        pygame.display.update()

# Death state
    def Death(self):
        # Globals
        global mouse_down, death_init

        # Event Handler
        for event in pygame.event.get():

            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # If death sprites hasnt init
        if not death_init:
            UI_group.add(UI(408, 362, 0)) # Restart button
            UI_group.add(UI(408, 437, 1)) # Mainmenu button

            # Death has init
            death_init = True

        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw skybox
        screen.blit(death_skybox,(0,0))

        # Draw and update UI
        UI_group.draw(screen)
        UI_group.update()

        # Update screen every frame
        pygame.display.update()

# Level1 State
    def Level1(self):
        # Globals
        global l_pressed, r_pressed, space_pressed, mouse_down, delevel, music_init, level1_init

        # Event Handler
        for event in pygame.event.get():
            
            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get key down (Left, Right, Space/Up)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    l_pressed = True
                if event.key == pygame.K_RIGHT:
                    r_pressed = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP and is_grounded == True:
                    space_pressed = True

            # Get key up (Left, Right, Space/Up)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    l_pressed = False
                if event.key == pygame.K_RIGHT:
                    r_pressed = False

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # Init level sprites
        if not level1_init:

            # Init terrain
            # Set start x position
            x_pos = 24
            
            # Get how many blocks length and height wise in the screen
            for layer in range(SCREEN_BLOCK_HEIGHT):
                for block in range(SCREEN_BLOCK_WIDTH):

                    # Create variable holding block data we get from check_block() above
                    new_terrain = check_block(layer,block,x_pos, tile_map_1)
                    
                    # If this variable is not None (ie. the block is air/transparent) then add this variable to the terrain group
                    # Python loves to throw an error here so this is nessasary
                    if new_terrain is not None:
                        terrain_group.add(new_terrain)
                    
                    # Move to next block
                    x_pos += 48

                # When layer is complete start at the first block
                x_pos = 24

            # Init enemy
            enemy_group.add(Enemy(648,216,8,3))

            # Init UI
            UI_group.add(UI(792,24,10)) # Exit button

            # Init player and gem if the player is starting the game and not just falling down from level2
            if not delevel:
                player_group.add(Player(screen_width/2,450))
                gem_group.add(Gem(BLOCK_DIMENSIONS/2,BLOCK_DIMENSIONS+(BLOCK_DIMENSIONS/2)))

            # Level1 has init
            level1_init = True
        
        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw skybox
        screen.blit(skybox,(0,0))

        # Draw trees if checked in settings (WARNING: Performance cost!)
        if Trees_state:
            screen.blit(trees,(0,screen_height-316))
            screen.blit(trees,(-200,screen_height-316))

        # Draw terrain
        terrain_group.draw(screen)

        # Draw and update gem(s)
        gem_group.draw(screen)
        gem_group.update()

        # Draw and update player
        player_group.draw(screen)
        player_group.update()

        # Draw and update enemy(s)
        enemy_group.draw(screen)
        enemy_group.update()

        # Draw and update UI
        UI_group.draw(screen)
        UI_group.update()

        # Draw and update game UI
        UI_Digit_group.draw(screen)
        UI_Digit_group.update()
        screen.blit(gem_text,(336,10))

        # Physics hitbox show (DEBUG ONLY!)
        #space.debug_draw(debug_draw_options)

        # Update screen every frame
        pygame.display.update()

# Level2 State
    def Level2(self):
        # Globals
        global l_pressed, r_pressed, space_pressed, mouse_down, delevel, gem_init, level2_init

        # Event Handler
        for event in pygame.event.get():
            
            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get key down (Left, Right, Space/Up)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    l_pressed = True
                if event.key == pygame.K_RIGHT:
                    r_pressed = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP and is_grounded == True:
                    space_pressed = True

            # Get key up (Left, Right, Space/Up)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    l_pressed = False
                if event.key == pygame.K_RIGHT:
                    r_pressed = False

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # Create gem a frame after the level is created
        # This is because while the player is being moved from the top of the screen to the bottom it can occasionally get the gem, this is the easiest work around
        if not gem_init:
            gem_group.add(Gem(24,24))

            # Gem has init
            gem_init = True

        # Init level sprites
        if not level2_init:

            # Init terrain
            # Set start x position
            x_pos = 24

            # Get how many blocks length and height wise in the screen
            for layer in range(SCREEN_BLOCK_HEIGHT):
                for block in range(SCREEN_BLOCK_WIDTH):

                    # Create variable holding block data we get from check_block() above
                    new_terrain = check_block(layer,block,x_pos,tile_map_2)
                    
                    # If this variable is not None (ie. the block is air/transparent) then add this variable to the terrain group
                    # Python loves to throw an error here so this is nessasary
                    if new_terrain is not None:
                        terrain_group.add(new_terrain)
                    
                    # Move to next block
                    x_pos += 48

                # When layer is complete start at the first block
                x_pos = 24
            
            # If this level is being drawn for the first time (ie not a delevel) draw gem
            if not level_unlock2:

                # Gem has not init
                gem_init = False

            # Init enemy
            enemy_group.add(Enemy(792,360,2,3))
            enemy_group.add(Enemy(456,264,2,2))
            enemy_group.add(Enemy(168,360,2,1))

            # Init UI
            UI_group.add(UI(792,24,10)) # Exit button

            # Level2 has init
            level2_init = True
        
        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw skybox
        screen.blit(skybox,(0,0))

        # Draw terrain
        terrain_group.draw(screen)

        # Draw and update gem(s)
        gem_group.draw(screen)
        gem_group.update()

        # Draw and update player
        player_group.draw(screen)
        player_group.update()

        # Draw and update enemy(s)
        enemy_group.draw(screen)
        enemy_group.update()
        
        # Draw and update UI
        UI_group.draw(screen)
        UI_group.update()

        # Draw and update game UI
        UI_Digit_group.draw(screen)
        UI_Digit_group.update()
        screen.blit(gem_text,(336,10))

        # Physics hitbox show (DEBUG ONLY!)
        #space.debug_draw(debug_draw_options)

        # Update screen every frame
        pygame.display.update()

# Level3 State
    def Level3(self):
        # Globals
        global l_pressed, r_pressed, space_pressed, mouse_down, gem_init, level3_init, level_unlock3

        # Event Handler
        for event in pygame.event.get():
            
            # Get window quit
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Get key down (Left, Right, Space/Up)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    l_pressed = True
                if event.key == pygame.K_RIGHT:
                    r_pressed = True
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP and is_grounded == True:
                    space_pressed = True

            # Get key up (Left, Right, Space/Up)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    l_pressed = False
                if event.key == pygame.K_RIGHT:
                    r_pressed = False

            # Get left mouse down
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True

            # Get left mouse up
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False

        # Create gem a frame after the level is created
        # This is because while the player is being moved from the top of the screen to the bottom it can occasionally get the gem, this is the easiest work around
        if not gem_init:
            gem_group.add(Gem(312,24))

            # Gem has init
            gem_init = True

        # Init level sprites
        if not level3_init:

            # Init terrain
            # Set start x position
            x_pos = 24

            # Get how many blocks length and height wise in the screen
            for layer in range(SCREEN_BLOCK_HEIGHT):
                for block in range(SCREEN_BLOCK_WIDTH):

                    # Create variable holding block data we get from check_block() above
                    new_terrain = check_block(layer,block,x_pos,tile_map_3)
                    
                    # If this variable is not None (ie. the block is air/transparent) then add this variable to the terrain group
                    # Python loves to throw an error here so this is nessasary
                    if new_terrain is not None:
                        terrain_group.add(new_terrain)
                    
                    # Move to next block
                    x_pos += 48

                # When layer is complete start at the first block
                x_pos = 24

            # If this level is being drawn for the first time (ie not a delevel) draw gem
            if not level_unlock3:

                # Gem has not init
                gem_init = False

            # Init enemy
            enemy_group.add(Enemy(792,504,3,0.75))
            enemy_group.add(Enemy(264,312,0,3))
            enemy_group.add(Enemy(120,360,1,1))
            enemy_group.add(Enemy(792,408,0,1))

            # Init UI
            UI_group.add(UI(792,24,10)) # Exit button

            # Init portal
            portal_group.add(Portal(312,140,360,456))

            # Level3 has init
            level3_init = True
        
        # Make mouse visible
        pygame.mouse.set_visible(True)

        # Draw skybox
        screen.blit(skybox,(0,0))

        # Draw terrain
        terrain_group.draw(screen)

        # Draw and update gem(s)
        gem_group.draw(screen)
        gem_group.update()

        # Draw and update player
        player_group.draw(screen)
        player_group.update()

        # Draw and update enemy(s)
        enemy_group.draw(screen)
        enemy_group.update()
        
        # Draw and update portal(s)
        portal_group.draw(screen)
        portal_group.update()

        # Draw and update UI
        UI_group.draw(screen)
        UI_group.update()

        # Draw and update game UI
        UI_Digit_group.draw(screen)
        UI_Digit_group.update()
        screen.blit(gem_text,(336,10))

        # Physics hitbox show (DEBUG ONLY!)
        # space.debug_draw(debug_draw_options)

        # Update screen every frame
        pygame.display.update()

# State manager
    def state_manager(self):

        # State Handler (run current state on state variable)
        if state == "Start":
            self.Start()
        if state == "MainMenu":
            self.MainMenu()
        if state == "Credits":
            self.Credits()
        if state == "Settings":
            self.Settings()
        if state == "Death":
            self.Death()
        if state == "Level1":
            self.Level1()
        if state == "Level2":
            self.Level2()
        if state == "Level3":
            self.Level3()

# Terrain Class
class Terrain(pygame.sprite.Sprite):

# Init
    def __init__(self, terrain_type, pos_x, pos_y, space):
        super().__init__()

        # Importing all block graphics
        images = [
            "sky_grass.png",
            "grass.png",
            "dirt.png",
            "stone.png",
            "snow_grass.png",
            "snow_stone.png"
        ]
        # Set block graphics off terrain type
        self.image = pygame.image.load(f"Assets\\Enviroment\\Blocks\\{images[terrain_type]}")
        
        # Create a STATIC physical body for each terrain block and add it too the physical space
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = (pos_x,pos_y)
        self.shape = pymunk.Poly.create_box(self.body,(BLOCK_DIMENSIONS,BLOCK_DIMENSIONS))
        space.add(self.body,self.shape)

        # Create Rect on block graphics
        self.image = pygame.transform.scale(self.image, (BLOCK_DIMENSIONS, BLOCK_DIMENSIONS))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

# Gem Class
class Gem(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y):
        super().__init__()

        # Importing gem graphics and scaling each by 2
        gem_scale = 2
        gem_images = [f"Assets\\sprites\\gem\\gem-{i}.png" for i in range(1,6)]
        self.gem = [pygame.transform.scale(pygame.image.load(img), (15 * gem_scale, 13 * gem_scale)) for img in gem_images]
        self.current_sprite = 0

        # Create Rect off gem graphics
        self.image = self.gem[self.current_sprite]
        self.rect = self.image.get_rect(center=[pos_x, pos_y])

# Animate
    def animate(self):
        # Animate gem every frame
        self.current_sprite = (self.current_sprite + 0.05) % len(self.gem)
        self.image = self.gem[int(self.current_sprite)]

# Gem Logic
    def gem_logic(self):
        # Globals
        global level_unlock, level_unlock1, level_unlock2, level_unlock3, top_level, gem_count

        # Default unlock as False
        unlock = False

        # Iterate through each gem checking for collision each frame
        for gem in gem_group:

            # Checking whether player has collided with the gem rect
            if pygame.sprite.spritecollide(gem, player_group, False):
                    
                # In level 2 there is a special collision I want for the gem to balance the games difficulty
                if level == 2:

                    # If so get player and check whether its right side of its rect is touching the left side of the gem rect
                    for player in player_group:
                        if abs(gem.rect.left-player.rect.right) < 40:

                            # If so set unlock to True
                            unlock = True
                    
                # In level 3 there is a special collision I want for the gem to balance the games difficulty
                if level == 3:

                    # If so get player and check wether its left side of its rect is touching the right side of the gem rect
                    for player in player_group:
                        if abs(gem.rect.left-player.rect.right) > 20:
                                
                                # If so set unlock to True
                                unlock = True
                
                # In level 1 standard collision
                if level == 1:

                    # If so set unlock to True
                    unlock = True
                
            # If unlock is True
            if unlock == True:

                # Play gem SFX
                gem_SFX.set_volume(1.0)
                gem_SFX.play()

                # Kill gem and increment gem count
                gem.kill()
                gem_count+=1

                # Unlock each the next level dependent on what level the player is currently on
                level_unlock = True
                if level_unlock:
                    if level == 1:
                        level_unlock1 = True
                        top_level = 1
                    if level == 2:
                        level_unlock2 = True
                        top_level = 2
                    if level == 3:
                        level_unlock3 = True
                        top_level = 3

# Update
    def update(self):

        # Run functions each frame
        self.gem_logic()
        self.animate()

# Player Class
class Player(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y):
        super().__init__()

        # Class variables
        self.l_timer = False
        self.r_timer = False
        self.prev = ""
        self.timer_init = False
        self.start_time = 0

        # Importing each right idle image and scaling them to PLAYER_DIMENSION, flipping them for the left idle
        self.right_idle = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\player\\idle\\player-idle-{i + 1}.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION)) for i in range(4)]
        self.left_idle = [pygame.transform.flip(image, True, False) for image in self.right_idle]
        
        # Importing each right run image and scaling them to PLAYER_DIMENSION, flipping them for the left run
        self.right_run = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\player\\run\\player-run-{i + 1}.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION)) for i in range(6)]
        self.left_run = [pygame.transform.flip(image, True, False) for image in self.right_run]
        
        # Importing jump1 image and jump2 image and scaling them to PLAYER_DIMENSION
        self.right_jump_1 = pygame.transform.scale(pygame.image.load("Assets\\sprites\\player\\jump\\player-jump-1.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION))
        self.right_jump_2 = pygame.transform.scale(pygame.image.load("Assets\\sprites\\player\\jump\\player-jump-2.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION))
        
        # Flipping jump1 and jump2 for the left
        self.left_jump_1 = pygame.transform.flip(self.right_jump_1, True, False)
        self.left_jump_2 = pygame.transform.flip(self.right_jump_2, True, False)

        # Smoke and death FX, scaling by PLAYER_DIMENSION
        self.smoke_FX = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\player\\FX\\smoke-{i + 1}.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION)) for i in range(5)]
        self.death_FX = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\player\\FX\\death-{i + 1}.png"), (PLAYER_DIMENSION, PLAYER_DIMENSION)) for i in range(5)]
        self.current_sprite = 0

        # Creating a DYNAMIC physics body for the player and adding it to the physics space
        self.body = pymunk.Body(1,1e+100,body_type=pymunk.Body.DYNAMIC)
        self.body.position = (pos_x, pos_y)
        self.shape = pymunk.Poly.create_box(self.body,(PLAYER_DIMENSION,PLAYER_DIMENSION))
        space.add(self.body,self.shape)

        # Creating a Rect for the player and setting its position
        self.image = self.right_idle[self.current_sprite]
        self.rect = self.image.get_rect(center=[pos_x, pos_y])

# Vertical Collision handler
    def vertical_collision_handler(self, collision_tolerance):
        # Globals
        global is_grounded
        
        # Init as not grounded
        is_grounded = False

        # Iterate through all terrain
        for terrain in terrain_group:
            
            # When player is touching or in the ground adjust position as the physics engine isnt amazing
            # Player is grounded
            if abs(self.rect.bottom-terrain.rect.top) < collision_tolerance or self.rect.colliderect(terrain.rect):

                # If sinking into ground slightly adjust y position
                if self.rect.colliderect(terrain.rect):
                    self.body.position += (0,-2)
                    break

                # Set is grounded true
                is_grounded = True
                break

            # When the player is touching or in the bottom of a block adjust position as the physics engine isnt amazing 
            if abs(self.rect.top-terrain.rect.bottom) < collision_tolerance or self.rect.colliderect(terrain.rect):
                self.body.position += (0,1)
                break

# Collision handler
    def collision_handler(self, collision_tolerance):
        # Check whether player is trying to leave scene and block inputs accordingly
        if self.rect.left <= 0:
            return 0
        if self.rect.right >= screen_width:
            return 1
        
        # Check whether player is colliding with sides of terrain and block input accordingly
        # This is nessasary as the physics engine cant do this
        for terrain in terrain_group:
            
            # If colliding on the right side block right input
            if abs(self.rect.right-terrain.rect.left) < collision_tolerance or self.rect.colliderect(terrain.rect):
                if terrain.rect.y-SIDE_COLLISION_TOLERANCE < self.rect.y < terrain.rect.y+SIDE_COLLISION_TOLERANCE: 
                    return 1
                
            # If colliding on the left side block left input
            if abs(self.rect.left-terrain.rect.right) < collision_tolerance or self.rect.colliderect(terrain.rect):
                if terrain.rect.y-SIDE_COLLISION_TOLERANCE < self.rect.y < terrain.rect.y+SIDE_COLLISION_TOLERANCE: 
                    return 0

# Inputs   
    def inputs(self, collision_tolerance):
        # Globals
        global space_pressed, is_grounded

        # Get whether a certain input is being blocked due to collisions
        collision_result = self.collision_handler(collision_tolerance)

        # Get key pressed and not blocked and change position accordingly by SPEED_MULT
        if l_pressed and collision_result != 0:
            self.body.position += (-SPEED_MULT, 0)
        if r_pressed and collision_result != 1:
            self.body.position += (SPEED_MULT, 0)
            
        # Get jump initiated and check if player is on the ground then apply an upwards force
        if space_pressed and is_grounded:
            self.body.apply_impulse_at_local_point((0, -JUMP_MULT))
            space_pressed = False

# Jump animate
    def jump_animate(self, anim_type):
        # Get whether player velocity is negative (ie. going upwards) animate accordingly
        # Note the physics engine seems to move the player within a (-1 -> 0) range. To prevent unwanted animation I used a -1 offset
        if self.body.velocity.y < -1:
            if anim_type == 0:
                self.image = self.left_jump_1
            if anim_type == 1:
                self.image = self.right_jump_1

        # Get whether player velocity is positive (ie. going downwards) animate accordingly
        if self.body.velocity.y > 0:
            if anim_type == 0:
                self.image = self.left_jump_2
            if anim_type == 1:
                self.image = self.right_jump_2

# Animate
    def animate(self):
        # Globals
        global animate_teleport, animate_death, timer, l_pressed, r_pressed, state, music_init

        # Animation speed
        self.current_sprite += 0.1
        
        # Get dominant key pressed
        if self.l_timer:
            self.prev = "l"
        elif self.r_timer:
            self.prev = "r"

        # If only left is pressed set it as the dominant key and animate accordingly, run jump_animate() to check if jumping
        if l_pressed and not self.r_timer:
            self.image = self.left_run[int(self.current_sprite) % len(self.left_run)]
            self.jump_animate(0)
            self.l_timer = True
        elif not l_pressed:
            self.l_timer = False

        # If only right is pressed set it as the dominant key and animate accordingly, run jump_animate() to check if jumping
        if r_pressed and not self.l_timer:
            self.image = self.right_run[int(self.current_sprite) % len(self.right_run)]
            self.jump_animate(1)
            self.r_timer = True
        elif not r_pressed:
            self.r_timer = False
        
        # If left and right are pressed get dominant key and idle in that direction, run jump_animate() to check if jumping
        if l_pressed and r_pressed:
            if self.l_timer:
                self.image = self.left_idle[int(self.current_sprite) % len(self.left_idle)]
                self.jump_animate(0)
            if self.r_timer:
                self.image = self.right_idle[int(self.current_sprite) % len(self.right_idle)]
                self.jump_animate(1)
        
        # If no key is pressed get last pressed key and idle in that direction, run jump_animate() to check if jumping
        if not l_pressed and not r_pressed:
            if self.prev == "l":
                self.image = self.left_idle[int(self.current_sprite) % len(self.left_idle)]
                self.jump_animate(0)
            if self.prev == "r":
                self.image = self.right_idle[int(self.current_sprite) % len(self.right_idle)]
                self.jump_animate(1)

        # If animate teleport
        if animate_teleport:

            # If timer hasn't init
            if not self.timer_init:
                self.current_sprite = 0
                self.start_time = timer
                self.timer_init = True
            
            # If the timer has finished stop animating teleport
            if timer-self.start_time >= 0.75:
                animate_teleport = False

            # Otherwise iterate through smoke FX animation and lock movement
            self.image = self.smoke_FX[int(self.current_sprite) % len(self.smoke_FX)]
            l_pressed = False
            r_pressed = False
            self.body.velocity = (self.body.velocity.x,0)      

        # If animate death
        if animate_death:

            # If timer hasn't init
            if not self.timer_init:
                self.current_sprite = 0
                self.start_time = timer
                self.timer_init = True

            # If the timer has finished stop animating death, switch state to death screen, and kill all current level sprites
            if timer-self.start_time >= 0.75:
                animate_death = False
                state = "Death"
                music_init = False
                for enemy in enemy_group:
                    enemy.kill()
                self.kill()
                space.remove(self.body, self.shape)

            # Otherwise iterate through death FX animation and lock movement
            self.image = self.death_FX[int(self.current_sprite) % len(self.death_FX)]
            l_pressed = False
            r_pressed = False
            self.body.velocity = (self.body.velocity.x,0)  

# Death logic
    def death_logic(self):
        # Globals
        global state, death_init, animate_death

        # Iterate through all enemies
        for enemy in enemy_group:

            # Check for collision with enemy, if collision play death sound stop all other sounds and play death animation
            # Initiate death state
            if self.rect.colliderect(enemy.rect):
                animate_death = True
                death_SFX.set_volume(1.0)
                death_SFX.play()
                game_music.stop()
                for button in UI_group:
                    button.kill()
                
                death_init = False

# Level logic
    def level_logic(self):

        # Globals
        global level_unlock, state, level1_init, level2_init, level3_init, delevel, level, top_level, level_changed, mainmenu_init, music_init, gem_count

        # This is to prevent player phasing through terrain when jumping from levels, if player is colliding with terrain on level change decrease level
        if level_changed:
            for terrain in terrain_group:
                if self.rect.colliderect(terrain.rect):
                    state = f"Level{level-1}"
            if self.rect.y <= screen_height:
                level_changed = False

        # If player hits the top of screen
        if self.rect.top <= 0:

            # If the current level is equal or below the top level acheived then player is allowed to level
            if level <= top_level:

                # If level is 3, I want to send the player to the mainmenu otherwise the game will quite literally crash as there is no Level4 state
                if level == 3:

                    # Change state, change gem_count, level, init music, mainmenu and all levels (mark level1 as not a delevel), as well as kill all level sprites
                    state = "MainMenu"
                    mainmenu_init = False
                    music_init = False
                    for player in player_group:
                        player.kill()
                    for button in UI_group:
                        button.kill()
                    gem_count = 0
                    level = 1
                    level1_init = False
                    level2_init = False
                    level3_init = False
                    delevel = False

                # If not level 3
                else:
                    
                    # Increment level, move player to just underneath the screen and add an upwards force to it, as well as reset level unlock 
                    level_changed = True
                    level += 1
                    self.body.position = (self.body.position.x,screen_height+24)
                    level_unlock = False
                    self.body.apply_impulse_at_local_point((0, -100))
                    state = f"Level{level}"

                # For all levels killing terrain(rect and physics body) and enemys is nessasary
                for terrain in terrain_group:
                    terrain.kill()
                    space.remove(terrain.body, terrain.shape)
                for enemy in enemy_group:
                    enemy.kill()

            # If level cannot be unlocked yet prevent player from leaving scene
            else:
                self.body.velocity = (self.body.velocity.x,0)
                self.body.position += (0,1)

        if not level_changed:
            
            # If player is touching the bottom of screen
            if self.rect.top >= screen_height:

                # Decrease level, set init for all levels as well as mark level 1 as a delevel, set position as well as kill terrain, enemys and gems
                level -= 1
                level1_init = False
                level2_init = False
                level3_init = False
                delevel = True
                level_unlock = True 
                state = f"Level{level}"
                self.body.position = (self.body.position.x,48)
                for terrain in terrain_group:
                    terrain.kill()
                    space.remove(terrain.body, terrain.shape)
                for enemy in enemy_group:
                    enemy.kill()
                for gem in gem_group:
                    gem.kill()

# Update
    def update(self):   
        # Track rect/image on to physical body
        self.rect.center = self.body.position

        # Setting collision tolerance
        collision_tolerance = 2
        
        # Update each player method each frame (pass collision tolerance into collision methods)
        self.vertical_collision_handler(collision_tolerance)
        self.inputs(collision_tolerance)
        self.animate()
        self.death_logic()
        self.level_logic()

# Enemy class
class Enemy(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y, patrol_distance, patrol_speed):
        super().__init__()

        # Set class variables
        self.difficulty_mult = 0

        # Import all left run images as well as scale them by 1.5
        self.left_run = [pygame.transform.scale(pygame.image.load(f"Assets\\sprites\\enemy\\run\\opossum-{i + 1}.png"), (36*1.5, 28*1.5)) for i in range(6)]
        
        # Flip each run image to the right
        self.right_run = [pygame.transform.flip(image, True, False) for image in self.left_run]
        self.current_sprite = 0

        # Create rect off image
        self.image = self.left_run[self.current_sprite]
        self.rect = self.image.get_rect(center=[pos_x, pos_y])
        
        # Make passed in variables accessable in the whole class
        self.patrol_speed = patrol_speed
        self.patrol_distance = patrol_distance
        self.distance_patrolled = 0
        self.init_x = self.rect.x

# Animate
    def animate(self):
        # Animation speed
        self.current_sprite += 0.1

        # If the player is not dying
        if not animate_death:

            # If the enemy is running left animate left
            if self.distance_patrolled <= self.patrol_distance:
                self.image = self.left_run[int(self.current_sprite) % len(self.left_run)]

            # If the enemy is running right animate right
            if (self.patrol_distance*2)+2 > self.distance_patrolled > self.patrol_distance:
                self.image = self.right_run[int(self.current_sprite) % len(self.right_run)]

# Enemy AI
    def enemy_AI(self):

        # Globals
        global difficulty

        # If easy mode set mult to 0
        if difficulty == 0:
            self.difficulty_mult = 0
        # If hard mode set mult to 1
        if difficulty == 1:
            self.difficulty_mult = 1

        # If enemy finished patrol reset patrol
        if (self.patrol_distance*2)+2 == self.distance_patrolled:
            self.distance_patrolled = 0

        # If the player isn't dying
        if not animate_death:

            # If the distance the enemy is, is less than the patrol distance, move enemy left and increment distance patrolled
            if self.distance_patrolled <= self.patrol_distance:
                self.rect.x += -(self.patrol_speed+self.difficulty_mult)
                if self.rect.x <= self.init_x-48:
                    self.distance_patrolled += 1
                    self.init_x = self.rect.x

            # If the distance the enemy is, is more than the patrol distance but less than double the patrol distance, move enemy right and increment distance patrolled
            if (self.patrol_distance*2)+2 > self.distance_patrolled > self.patrol_distance:
                self.rect.x += (self.patrol_speed+self.difficulty_mult)
                if self.rect.x >= self.init_x+48:
                    self.distance_patrolled += 1
                    self.init_x = self.rect.x

# Update
    def update(self):

        # Run enemy methods each frame
        self.animate()
        self.enemy_AI()

# Portal Class
class Portal(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y, teleport_x, teleport_y):
        super().__init__()

        # Set passed in variables to be accesable in the whole class
        self.teleport_x = teleport_x
        self.teleport_y = teleport_y

        # Import each portal image and scale them by 3
        portal = [f"Assets\\sprites\\portal\\portal{i}.png" for i in range(0,4)]
        self.portal = [pygame.transform.scale(pygame.image.load(img), (16 * 3, 4 * 3)) for img in portal]
        self.current_sprite = 0

        # Create Rect off image
        self.image = self.portal[self.current_sprite] 
        self.rect = self.image.get_rect(center=[pos_x, pos_y])

# Animate
    def animate(self):

        # Animate portal each frame
        self.current_sprite = (self.current_sprite + 0.05) % len(self.portal)
        self.image = self.portal[int(self.current_sprite)]

# Portal logic
    def portal_logic(self):

        # Globals
        global animate_teleport

        # If player collides with portal init teleport animation and move player, kill portal
        for player in player_group:
            if pygame.sprite.spritecollide(player, portal_group, True):
                player.body.position = (self.teleport_x, self.teleport_y)
                animate_teleport = True

# Update
    def update(self):

        # Run portal methods every frame
        self.animate()
        self.portal_logic()

# UI Digits class
class UI_Digits(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y):
        super().__init__()

        # Import and scale numbers from 0-9
        UI_number = [f"Assets\\UI\\text\\numbers\\{i}_text.png" for i in range(0,9)]
        self.UI = [pygame.transform.scale(pygame.image.load(img), (10 * 2, 8 * 2)) for img in UI_number]
        self.current_sprite = 0

        # Get Rect from image
        self.image = self.UI[self.current_sprite]
        self.rect = self.image.get_rect(center=[pos_x, pos_y])

# Gem count
    def gem_count(self):

        # Gets ones and tens digit. From gem count get tens and ones using division. Set image accordingly
        for number in UI_Digit_group:
            if number.rect.x == 443:
                gem_double_digit = (gem_count // 10) % 10
                number.image = self.UI[gem_double_digit]
            if number.rect.x == 470:
                gem_single_digit = gem_count % 10
                number.image = self.UI[gem_single_digit]

# Level count
    def level_count(self):

        # Get level count sprite and set the image to the current level
        for number in UI_Digit_group:
            if number.rect.x == 398:
                number.image = self.UI[level]

# Update
    def update(self):

        # Run each UI Digit method
        self.gem_count()
        self.level_count()

# UI Class
class UI(pygame.sprite.Sprite):

# Init
    def __init__(self, pos_x, pos_y, UI_type):
        super().__init__()

        # Globals
        global difficulty

        # Set all buttons hover state to false
        self.button_hover_states = {}
        for button in UI_group:
            self.button_hover_states[button] = False

        # Import buttons normal and hover states
        self.button_normal_arr = [pygame.image.load(f"Assets\\UI\\text\\UI_buttons\\normal-{i}.png") for i in range(1, 12)]
        self.button_selected_arr = [pygame.image.load(f"Assets\\UI\\text\\UI_buttons\\selected-{i}.png") for i in range(1, 12)]

        # Import difficulty normal and hover states
        self.difficulty = [pygame.image.load(f"Assets\\UI\\text\\UI_buttons\\diff-{i}.png") for i in range(1, 3)]

        # Get Rect off image unless button is difficulty in which use difficulty images
        if UI_type != 12:
            self.image = self.button_normal_arr[UI_type]
            self.rect = self.image.get_rect(center=(pos_x,pos_y))
        else:   
            self.image = self.difficulty[difficulty]
            self.rect = self.image.get_rect(center=(pos_x,pos_y))

# Hover
    def hover(self):
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Excluded y values
        excluded_y_values = [116, 191, 266, 341]

        # Iterate through each button
        for button in UI_group:

            # Get restart button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 340:
                button.image = pygame.transform.scale(self.button_normal_arr[0],(273,44))
                button.rect.x = 272
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[0],(273*1.2,44*1.2))
                    button.rect.x = 242

            # Get main menu button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 415:
                button.image = pygame.transform.scale(self.button_normal_arr[1],(330,44))
                button.rect.x = 243
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[1],(330*1.2,44*1.2))
                    button.rect.x = 213

            # Get play button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 168:
                button.image = pygame.transform.scale(self.button_normal_arr[2],(171,48))
                button.rect.x = 323
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[2],(171*1.2,48*1.2))
                    button.rect.x = 305
            
            # Get settings button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 218:
                button.image = pygame.transform.scale(self.button_normal_arr[3],(318,48))
                button.rect.x = 249
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[3],(318*1.2,48*1.2))
                    button.rect.x = 225

            # Get quit button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 268:
                button.image = pygame.transform.scale(self.button_normal_arr[8],(160,48))
                button.rect.x = 328
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[8],(160*1.2,48*1.2))
                    button.rect.x = 315

            # Depending on music state is on or off set image accordingly
            if button.rect.y == 116:
                if music_state:
                    button.image = self.button_normal_arr[4]
                else:
                    button.image = self.button_selected_arr[4]

            # Depending on SFX state is on or off set image accordingly
            if button.rect.y == 191:
                if SFX_state:
                    button.image = self.button_normal_arr[5]
                else:
                    button.image = self.button_selected_arr[5]

            # Depending on trees state is on or off set image accordingly
            if button.rect.y == 266:
                if Trees_state:
                    button.image = self.button_normal_arr[6]
                else:
                    button.image = self.button_selected_arr[6]

            # Get credits back button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 575:
                button.image = pygame.transform.scale(self.button_normal_arr[7],(139,41))
                button.rect.x = 16
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[7],(139*1.2,41*1.2))
                    button.rect.x = 7
            
            # Get settings back button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 9:
                button.image = pygame.transform.scale(self.button_normal_arr[7],(139,41))
                button.rect.x = 16
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[7],(139*1.2,41*1.2))
                    button.rect.x = 7

            # Get credits button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 14:
                button.image = pygame.transform.scale(self.button_normal_arr[9],(144,23))
                button.rect.x = 658
                if button.rect.collidepoint(mouse_pos):
                    print("pluh")
                    button.image = pygame.transform.scale(self.button_selected_arr[9],(144*1.2,23*1.2))
                    button.rect.x = 643

            # Get level exit button, when mouse is not hovered keep default scale and image
            # When mouse hovered change scale and image
            if button.rect.y == 6:
                button.image = pygame.transform.scale(self.button_normal_arr[10],(25,36))
                if button.rect.collidepoint(mouse_pos):
                    button.image = pygame.transform.scale(self.button_selected_arr[10],(25*1.2,36*1.2))

            # If SFX is enabled
            if SFX_state:

                # Skip the buttons with excluded Y values
                if button.rect.y in excluded_y_values:
                    continue
                
                # If mouse is hovering on button init SFX
                if button.rect.collidepoint(mouse_pos):
                    if not self.button_hover_states.get(button, False):

                        # Play hover SFX
                        self.button_hover_states[button] = True
                        hover_SFX.set_volume(0.4)
                        hover_SFX.play()
                else:
                        # SFX has init
                        self.button_hover_states[button] = False

# Statechange
    def statechange_init(self):
        # Globals
        global mouse_down, l_pressed, r_pressed

        # Play click SFX
        if SFX_state:
            press_SFX.set_volume(1.0)
            press_SFX.play()

        # Reset inputs and kill sprites
        mouse_down = False
        l_pressed = False
        r_pressed = False
        for button in UI_group:
            button.kill()
        for gem in gem_group:
            gem.kill()
        for enemy in enemy_group:
            enemy.kill()
        for terrain in terrain_group:
            terrain.kill()
            space.remove(terrain.body, terrain.shape)

    def button_logic(self):
        # Globals
        global mouse_down, state, player_group, credits_init, level1_init, level2_init, level3_init, mainmenu_init, settings_init, gem_count, music_state, SFX_state, Trees_state, delevel, level, level_unlock1, level_unlock2, level_unlock3, difficulty, music_init

        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Iterate through buttons
        for button in UI_group:

            # Get restart button, when clicked: Init all levels and level variables, change state, and call statechange
            if button.rect.y == 340 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "Level1"
                music_init = False
                self.statechange_init()
                delevel = False
                level1_init = False
                level2_init = False
                level3_init = False
                gem_count = 0
                level = 1
                level_unlock1 = False
                level_unlock2 = False
                level_unlock3 = False

            # Get MainMenu button, when clicked: Init all levels and level variables, change state, and call statechange
            if button.rect.y == 415 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "MainMenu"
                self.statechange_init()
                mainmenu_init = False
                level1_init = False
                level2_init = False
                level3_init = False
                gem_count = 0
                level = 1
                delevel = False
                music_init = False

            # Get Play button, when clicked: Init all levels and level variables, change state, and call statechange            
            if button.rect.y == 168 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "Level1"
                self.statechange_init()
                level1_init = False
                level2_init = False
                level3_init = False
                delevel = False
                gem_count = 0
                music_init = False
                level_unlock1 = False
                level_unlock2 = False
                level_unlock3 = False

            # Get Settings button, when clicked: Change state, and call statechange
            if button.rect.y == 218 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "Settings"
                self.statechange_init()
                settings_init = False
            
            # Get music state button, when clicked: Toggle music, and play click SFX
            if button.rect.y == 116 and button.rect.collidepoint(mouse_pos) and mouse_down:
                music_state = not music_state
                music_init = False
                mouse_down = False
                if SFX_state:
                    press_SFX.set_volume(1.0)
                    press_SFX.play()

            # Get SFX state button, when clicked: Toggle SFX, and play click SFX
            if button.rect.y == 191 and button.rect.collidepoint(mouse_pos) and mouse_down:
                SFX_state = not SFX_state
                mouse_down = False
                if SFX_state:
                    press_SFX.set_volume(1.0)
                    press_SFX.play()
            
            # Get trees state button, when clicked: Toggle trees, and play click SFX
            if button.rect.y == 266 and button.rect.collidepoint(mouse_pos) and mouse_down:
                Trees_state = not Trees_state
                mouse_down = False
                if SFX_state:
                    press_SFX.set_volume(1.0)
                    press_SFX.play()

            # Get credits back button, when clicked: Change state and call statechange
            if button.rect.y == 575 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "MainMenu"
                self.statechange_init()
                mainmenu_init = False

            # Get settings back button, when clicked: Change state and call statechange
            if button.rect.y == 9 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "MainMenu"
                self.statechange_init()
                mainmenu_init = False

            # Get quit button, when clicked: Quit game
            if button.rect.y == 268 and button.rect.collidepoint(mouse_pos) and mouse_down:
                pygame.quit()
                sys.exit()

            # Get credits button, when clicked: Change state and call statechange
            if button.rect.y == 14 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "Credits"
                self.statechange_init()
                credits_init = False

            # Get level exit button, when clicked: Change state, call statechange and un-init all levels
            if button.rect.y == 6 and button.rect.collidepoint(mouse_pos) and mouse_down:
                state = "MainMenu"
                self.statechange_init()
                mainmenu_init = False
                delevel = False
                gem_count = 0
                level = 1
                level1_init = False
                level2_init = False
                level_unlock1 = False
                level_unlock2 = False
                level_unlock3 = False
                music_init = False

            # Get level state button, when clicked: Change difficulty, and play button SFX
            if button.rect.y == 341 and button.rect.collidepoint(mouse_pos) and mouse_down:
                difficulty += 1
                if difficulty == 2:
                    difficulty = 0

                button.image = self.difficulty[difficulty]
                mouse_down = False
                if SFX_state:
                    press_SFX.set_volume(1.0)
                    press_SFX.play()
        
    def update(self):

        # Call UI methods each frame
        self.hover()
        self.button_logic()

# Game and Physics Init
pygame.init()
game_state = GameState()
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity=(0,1000)

# Screen Init
screen_flags = pygame.NOFRAME
screen_width = BLOCK_DIMENSIONS * SCREEN_BLOCK_WIDTH
screen_height = BLOCK_DIMENSIONS * SCREEN_BLOCK_HEIGHT
screen = pygame.display.set_mode((screen_width,screen_height), flags=screen_flags)

# Import Skyboxes
skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox.png")
death_skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox_death.png")
main_menu_skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox_main_menu.png")
settings_skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox_settings.png")
credits_skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox_credits.png")
loading_skybox = pygame.image.load("Assets\\Enviroment\\Other\\skybox_loading.png")

# Import Gem text and trees
gem_text = pygame.transform.scale(pygame.image.load("Assets\\UI\\text\\gem_text.png"), (49*2,8*2))
trees = pygame.image.load("Assets\\Enviroment\\Other\\trees.png")
trees = pygame.transform.scale(trees,(528*2,110*2))

# Group init
player_group = pygame.sprite.GroupSingle()
terrain_group = pygame.sprite.Group()
gem_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
UI_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()

# Import music
main_menu_music = pygame.mixer.Sound("Assets\\Sound\\Music\\Main_Menu_music.mp3")
game_music = pygame.mixer.Sound("Assets\\Sound\\Music\\Game_music.mp3")

# Import SFX
hover_SFX = pygame.mixer.Sound("Assets\\Sound\\SFX\\hover.mp3")
press_SFX = pygame.mixer.Sound("Assets\\Sound\\SFX\\press.mp3")
gem_SFX = pygame.mixer.Sound("Assets\\Sound\\SFX\\gem.mp3")
death_SFX = pygame.mixer.Sound("Assets\\Sound\\SFX\\death.mp3")
grass_SFX = [pygame.mixer.Sound("Assets\\Sound\\SFX\\grass1.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\grass2.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\grass3.mp3"), pygame.mixer.Sound("Assets\\Sound\\SFX\\grass4.mp3")]
stone_SFX = [pygame.mixer.Sound("Assets\\Sound\\SFX\\stone1.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\stone2.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\stone3.mp3"), pygame.mixer.Sound("Assets\\Sound\\SFX\\stone4.mp3")]
snow_SFX = [pygame.mixer.Sound("Assets\\Sound\\SFX\\snow1.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\snow2.mp3"),pygame.mixer.Sound("Assets\\Sound\\SFX\\snow3.mp3"), pygame.mixer.Sound("Assets\\Sound\\SFX\\snow4.mp3")]

# Game UI init
UI_Digit_group = pygame.sprite.Group()
UI_Digit_group.add(UI_Digits(screen_width/2+45, 18))  # Tens Digit
UI_Digit_group.add(UI_Digits(screen_width/2+72, 18))  # Ones Digit
UI_Digit_group.add(UI_Digits(screen_width/2, 36))  # Level Count

# FOR DEBUG (!DONT TOUCH!)
debug_draw_options = pymunk.pygame_util.DrawOptions(screen)

# Main loop: start timer, init music and SFX handlers and run game_state manager
while True:
    music_handler()
    SFX_handler()
    timer += 1/60
    game_state.state_manager()
    clock.tick(60)
    space.step(1/60)
