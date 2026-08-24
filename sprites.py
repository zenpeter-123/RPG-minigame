import pygame
from config import *
import math
import random
from utils import resource_path

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(resource_path(file)).convert_alpha()
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width,height], pygame.SRCALPHA) #empty surface where we are going to blit the sprite
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        return sprite

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE

        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        # --- STATS ---
        self.name = ""
        self.hp = 20
        self.max_hp = 20
        self.atk = PLAYER_DAMAGE
        self.level = 1
        self.gold = 0
        self.xp = 0
        self.xp_to_next_level = XP_PER_LEVEL.get(1, 10)
        self.alive = True
        self.inventory = {
            "potion": 1,
            "elixir": 1,
            "key": 1,
            "chest": 1,
            "equipment": {
                "weapon": None,
                "armor": None,
                "shield": None,
            },
        }
        self.max_inventory_size = 10
        self.speed = PLAYER_SPEED

        # --- MOVEMENT AND DIRECTION ---
        self.can_move_left = True
        self.can_move_right = True
        self.can_move_up = True
        self.can_move_down = True

        self.level_just_upgraded = False
        self.prev_level = self.level

        self.facing = 'down'
        self.animation_loop = 1

        self.hit_flash = False
        self.hit_flash_time = 0
        self.hit_flash_duration = 100

        # --- SPRITE-SHEETs ---
        self.body_sheet = self.game.player_body_spritesheet
        self.head_sheet = self.game.player_head_spritesheet
        self.sword_carry_frames = self.game.sword_carry_frames

        # --- COOLDOWN ---
        self.hit_cooldown = 1000
        self.last_hit_time = 0

        # --- HEALTH BAR ---
        self.hp_bar_offset_y = HP_BAR_OFFSET_Y
        self.hp_bar_width = TILESIZE
        self.hp_bar_height = math.floor(TILESIZE / 8)

        # --- ATTACKING ---
        self.attacking = False
        self.attack_start_time = 0
        self.attack_duration = 400

        # --- KNOCKBACK ---
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_duration = 100
        self.knockback_start_time = 0
        self.is_knocked = False

        # --- RECT (32x32 COLLISION AREA) ---
        self.rect = pygame.Rect(self.x, self.y, TILESIZE, TILESIZE)

        # --- IMAGE-CACHE (with `attacking` state) ---
        self.composed_frames = {}
        self.frame_offsets = {}
        for direction in ROW_FOR_DIRECTION:
            for pose in (POSE_IDLE, POSE_WALK):
                for attacking in (False, True):  # <- KÉT ÁLLAPOT!
                    frame, offset = self._compose_full_frame(direction, pose, attacking)
                    self.composed_frames[(direction, pose, attacking)] = frame
                    self.frame_offsets[(direction, pose, attacking)] = offset

        # --- INITIAL IMAGE ---
        self.image = self.composed_frames[('down', POSE_IDLE, False)]

        # --- DRAWING RECT SETUP ---
        self._sync_draw_rect()

    def _compose_full_frame(self, direction, pose_col, attacking):
        row = ROW_FOR_DIRECTION[direction]
        body_frame = self.body_sheet.get_sprite(pose_col * TILE_W, row * BODY_H, TILE_W, BODY_H)
        head_frame = self.head_sheet.get_sprite(pose_col * TILE_W, row * HEAD_H, TILE_W, HEAD_H)

        # --- WHEN ATTACKING HIDE THE SWORD ---
        if attacking:
            # When attacking, there is no sword, but there is an empty 32x32 Surface
            sword_frame = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            offset_x, offset_y = 0, 0
            # When attacking, the combined image size is TILESIZE x TILESIZE
            combined = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        else:
            variant = IDLE_SWORD_VARIANT_FOR_FACING[direction]
            sword_frame = self.sword_carry_frames[variant]
            offset_x, offset_y = SWORD_OFFSET_FOR_VARIANT[variant]
            # In non-attacking state, the combined image size is based on the sword frame
            combined = pygame.Surface(sword_frame.get_size(), pygame.SRCALPHA)
        
        layers = {
            'body': (body_frame, (offset_x, offset_y + HEAD_H)),
            'head': (head_frame, (offset_x, offset_y)),
            'sword': (sword_frame, (0, 0)),
        }

        # --- Layer Order ---
        if attacking:
            order = ['body', 'head', 'sword']  # Attacking: body -> head -> sword
        else:
            order = ['body', 'sword', 'head']  # Normal: body -> sword -> head

        for name in order:
            img, pos = layers[name]
            combined.blit(img, pos)

        # return the combined image and the offset for positioning
        return combined, (offset_x, offset_y)

    def _sync_draw_rect(self):
        # A rect pozíciója a karakter pozíciója
        self.rect.x = self.x
        self.rect.y = self.y
        
        # If the image is big, adjust the rect to be centered at the bottom of the image
        if self.image and (self.image.get_width() > TILESIZE or self.image.get_height() > TILESIZE):
            self.rect.centerx = self.x + TILESIZE // 2
            self.rect.bottom = self.y + TILESIZE

    def update(self):
        if self.attacking:
            now = pygame.time.get_ticks()
            if now - self.attack_start_time > self.attack_duration:
                self.attacking = False

        # --- KNOCKBACK ---
        if self.is_knocked:
            now = pygame.time.get_ticks()
            if now - self.knockback_start_time < self.knockback_duration:
                self.x += self.knockback_x
                self.y += self.knockback_y
                self.knockback_x *= 0.9
                self.knockback_y *= 0.9
                self._sync_draw_rect()
                return  # Left when knockback is active, skip other movements
            else:
                self.is_knocked = False
                self.knockback_x = 0
                self.knockback_y = 0

        # --- HIT FLASH HANDLING (EXACTLY HERE) ---
        if self.hit_flash:
            now = pygame.time.get_ticks()
            if now - self.hit_flash_time < self.hit_flash_duration:
                # Lighter image
                flash_image = self.image.copy()
                flash_image.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGB_ADD)
                self.image = flash_image
            else:
                self.hit_flash = False
                # Restore the original image
                moving = (self.x_change != 0 or self.y_change != 0)
                pose = POSE_WALK if moving else POSE_IDLE
                self.image = self.composed_frames[(self.facing, pose, self.attacking)]

        self.movement()
        self.animate()
        self.collide_enemy()

        self.x += self.x_change
        self.y += self.y_change
        self._sync_draw_rect()
        self.collide_blocks()

        self.x_change = 0
        self.y_change = 0


    def movement(self):
        if self.attacking:
            return

        dx, dy = self.get_direction()
        ratio = math.sqrt(2) / 2

        if dx == -1 and dy == 0 and self.can_move_left:
            self.x_change -= self.speed
            self.facing = 'left'
        elif dx == 1 and dy == 0 and self.can_move_right:
            self.x_change += self.speed
            self.facing = 'right'
        elif dx == 0 and dy == -1 and self.can_move_up:
            self.y_change -= self.speed
            self.facing = 'up'
        elif dx == 0 and dy == 1 and self.can_move_down:
            self.y_change += self.speed
            self.facing = 'down'
        elif dx == 1 and dy == -1 and self.can_move_right and self.can_move_up:
            self.y_change -= ratio * self.speed
            self.x_change += ratio * self.speed
            self.facing = 'right'
        elif dx == 1 and dy == 1 and self.can_move_right and self.can_move_down:
            self.y_change += ratio * self.speed
            self.x_change += ratio * self.speed
            self.facing = 'right'
        elif dx == -1 and dy == -1 and self.can_move_left and self.can_move_up:
            self.y_change -= ratio * self.speed
            self.x_change -= ratio * self.speed
            self.facing = 'left'
        elif dx == -1 and dy == 1 and self.can_move_left and self.can_move_down:
            self.y_change += ratio * self.speed
            self.x_change -= ratio * self.speed
            self.facing = 'left'

    def collide_enemy(self):
        now = pygame.time.get_ticks()
        if now - self.last_hit_time < self.hit_cooldown:
            return
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            for enemy in hits:
                if hasattr(enemy, 'hitable') and enemy.hitable:
                    # Damage the player and start the hit cooldown
                    self.hp -= ENEMY_DAMAGE
                    self.last_hit_time = now
                    self.hit_flash = True
                    self.hit_flash_time = now
                    
                    # --- KNOCKBACK ---
                    # Compute the direction from the enemy to the player
                    dx = self.rect.centerx - enemy.rect.centerx
                    dy = self.rect.centery - enemy.rect.centery
                    distance = math.sqrt(dx**2 + dy**2)
                    
                    if distance > 0:
                        # Normalize and set the knockback power
                        knockback_power = 10  # Power, you can adjust this
                        self.knockback_x = (dx / distance) * knockback_power
                        self.knockback_y = (dy / distance) * knockback_power
                        self.is_knocked = True
                        self.knockback_start_time = now
                    
                    if self.hp <= 0:
                        self.hp = 0
                        self.alive = False
                        self.kill()
                        self.game.playing = False
                        print("You have been killed by an enemy!")

    def draw_health_bar(self, camera_x, camera_y):
        bar_x = self.rect.x - camera_x
        bar_y = self.rect.y - camera_y + self.hp_bar_offset_y

        hp_ratio = self.hp / self.max_hp
        current_width = self.hp_bar_width * hp_ratio

        if hp_ratio > 0.6:
            color = 'green'
        elif hp_ratio > 0.3:
            color = 'yellow'
        else:
            color = 'red'

        bg_rect = pygame.Rect(bar_x, bar_y, self.hp_bar_width, self.hp_bar_height)
        pygame.draw.rect(self.game.screen, 'grey', bg_rect)

        hp_rect = pygame.Rect(bar_x, bar_y, current_width, self.hp_bar_height)
        pygame.draw.rect(self.game.screen, color, hp_rect)

    def collide_blocks(self):
        dx, dy = self.get_direction()

        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True

        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)

        if hits:
            if dx == 1 and dy == 0:
                self.can_move_right = False
            elif dx == -1 and dy == 0:
                self.can_move_left = False
            elif dx == 0 and dy == 1:
                self.can_move_down = False
            elif dx == 0 and dy == -1:
                self.can_move_up = False
            elif dx == 1 and dy == -1:
                self.can_move_right = False
                self.can_move_up = False
            elif dx == 1 and dy == 1:
                self.can_move_right = False
                self.can_move_down = False
            elif dx == -1 and dy == -1:
                self.can_move_left = False
                self.can_move_up = False
            elif dx == -1 and dy == 1:
                self.can_move_left = False
                self.can_move_down = False

    def get_direction(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        return dx, dy

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.xp_to_next_level = XP_PER_LEVEL.get(self.level, 10)

            self.level_just_upgraded = True

            self.game.add_message(f"You reached level {self.level}. The Sphinx may appear...", (255, 215, 0))

        if self.level >= 10:
            self.game.win()

    def add_item(self, item_name, quantity):
        self.item_name = item_name
        self.quantity = quantity
        if self.item_name in self.inventory:
            if isinstance(self.inventory[self.item_name], int):
                self.inventory[self.item_name] += self.quantity
            else:
                self.inventory[self.item_name] = self.quantity
        else:
            self.inventory[self.item_name] = self.quantity

    def use_potion(self):
        if self.inventory.get("potion", 0) > 0:
            self.inventory["potion"] -= 1
            self.hp = min(self.max_hp, self.hp + POTION_HEALING)
        else:
            return False

    def use_elixir(self):
        if self.inventory.get("elixir", 0) > 0:
            self.inventory["elixir"] -= 1
            self.hp = self.max_hp
        else:
            return False

    def use_chest(self):

        if self.inventory.get("chest", 0) > 0:

            if self.inventory.get("key", 0) > 0:
                    
                self.inventory["chest"] -= 1
                self.inventory["key"] -= 1

                for _ in range(3):

                    loot_type = random.choice(['gold', 'potion', 'elixir', 'key', 'xp'])
                    
                    if loot_type == 'gold':
                        gold = random.randint(20, 50) * self.level // 3
                        self.gold += gold
                        self.game.add_message(f"📦 +{gold} gold!", (255, 215, 0))
                    elif loot_type == 'potion':
                        self.add_item("potion", 1)
                        self.game.add_message(f"📦 +1 potion!", (100, 255, 100))
                    elif loot_type == 'elixir':
                        self.add_item("elixir", 1)
                        self.game.add_message(f"📦 +1 elixir!", (100, 200, 255))
                    elif loot_type == 'key':
                        self.add_item("key", 1)
                        self.game.add_message(f"📦 +1 key!", (255, 215, 0))
                    elif loot_type == 'xp':
                        xp_gain = random.randint(30, 50) * self.level / 2
                        self.gain_xp(xp_gain)
                        self.game.add_message(f"📦 +{xp_gain} XP!", (100, 200, 255))
                return True

            else:
                self.game.add_message("You don't have any key to open this chest!", (255, 100, 100))
        else:
            self.game.add_message("You don't have any chest!", (255, 100, 100))
            return False


    def animate(self):
        moving = (self.x_change != 0 or self.y_change != 0)
        pose = POSE_WALK if moving else POSE_IDLE
        self.image, _ = self._compose_full_frame(self.facing, pose, self.attacking)
        # It is neccessary to call _sync_draw_rect() after updating the image to ensure 
        # the rect is correctly positioned based on the new image size.
        self._sync_draw_rect()

    def get_center(self):
        self.x_center = self.rect.x + TILESIZE / 2
        self.y_center = self.rect.y + TILESIZE / 2
        return self.x_center, self.y_center

class Enemy (pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.hp_bar_width = TILESIZE
        self.hp_bar_height = math.floor(TILESIZE/8)
        self.hp_bar_offset_y = HP_BAR_OFFSET_Y

        self.x_change = 0
        self.y_change = 0

        self.facing = random.choice(['left', 'right'])
        self.animation_loop = 1
        self.movement_loop = 0
        self.max_travel = random.randint(7,30) #old feasure, random movement distance before changing direction

        self.image = self.game.enemy_spritesheet.get_sprite(0, 0, self.width, self.height)
        self.image.set_colorkey('black')

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.base_max_hp = ENEMY_HP
        self.max_hp = self.calculate_max_hp()
        self.hp = self.max_hp

        self.spawn_delay = random.randint(3000, 6000)
        self.hitable = True
        self.is_dead = False
        self.spawn_radius = NEW_ENEMY_SPAWN_RADIUS
        self.vision_range = 200
        self.attack_range = 40
        self.state = "idle"
        self.origin_x = x * TILESIZE
        self.origin_y = y * TILESIZE

        self.fire = Fire(self.game, self)

        self.attack_cooldown = 0
        self.attack_cooldown_time = 1000

        self.base_speed = ENEMY_SPEED

        self.speed = self.calculate_speed()

        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_duration = 150  # Longer than the player's
        self.knockback_start_time = 0
        self.is_knocked = False

        self.can_move_left = True
        self.can_move_right = True
        self.can_move_up = True
        self.can_move_down = True

        self.path = []
        self.path_index = 0
        self.path_update_timer = 0
        self.path_update_interval = 30
        self.last_known_position = (0,0)
        self.last_seen_time = 0
        self.memory_time = 5000

        self.mix_factor = 0.7
        self.direction_change_timer = 0
        self.direction_change_interval = 60
        self.stored_random_dx = 0
        self.stored_random_dy = 0

        self.small_fires = []
        
        for i in range(3): 
            angle = i * 2.094  # 0°, 120°, 240°
            radius = 20 + i * 5 * (1.05 ** self.game.player.level)  # 20, 25, 30 pixel distance
            speed = 0.02 + i * 0.005 * self.game.player.level

            small_fire = SmallFire(
                self.game,
                self, 
                angle=angle,
                radius=radius,
                speed=speed
            )
            self.small_fires.append(small_fire)


        self.down_animations = [self.game.enemy_spritesheet.get_sprite(3, 2, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 2, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 2, self.width, self.height)]

        self.up_animations = [self.game.enemy_spritesheet.get_sprite(3, 34, self.width, self.height),
                         self.game.enemy_spritesheet.get_sprite(35, 34, self.width, self.height),
                         self.game.enemy_spritesheet.get_sprite(68, 34, self.width, self.height)]

        self.left_animations = [self.game.enemy_spritesheet.get_sprite(3, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(35, 98, self.width, self.height),
                           self.game.enemy_spritesheet.get_sprite(68, 98, self.width, self.height)]

        self.right_animations = [self.game.enemy_spritesheet.get_sprite(3, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(35, 66, self.width, self.height),
                            self.game.enemy_spritesheet.get_sprite(68, 66, self.width, self.height)]
    
    def calculate_speed(self):

        if self.game.player is None:
            return self.base_speed
        
        player_level = self.game.player.level

        if player_level >= 5:

            levels_above_5 = player_level - 5

            multiplier = 1.1 ** levels_above_5
            return self.base_speed * multiplier
        else:
            return self.base_speed
        
    def calculate_max_hp(self):

        if self.game.player is None:
            return self.base_max_hp
        
        player_level = self.game.player.level

        if player_level >= 5:

            levels_above_5 = player_level - 5

            multiplier = 1.1 ** levels_above_5
            return self.base_max_hp * multiplier
        else:
            return self.base_max_hp
    
    
    def collide_blocks(self):
        dx, dy = self.get_direction()

        self.can_move_up = True
        self.can_move_down = True
        self.can_move_left = True
        self.can_move_right = True

        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        
        if hits:
            if dx == 1 and dy == 0:
                self.can_move_right = False
            elif dx == -1 and dy == 0:
                self.can_move_left = False
            elif dx == 0 and dy == 1:
                self.can_move_down = False
            elif dx == 0 and dy == -1:
                self.can_move_up = False
            elif dx == 1 and dy == -1:
                self.can_move_right = False
                self.can_move_up = False
            elif dx == 1 and dy == 1:
                self.can_move_right = False
                self.can_move_down = False
            elif dx == -1 and dy == -1:
                self.can_move_left = False
                self.can_move_up = False
            elif dx == -1 and dy == 1:
                self.can_move_left = False
                self.can_move_down = False
        else:
    
            self.can_move_up = True
            self.can_move_down = True
            self.can_move_left = True
            self.can_move_right = True
    
    def take_damage(self, damage): #boolean function

        self.damage = damage
        self.hp -= self.damage

        if self.hp <= 0:
            self.death_time = pygame.time.get_ticks()
            self.is_dead = True
            self.hitable = False
            self.image.set_alpha(0) #vanish the image
            return self.is_dead
        else:
            return False
        
        
    def generate_new_enemys_coordinates(self):

            center_x = self.game.tiled_map.width // 2
            center_y = self.game.tiled_map.height // 2

            max_attempts = 100
            attempts = 0

            # Safeguard: If no valid position is found after max_attempts, return the center of the map
            fallback_tile_x, fallback_tile_y = self.game.tiled_map.find_center_walkable()

            while attempts < max_attempts:
                attempts += 1
                
                offset_x = random.randint(-self.spawn_radius, self.spawn_radius)
                offset_y = random.randint(-self.spawn_radius, self.spawn_radius)
                
                temp_x = center_x + offset_x
                temp_y = center_y + offset_y


                if 0 <= temp_x < self.game.tiled_map.width and 0 <= temp_y < self.game.tiled_map.height:
                    
                    if self.is_walkable(temp_x, temp_y):

                        return temp_x, temp_y

            return fallback_tile_x, fallback_tile_y
    
    def draw_attack_range(self, camera_x, camera_y):
        """Draws the attack range and vision range of the enemy"""
        center_x = self.rect.centerx - camera_x
        center_y = self.rect.centery - camera_y
        
        pygame.draw.circle(self.game.screen, (255, 0, 0, 50), (center_x, center_y), self.attack_range, 1)
        
        pygame.draw.circle(self.game.screen, (0, 255, 0, 30), (center_x, center_y), self.vision_range, 1)
    

    def draw_health_bar(self, camera_x, camera_y):

        if self.is_dead:
            pass
        else:

            bar_x = self.rect.x - camera_x
            bar_y = self.rect.y - camera_y + self.hp_bar_offset_y

            hp_ratio = self.hp / self.max_hp

            current_width = self.hp_bar_width * hp_ratio

            if hp_ratio > 0.6:
                color = 'green'
            elif hp_ratio > 0.3:
                color = 'yellow'
            else:
                color = 'red'

            bg_rect = pygame.Rect(bar_x, bar_y, self.hp_bar_width, self.hp_bar_height)
            pygame.draw.rect(self.game.screen, 'grey', bg_rect)

            hp_rect = pygame.Rect(bar_x, bar_y, current_width, self.hp_bar_height)
            pygame.draw.rect(self.game.screen, color, hp_rect) 

    def update(self):
        if self.is_dead:
            self.fire.kill()
            for fire in self.small_fires:
                fire.kill()

            now = pygame.time.get_ticks()
            if now - self.death_time > self.spawn_delay:
                new_x, new_y = self.generate_new_enemys_coordinates()
                print(self.generate_new_enemys_coordinates())
                self.game.enemy = Enemy(self.game, new_x, new_y)
                print(f"New enemy has spawned at {new_x, new_y} coordinates")
                self.is_dead = False
                self.kill()
            return

        # --- KNOCKBACK (ENEMY) ---
        if self.is_knocked:
            now = pygame.time.get_ticks()
            if now - self.knockback_start_time < self.knockback_duration:
                self.rect.x += self.knockback_x
                self.rect.y += self.knockback_y
                self.knockback_x *= 0.9  # Slowly reduce the knockback over time for a smoother effect
                self.knockback_y *= 0.9
                return  # Don't process other movements while knocked back
            else:
                self.is_knocked = False
                self.knockback_x = 0
                self.knockback_y = 0

        self.ai_update()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.state != "attacking":
            self.rect.x += self.x_change
            self.rect.y += self.y_change
            self.collide_blocks()
            self.animate()
            self.x_change = 0
            self.y_change = 0
            self.follow_path()
            self.movement()


    def has_line_of_sight(self, x1, y1, x2, y2):

        x1_tile = int(x1 // TILESIZE)
        y1_tile = int(y1 // TILESIZE)
        x2_tile = int(x2 // TILESIZE)
        y2_tile = int(y2 // TILESIZE)

        # Bresenham line algorithm
        dx = abs(x2_tile - x1_tile)
        dy = abs(y2_tile - y1_tile)
        sx = 1 if x1_tile < x2_tile else -1
        sy = 1 if y1_tile < y2_tile else -1
        err = dx - dy

        x = x1_tile
        y = y1_tile

        while True:
            # If the tile is not walkable then there is no line of sight
            if not self.is_walkable(x, y):
                return False

            if x == x2_tile and y == y2_tile:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

        return True


    def is_walkable(self, x, y):

        if x < 0 or x >= self.game.tiled_map.width or y < 0 or y >= self.game.tiled_map.height:
            return False
            
        gid = self.game.tiled_map.gid_at(x, y)

        if gid == 14 or gid == 0:
            return False
            
        return True

    def can_diagonal_move(self, x, y, dx, dy):

        nx = x + dx
        ny = y + dy

        return (self.is_walkable(x,y) and 
        self.is_walkable(nx, ny) and 
        self.is_walkable(nx, y) and 
        self.is_walkable(x, ny))


    def bfs_path(self, start_x, start_y, target_x, target_y, max_distance=200):

            map_width = self.game.tiled_map.width
            map_height = self.game.tiled_map.height
            
            if not (0 <= start_y < map_height and 0 <= start_x < map_width):
                return None
            if not (0 <= target_y < map_height and 0 <= target_x < map_width):
                return None

            if start_x == target_x and start_y == target_y:
                return [(start_x, start_y)]

            from collections import deque
            queue = deque()
            queue.append((start_x, start_y))

            visited = set()
            visited.add((start_x, start_y))
            parent = {}

            directions = [
                (0, -1), (0, 1), (-1, 0), (1, 0),
                (-1, -1), (1, -1), (-1, 1), (1, 1)
            ]

            max_tile_distance = max_distance // TILESIZE

            while queue:
                x, y = queue.popleft()

                if (x, y) == (target_x, target_y):
                    path = []
                    current = (x, y)
                    while current != (start_x, start_y):
                        path.append(current)
                        current = parent[current]
                    path.append((start_x, start_y))
                    path.reverse()
                    return path

                for c in directions:
                    dx = c[0]
                    dy = c[1]

                    if 0 <= y < map_height and 0 <= y + dy < map_height: 
                        ny = y + dy
                    else:
                        continue
                    
                    if 0 <= x < map_width and 0 <= x + dx < map_width:
                        nx = x + dx
                    else:
                        continue

                    if not self.is_walkable(nx, ny):
                        continue

                    if dx != 0 and dy != 0:
                        if self.game.tiled_map.gid_at(nx, y) == 14 or self.game.tiled_map.gid_at(x, ny) == 14:
                            continue

                    distance_from_start = abs(nx - start_x) + abs(ny - start_y)
                    if distance_from_start > max_tile_distance:
                        continue

                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (x, y)
                        queue.append((nx, ny))

            return None
    
    def follow_path(self):

        if self.state == "idle":

            dx = self.origin_x - self.rect.x
            dy = self.origin_y - self.rect.y
            distance_to_origin = math.sqrt(dx**2 + dy**2)


            self.path = self.bfs_path(int(math.floor(self.x_center//TILESIZE)), 
                                      int(math.floor(self.y_center//TILESIZE)), 
                                      int(math.floor(self.origin_x//TILESIZE)), 
                                      int(math.floor(self.origin_y//TILESIZE)))

            if distance_to_origin > 5:
                dx = dx/distance_to_origin
                dy = dy/distance_to_origin
                self.x_change = dx * ENEMY_SPEED
                self.y_change = dy * ENEMY_SPEED

                if abs(dx) > abs(dy):
                    self.facing = 'right' if dx > 0 else 'left'
                else:
                    self.facing = 'down' if dy > 0 else 'up'

            else:
                self.x_change = 0
                self.y_change = 0

        if self.state == "chasing" or self.state == "searching":
            
            if self.path and self.path_index < len(self.path):

                target_x, target_y = self.path[self.path_index]
                target_pixel_x = target_x * TILESIZE + TILESIZE // 2
                target_pixel_y = target_y * TILESIZE + TILESIZE // 2

                dx = target_pixel_x - self.rect.centerx
                dy = target_pixel_y - self.rect.centery
                distance = math.sqrt(dx**2 + dy**2)

                if distance < 5:
                    self.path_index += 1
                    return

                if distance > 0:
                    dx = dx / distance
                    dy = dy / distance

                self.direction_change_timer += 1
                if self.direction_change_timer >= self.direction_change_interval:
                    self.direction_change_timer = 0

                    target_angle = math.atan2(dy, dx)
                    max_deviation = math.radians(45)
                    random_offset = random.uniform(-max_deviation, max_deviation)
                    random_angle = target_angle + random_offset

                    self.stored_random_dx = math.cos(random_angle)
                    self.stored_random_dy = math.sin(random_angle)

                random_dx = self.stored_random_dx
                random_dy = self.stored_random_dy

                final_dx = self.mix_factor * dx + (1 - self.mix_factor) * random_dx
                final_dy = self.mix_factor * dy + (1 - self.mix_factor) * random_dy

                length = math.sqrt(final_dx**2 + final_dy**2)
                if length > 0:
                    final_dx = final_dx / length
                    final_dy = final_dy / length

                self.x_change = final_dx * ENEMY_SPEED
                self.y_change = final_dy * ENEMY_SPEED

                if abs(final_dx) > abs(final_dy):
                    self.facing = 'right' if final_dx > 0 else 'left'
                else:
                    self.facing = 'down' if final_dy > 0 else 'up'

            else:
                self.x_change = 0
                self.y_change = 0

    def get_random_direction(self, dx, dy):
        target_angle = math.atan2(dy, dx)
        max_deviation = math.radians(45)
        random_offset = random.uniform(-max_deviation, max_deviation)
        random_angle = target_angle + random_offset
        return math.cos(random_angle), math.sin(random_angle)

    def ai_update(self):
        if self.game.player is None:
            return

        self.x_center, self.y_center = self.get_center()
        player_x_center, player_y_center = self.game.player.get_center()

        dx = player_x_center - self.x_center
        dy = player_y_center - self.y_center
        distance = math.sqrt(dx**2 + dy**2)

        has_los = self.has_line_of_sight(
            self.x_center, self.y_center,
            self.game.player.x_center, self.game.player.y_center
        )

        if has_los and distance <= self.vision_range:
            self.last_known_position = (player_x_center, player_y_center)
            self.last_seen_time = pygame.time.get_ticks()
            self.state = "chasing"

            self.path_update_timer += 1
            if self.path_update_timer >= self.path_update_interval or not self.path:
                self.path_update_timer = 0
                start_tile = (int(self.x_center // TILESIZE), int(self.y_center // TILESIZE))
                target_tile = (int(player_x_center // TILESIZE), int(player_y_center // TILESIZE))

                buffer = 4 * TILESIZE
                max_search_distance = self.vision_range + buffer

                self.path = self.bfs_path(
                    start_tile[0], start_tile[1],
                    target_tile[0], target_tile[1],
                    max_search_distance
                )
                self.path_index = 0


            if distance <= self.attack_range and self.attack_cooldown == 0:
                self.state = "attacking"


        elif self.last_known_position and (pygame.time.get_ticks() - self.last_seen_time < self.memory_time):

            self.state = "searching"

            self.path_update_timer += 1
            if self.path_update_timer >= self.path_update_interval or not self.path:
                self.path_update_timer = 0
                start_tile = (int(self.x_center // TILESIZE), int(self.y_center // TILESIZE))
                target_tile = (int(self.last_known_position[0] // TILESIZE), int(self.last_known_position[1] // TILESIZE))

                self.path = self.bfs_path(
                    start_tile[0], start_tile[1],
                    target_tile[0], target_tile[1],
                    self.vision_range + 4 * TILESIZE
                )
                self.path_index = 0

        else:
            self.state = "idle"
            self.path = []

    def get_direction(self):

        x, y = self.game.player.get_center()

        self.x = x
        self.y = y

        return self.x, self.y
    
    def get_center(self):
        return self.rect.x + TILESIZE/2, self.rect.y + TILESIZE/2


    def movement(self):
        pass


    def animate(self):
        
        pass

class Fire(pygame.sprite.Sprite):
    def __init__(self, game, enemy):
        super().__init__()
        self.game = game
        self.enemy = enemy
        self._layer = ENEMY_LAYER + 1
        
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        # --- MAIN FIRE ANIMATION ---
        self.frames = self.load_fire_animation()
        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.frames[0]
        self.image.set_colorkey('black')
        
        self.rect = self.image.get_rect()
        self.update_position()
    
    def load_fire_animation(self):
        frames = []
        cols = 4
        rows = 2
        frame_width = 32
        frame_height = 32

        for row in range(rows):
            for col in range(cols):
                x = col * frame_width
                y = row * frame_height
                frame = self.game.fire_spritesheet.get_sprite(x, y, frame_width, frame_height)
                frames.append(frame)
        return frames
    
    def update_position(self):
        if self.enemy and self.enemy.alive():

            self.rect.centerx = self.enemy.rect.centerx
            self.rect.centery = self.enemy.rect.centery
        else:
            self.kill()
    
    def update(self):
        self.update_position()
        self.animate()
    
    def animate(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

class SmallFire(pygame.sprite.Sprite):
    def __init__(self, game, enemy, angle=0, radius=20, speed=0.02):
        super().__init__()
        self.game = game
        self.enemy = enemy
        self._layer = ENEMY_LAYER + 1
        
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.angle = angle
        self.radius = radius
        self.speed = speed

        self.damage = 3
        self.hit_cooldown = 0
        self.hit_cooldown_time = 500  # 500ms

        self.frames = self.load_animation()
        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.frames[0]
        self.image.set_colorkey('black')
        
        self.rect = self.image.get_rect()
        self.update_position()
    
    def load_animation(self):

        frames = []
        for i in range(4):
            frame = self.game.fire_spritesheet.get_sprite(i * 16, 0, 16, 16)
            frames.append(frame)
        return frames
    
    def update_position(self):

        if self.enemy and self.enemy.alive():
            self.angle += self.speed
            dx = math.cos(self.angle) * self.radius
            dy = math.sin(self.angle) * self.radius
            
            self.rect.centerx = self.enemy.rect.centerx + dx
            self.rect.centery = self.enemy.rect.centery + dy
        else:
            self.kill()
    
    def check_player_collision(self):

        if self.game.player and self.game.player.alive:
            now = pygame.time.get_ticks()
            if now - self.hit_cooldown < self.hit_cooldown_time:
                return
            
            if self.rect.colliderect(self.game.player.rect):
                self.game.player.hp -= self.damage
                self.hit_cooldown = now
                
                if self.game.player.hp <= 0:
                    self.game.player.hp = 0
                    self.game.player.alive = False
                    self.game.player.kill()
                    self.game.playing = False
    
    def update(self):
        self.update_position()
        self.check_player_collision()
        self.animate()
    
    def animate(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.frames):
            self.current_frame = 0
        self.image = self.frames[int(self.current_frame)]

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.blocks #will be useful when testing collisions
        pygame.sprite.Sprite.__init__(self, self.groups) 

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.greek_column.get_sprite(32, 0, self.width, self.height)

        self.rect = self.image.get_rect() #making rect from the image defined above
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite): #pygame.sprite.Sprite the inhereted class
    def __init__(self, game, x, y, surface = None):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups) #it adds the class into the self.game.all_sprites

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        if surface is not None:
            self.image = surface
        else:
            self.image = self.game.greek_tiles.get_sprite(32, 0, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Button():
    def __init__(self, x, y, width, height, fg, bg, content, fontsize):
        self.font = pygame.font.Font(resource_path('arial.ttf'), fontsize)
        self.content = content

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.fg = fg #foreground
        self.bg = bg #background

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.bg)
        self.rect = self.image.get_rect() 

        self.rect.x = self.x
        self.rect.y = self.y

        self.text = self.font.render(self.content ,True, self.fg)
        self.text_rect = self.text.get_rect(center = (self.width/2, self.height/2))
        self.image.blit(self.text, self.text_rect)

    def is_pressed(self, pos, pressed):
        if self.rect.collidepoint(pos):
            if pressed[0]: #check for the left click button
                return True
            return False
        return False



class Attack(pygame.sprite.Sprite):
    def __init__(self, game, x, y, dx, dy):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

        raw_direction = self.get_direction(dx, dy)
        self.variant = self._resolve_variant(raw_direction)

        self.animation_loop = 0
        self.frames = self.game.attack_variant_frames[self.variant]

        self.image = self.frames[0]
        self.rect = self.image.get_rect()

        self.rect.center = (self.x, self.y)

        self.has_hit = False

    def _resolve_variant(self, direction):
        if direction in self.game.attack_variant_frames:
            return direction
        if direction in DIAGONAL_FOR_CARDINAL:
            return random.choice(DIAGONAL_FOR_CARDINAL[direction])
        return 'down-left' 

    def get_direction(self, dx, dy):
        if dy == -1 and dx == 0:
            return 'up'
        elif dy == 1 and dx == 0:
            return 'down'
        elif dx == -1 and dy == 0:
            return 'left'
        elif dx == 1 and dy == 0:
            return 'right'
        elif dx == -1 and dy == -1:
            return 'up-left'
        elif dx == 1 and dy == -1:
            return 'up-right'
        elif dx == -1 and dy == 1:
            return 'down-left'
        elif dx == 1 and dy == 1:
            return 'down-right'
        else:
            return self.game.player.facing

    def update(self):
        self.animate()
        self.collide()

    def collide(self):
        if self.has_hit:
            return
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        for enemy in hits:
            if hasattr(enemy, 'hitable') and not enemy.hitable:
                continue
            
            dx = enemy.rect.centerx - self.game.player.rect.centerx
            dy = enemy.rect.centery - self.game.player.rect.centery
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                knockback_power = 15 
                enemy.knockback_x = (dx / distance) * knockback_power
                enemy.knockback_y = (dy / distance) * knockback_power
                enemy.is_knocked = True
                enemy.knockback_start_time = pygame.time.get_ticks()
            
            # Damage
            if enemy.take_damage(self.game.player.atk):
                print("Enemy Defeated!")
                earned_gold = random.randint(3, 10)
                gained_xp = random.randint(20, 40)
                self.game.player.gold += earned_gold
                self.game.player.gain_xp(gained_xp)
                if random.random() < 0.2:
                    dropped_item = random.choice(['potion', 'elixir', 'key', 'chest'])
                    self.game.player.add_item(dropped_item, 1)
            else:
                self.has_hit = True

    def animate(self):
        index = math.floor(self.animation_loop)
        if index >= SWORD_FRAME_COUNT:
            self.kill()
            return
        self.image = self.frames[index]
        self.animation_loop += 0.5

class Message:
    def __init__(self, text, color=(255, 255, 255), duration=2000):
        self.text = text
        self.color = color
        self.duration = duration  # Ezredmásodperc
        self.start_time = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 24)
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10
    
    def is_expired(self):

        now = pygame.time.get_ticks()
        return now - self.start_time > self.duration
    
    def draw(self, screen):

        screen.blit(self.image, self.rect)

class Shop:
    def __init__(self, game):
        self.game = game
        self.is_open = False
        self.mode = "buy"
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        self.items = [
            {"name": "Potion", "buy_price": 100, "sell_price": 50, "effect": "heal", "value": 20, "icon": ""},
            {"name": "Elixir", "buy_price": 150, "sell_price": 75, "effect": "full_heal", "value": 0, "icon": ""},
            {"name": "Key", "buy_price": 150, "sell_price": 75, "effect": "key", "value": 1, "icon": ""},
            {"name": "+1 ATK", "buy_price": 500, "sell_price": 250, "effect": "atk_up", "value": 1, "icon": ""},
            {"name": "Chest", "buy_price": 150, "sell_price": 75, "effect": "chest", "value": 1, "icon": ""},
            {"name": "XP Chest", "buy_price": 250, "sell_price": 125, "effect": "xp_chest", "value": None, "icon": ""},
            {"name": "+5 Max HP", "buy_price": 400, "sell_price": 200, "effect": "max_hp_up", "value": 5, "icon": ""},
            {"name": "Speed Boost (+10%)", "buy_price": 600, "sell_price": 300, "effect": "speed_up", "value": 0.1, "icon": "", "min_level": 8}
        ]
        
        self.buttons = []
        self.exit_rect = None
        self.mode_buttons = []
        self.update_buttons()
    
    def update_buttons(self):
        self.buttons = []
        self.mode_buttons = []
        
        win_width, win_height = self.game.screen.get_size()
        
        shop_width = 320
        shop_height = 450
        shop_x = (win_width - shop_width) // 2
        shop_y = (win_height - shop_height) // 2
        
        buy_btn = pygame.Rect(shop_x + 20, shop_y + 50, 130, 25)
        sell_btn = pygame.Rect(shop_x + shop_width - 150, shop_y + 50, 130, 25)
        self.mode_buttons = [(buy_btn, "buy"), (sell_btn, "sell")]
        
        y_offset = 120
        for i, item in enumerate(self.items):
            btn_rect = pygame.Rect(shop_x + 20, shop_y + y_offset + i * 35, shop_width - 40, 30)
            self.buttons.append((btn_rect, item))
        
        self.exit_rect = pygame.Rect(shop_x + 20, shop_y + shop_height - 45, shop_width - 40, 35)
    
    def open(self):
        self.is_open = True
        self.update_buttons()
    
    def close(self):
        self.is_open = False
    
    def handle_click(self, mouse_pos):
        if not self.is_open:
            return
        
        for rect, mode in self.mode_buttons:
            if rect.collidepoint(mouse_pos):
                self.mode = mode
                return
        
        for rect, item in self.buttons:
            if rect.collidepoint(mouse_pos):
                if self.mode == "buy":
                    self.buy_item(item)
                else:
                    self.sell_item(item)
                return
        
        if self.exit_rect and self.exit_rect.collidepoint(mouse_pos):
            self.close()
    
    def buy_item(self, item):
        player = self.game.player

        if item.get("min_level", 1) > player.level:
            self.game.add_message(f"Requires level {item['min_level']} to buy this item!", (255, 200, 100))
            return
        
        if item["effect"] == "xp_chest" and player.level >= 10:
            self.game.add_message("You are already at max level!", (255, 215, 0))
            return
        
        if player.gold >= item["buy_price"]:
            player.gold -= item["buy_price"]
            
            if item["effect"] == "heal":
                healed = min(item["value"], player.max_hp - player.hp)
                player.hp += healed
                self.game.add_message(f" +{healed} HP", (100, 255, 100))
            
            elif item["effect"] == "full_heal":
                player.hp = player.max_hp
                self.game.add_message(f" HP is full!", (100, 255, 100))
            
            elif item["effect"] == "key":
                player.add_item("key", item["value"])
                self.game.add_message(f" +{item['value']} key", (255, 215, 0))
            
            elif item["effect"] == "atk_up":
                player.atk += item["value"]
                self.game.add_message(f" +{item['value']} ATK", (255, 200, 100))
            
            elif item["effect"] == "chest":
                player.add_item("chest", item["value"])
                self.game.add_message(f" +1 chest", (255, 215, 0))
            
            elif item["effect"] == "xp_chest":
                xp_gain = player.level * random.randint(100, 200)
                player.gain_xp(xp_gain)
                self.game.add_message(f" +{xp_gain} XP", (100, 200, 255))
            
            elif item["effect"] == "max_hp_up":
                player.max_hp += item["value"]
                player.hp += item["value"]
                self.game.add_message(f" Max HP +{item['value']}", (255, 100, 100))
            elif item["effect"] == "speed_up":
                player.base_speed *= (1 + item["value"])
                player.speed = player.calculate_speed()
                self.game.add_message(f" Speed increased by {int(item['value'] * 100)}%!", (200, 200, 255))
            
            self.update_buttons()
        else:
            self.game.add_message(f"You don't have enough gold! (Need {item['buy_price']})", (255, 100, 100))
    
    def sell_item(self, item):
        player = self.game.player
        
        effect_map = {
            "heal": "potion",
            "full_heal": "elixir",
            "key": "key",
            "chest": "chest",
        }
        
        if item["effect"] in effect_map:
            key = effect_map[item["effect"]]
            if player.inventory.get(key, 0) <= 0:
                self.game.add_message(f"No {item['name']} in inventory!", (255, 100, 100))
                return
            
            player.inventory[key] -= 1
            if player.inventory[key] == 0:
                del player.inventory[key]
            
            player.gold += item["sell_price"]
            self.game.add_message(f" +{item['sell_price']} gold ({item['name']} sold)", (255, 215, 0))
            self.update_buttons()
        else:
            self.game.add_message(f"{item['name']} cannot be sold!", (255, 100, 100))
    
    def draw(self, screen):
        if not self.is_open:
            return
        
        win_width, win_height = screen.get_size()
        
        shop_width = 320
        shop_height = 450
        shop_x = (win_width - shop_width) // 2
        shop_y = (win_height - shop_height) // 2
        
        bg_surface = pygame.Surface((win_width, win_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        screen.blit(bg_surface, (0, 0))
        
        pygame.draw.rect(screen, (40, 40, 60), (shop_x, shop_y, shop_width, shop_height))
        pygame.draw.rect(screen, (200, 180, 100), (shop_x, shop_y, shop_width, shop_height), 2)
        
        mode_text = "BUY" if self.mode == "buy" else "SELL"
        title = self.title_font.render(f"SHOP - {mode_text}", True, (255, 215, 0))
        title_rect = title.get_rect(center=(shop_x + shop_width // 2, shop_y + 25))
        screen.blit(title, title_rect)
        
        for rect, mode in self.mode_buttons:
            color = (80, 80, 120) if mode == self.mode else (60, 60, 90)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            text = self.font.render("Buy" if mode == "buy" else "Sell", True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        
        gold_text = self.font.render(f"Gold: {self.game.player.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (shop_x + 20, shop_y + 80))
        
        y_offset = 120
        for i, item in enumerate(self.items):
                rect = pygame.Rect(shop_x + 20, shop_y + y_offset + i * 35, shop_width - 40, 30)
                
                if rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (80, 80, 120), rect)
                else:
                    pygame.draw.rect(screen, (60, 60, 90), rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)
                
                min_level = item.get("min_level", 1)
                level_text = f" (Lv.{min_level})" if min_level > 1 else ""
                
                if self.mode == "buy":
                    price = item["buy_price"]
                    price_text = f"{item['icon']} {item['name']}{level_text} - {price}💰"
                else:
                    price = item["sell_price"]
                    if item["effect"] in ["heal", "full_heal", "key", "chest"]:
                        effect_map = {"heal": "potion", "full_heal": "elixir", "key": "key", "chest": "chest"}
                        key = effect_map.get(item["effect"])
                        if key:
                            count = self.game.player.inventory.get(key, 0)
                            if count <= 0:
                                price_text = f"{item['icon']} {item['name']} - (none)"
                            else:
                                price_text = f"{item['icon']} {item['name']} - {price}💰 ({count})"
                        else:
                            price_text = f"{item['icon']} {item['name']} - {price}💰"
                    else:
                        price_text = f"{item['icon']} {item['name']} - {price}💰"
                
                text = self.font.render(price_text, True, (255, 255, 255))
                screen.blit(text, (rect.x + 10, rect.y + 5))
        
        if self.exit_rect:
            pygame.draw.rect(screen, (150, 50, 50), self.exit_rect)
            pygame.draw.rect(screen, (200, 200, 200), self.exit_rect, 1)
            exit_text = self.font.render("Exit", True, (255, 255, 255))
            exit_text_rect = exit_text.get_rect(center=self.exit_rect.center)
            screen.blit(exit_text, exit_text_rect)
            