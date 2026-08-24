import json
import pygame
from sprites import *
from config import *
import config
import sys
import pathfinding
from tiled_loader import TiledMap
from sphinx_ui import SphinxPopup
from sphinx_hmm import SphinxHMM
from utils import resource_path

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(resource_path('arial.ttf'), 32)
        self.show_inventory = True

        self.player_spritesheet = Spritesheet(resource_path('img/player.png'))
        self.player_body_spritesheet = Spritesheet(resource_path('img/player_body.png'))
        self.player_head_spritesheet = Spritesheet(resource_path('img/player_head.png'))
        self.terrain_spritesheet = Spritesheet(resource_path('img/terrain.png'))
        self.enemy_spritesheet = Spritesheet(resource_path('img/enemy_empty.png'))
        self.attack_spritesheet = Spritesheet(resource_path('img/attack_spritesheet.png'))
        self.intro_background = pygame.image.load(resource_path('img/introbackground.png'))
        self.go_background = pygame.image.load(resource_path('img/gameover.png'))
        self.sky_background = pygame.image.load(resource_path('img/sky_background.png')).convert_alpha()
        self.greek_tiles = Spritesheet(resource_path('img/greek_tiles.png'))
        self.greek_column = Spritesheet(resource_path('img/greek_column.png'))
        self.fire_spritesheet = Spritesheet(resource_path('img/blue_fire_spritesheet.png'))
        self.chest_spritesheet = Spritesheet(resource_path('img/chest_spritesheet.png'))

        initial_skills = [1, 1, 1]
        self.sphinx_hmm = SphinxHMM(initial_skills = initial_skills)
        self.sphinx_popup = SphinxPopup(self)

        self.game_paused = False

        self.sphinx_spawn_timer = 0
        self.sphinx_spawn_interval = 5000
        self.level_up_triggered = False

        self.attack_variant_frames = {
            'up-left':    self.load_attack_variant_frames('up_left'),
            'up-right':   self.load_attack_variant_frames('up_right'),
            'down-left':  self.load_attack_variant_frames('down_left'),
            'down-right': self.load_attack_variant_frames('down_right'),
        }

        self.sky_width = self.sky_background.get_width()

        self.camera_x = 0
        self.camera_y = 0

        self.tiled_map = TiledMap('map.json')

        self.messages = []

        self.shop = Shop(self)

        self.sword_carry_frames = {
            variant: frames[0]
            for variant, frames in self.attack_variant_frames.items()
}



    def handle_answer(self, q_type: int, correct: bool):

        self.sphinx_hmm.add_answer(q_type, correct)

        skills = self.sphinx_hmm.estimate_skills()

        if skills:
            print(f"Abilities: math = {skills[0]}, history = {skills[1]}, literature = {skills[2]}")

    def sphinx_appears(self):

        q_type = self.sphinx_hmm.get_weakest_type()

        correct = self.ask_question(q_type)
        self.handle_answer(q_type, correct)

        if not correct: 
            self.player.hp -= self.player.hp//3


    def load_attack_variant_frames(self, variant_name):
        """variant_name pl. 'up_left', 'up_right', 'down_left', 'down_right'."""
        sword_sheet = Spritesheet(f'img/sword_{variant_name}.png')
        effect_sheet = Spritesheet(f'img/attack_effect_{variant_name}.png')

        frames = []
        for i in range(SWORD_FRAME_COUNT):
            sword_frame = sword_sheet.get_sprite(i * SWORD_FRAME_SIZE, 0, SWORD_FRAME_SIZE, SWORD_FRAME_SIZE)
            effect_frame = effect_sheet.get_sprite(i * SWORD_FRAME_SIZE, 0, SWORD_FRAME_SIZE, SWORD_FRAME_SIZE)

            combined = pygame.Surface((SWORD_FRAME_SIZE, SWORD_FRAME_SIZE), pygame.SRCALPHA)
            combined.blit(effect_frame, (0, 0))   # az effekt kerül hátra (mintha nyom lenne a penge mögött)
            combined.blit(sword_frame, (0, 0))    # a kard felülre
            frames.append(combined)
        return frames


    def add_message(self, text, color=(255, 255, 255), duration=3000):
        """Új üzenet hozzáadása a képernyőre."""
        self.messages.append(Message(text, color, duration))

    def createTilemap(self):
        config.tilemap = self.tiled_map.build_walkable_grid(blocking_gids={14})

        for y in range(self.tiled_map.height):
            for x in range(self.tiled_map.width):
                gid = self.tiled_map.gid_at(x, y)
                if gid == 0:
                    continue
                surface = self.tiled_map.get_surface(gid)
                Ground(self, x, y, surface)

        spawn_x, spawn_y = self.tiled_map.find_center_walkable()
        self.player = Player(self, spawn_x, spawn_y)

        import random
        walkable = [
            (x, y)
            for y in range(self.tiled_map.height)
            for x in range(self.tiled_map.width)
            if config.tilemap[y][x] == "G"
        ]
        for _ in range(3):
            ex, ey = random.choice(walkable)
            Enemy(self, ex, ey)

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def win(self):

        self.playing = False
        self.running = True
        self.game_over_reason = "win"

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
                sys.exit()
                pygame.quit()


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.shop.is_open:

                        self.shop.handle_click(event.pos)
                    elif self.show_inventory:

                        self.handle_inventory_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory

                if event.key == pygame.K_b:
                    if self.shop.is_open:
                        self.shop.close()
                    else:
                        self.shop.open()

                if event.key == pygame.K_q:
                    self.player.use_potion()
                if event.key == pygame.K_e:
                    self.player.use_elixir()
                if event.key == pygame.K_c:
                    self.player.use_chest()

                if event.key == pygame.K_SPACE:
                    if not self.player.attacking:
                        self.player.attacking = True
                        self.player.attack_start_time = pygame.time.get_ticks()

                        dx, dy = self.player.get_direction()

                        if dx == 0 and dy == 0:
                            if self.player.facing == 'up':
                                dy = -1
                            elif self.player.facing == 'down':
                                dy = 1
                            elif self.player.facing == 'left':
                                dx = -1
                            elif self.player.facing == 'right':
                                dx = 1

                        attack_x = self.player.x_center
                        attack_y = self.player.y_center

                        Attack(self, attack_x, attack_y, dx, dy)

            if self.sphinx_popup.is_open:
                if self.sphinx_popup.handle_event(event):
                    pass #the event is managed by popup

    def handle_inventory_click(self, mouse_pos):
        if not self.player:
            return

        inv_width = 250
        inv_height = 200
        inv_x = WIN_WIDTH - inv_width - 10
        inv_y = WIN_HEIGHT - inv_height - 10

        y_offset = 30

        # 1. Összes tárgy pozíciójának összegyűjtése
        items_positions = []
        for key, value in self.player.inventory.items():
            if key == "equipment":
                continue
            if isinstance(value, int) and value > 0:
                item_rect = pygame.Rect(inv_x + 10, inv_y + y_offset, inv_width - 20, 20)
                items_positions.append((item_rect, key, value))
                y_offset += 20
            elif isinstance(value, dict):
                for eq_key, eq_value in value.items():
                    if eq_value:
                        item_rect = pygame.Rect(inv_x + 10, inv_y + y_offset, inv_width - 20, 20)
                        items_positions.append((item_rect, eq_key, eq_value))
                        y_offset += 20

        for rect, key, value in items_positions:
            if rect.collidepoint(mouse_pos):
                self.handle_item_use(key)
                return

        if "chest" in self.player.inventory and self.player.inventory["chest"] > 0:
            chest_rect = pygame.Rect(inv_x + 10, inv_y + y_offset, inv_width - 20, 20)
            if chest_rect.collidepoint(mouse_pos):
                self.player.use_chest()
                return

    def handle_item_use(self, key):
        if key == "potion":
            self.player.use_potion()
        elif key == "elixir":
            self.player.use_elixir()
        elif key == "key":
            print(f" Number of keys: {self.player.inventory.get('key', 0)}")
        elif key == "chest":
            self.player.use_chest()
        else:
            print(f"Unknown item: {key}")

    def update(self):

        if self.sphinx_popup.is_open:
            self.sphinx_popup.update()
            return #pausing when the sphinx appears


        self._check_sphinx_spawn()

        self.all_sprites.update()

    def _check_sphinx_spawn(self):
        """Check is Sphinx should appear"""

        if self.sphinx_popup.is_open:
            return
        if not hasattr(self, 'player'):
            return 

        if hasattr(self.player, 'level_just_upgraded') and self.player.level_just_upgraded:

            if random.random() < 0.5:
                self.sphinx_popup.open()
                self.player.level_just_upgraded = False
            else:
                self.player.level_just_upgraded = False


    def update_camera(self):
        if self.player:

            center_x, center_y = self.player.get_center()
            self.camera_x = center_x - WIN_WIDTH // 2
            self.camera_y = center_y - WIN_HEIGHT // 2

    def draw_stats(self):
        if not self.player:
            return


        stats_width = 200
        stats_height = 40
        stats_x = 10
        stats_y = 10
        
        bg_surface = pygame.Surface((stats_width, stats_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        self.screen.blit(bg_surface, (stats_x, stats_y))
        
        pygame.draw.rect(self.screen, (200, 200, 200), (stats_x, stats_y, stats_width, stats_height), 1)
        
        font = pygame.font.Font(None, 20)
        
        level_text = font.render(f"Level: {self.player.level}", True, (255, 215, 0))
        self.screen.blit(level_text, (stats_x + 10, stats_y + 5))

        xp_ratio = self.player.xp / self.player.xp_to_next_level if self.player.xp_to_next_level > 0 else 0
        bar_width = stats_width - 20
        bar_height = 8
        bar_x = stats_x + 10
        bar_y = stats_y + 25

        pygame.draw.rect(self.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        fill_width = int(bar_width * xp_ratio)
        if fill_width > 0:
            pygame.draw.rect(self.screen, (100, 200, 255), (bar_x, bar_y, fill_width, bar_height))

    def draw_inventory(self):
        if not self.show_inventory:
            return

        if not self.player:
            return

        inv_width = 250
        inv_height = 200
        inv_x = WIN_WIDTH - inv_width - 10
        inv_y = WIN_HEIGHT - inv_height - 10

        bg_surface = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 180))
        self.screen.blit(bg_surface, (inv_x, inv_y))

        pygame.draw.rect(self.screen, (200, 200, 200), (inv_x, inv_y, inv_width, inv_height), 2)

        font = pygame.font.Font(None, 20)
        title = font.render("INVENTORY (I)", True, (255, 255, 255))
        self.screen.blit(title, (inv_x + 10, inv_y + 5))

        y_offset = 30
        for key, value in self.player.inventory.items():
            if key == "equipment":
                continue

            if isinstance(value, int) and value > 0:
                if key == "chest":
                    text = font.render(f"{key}: {value} (click)", True, (255, 215, 0))
                else:
                    text = font.render(f"{key}: {value}", True, (200, 200, 200))
                self.screen.blit(text, (inv_x + 10, inv_y + y_offset))
                y_offset += 20
            elif isinstance(value, dict):
                for eq_key, eq_value in value.items():
                    if eq_value:
                        text = font.render(f"{eq_key}: {eq_value}", True, (200, 200, 200))
                        self.screen.blit(text, (inv_x + 10, inv_y + y_offset))
                        y_offset += 20

    def draw(self):
        self.update_camera()

        sky_x = -self.camera_x * 0.2
        sky_x = sky_x % self.sky_width - self.sky_width
        self.screen.blit(self.sky_background, (sky_x, 0))
        self.screen.blit(self.sky_background, (sky_x + self.sky_width, 0))

        for sprite in self.all_sprites:
            screen_x = sprite.rect.x - self.camera_x
            screen_y = sprite.rect.y - self.camera_y

            # --- CSAK AKKOR TOLJUK EL, HA NEM TÁMAD ---
            if isinstance(sprite, Player) and not sprite.attacking:
                screen_x -= 48
                screen_y -= 48

            self.screen.blit(sprite.image, (screen_x, screen_y))

        for enemy in self.enemies:
            if not enemy.is_dead:
                enemy.draw_health_bar(self.camera_x, self.camera_y)
                enemy.draw_attack_range(self.camera_x, self.camera_y)

        self.player.draw_health_bar(self.camera_x, self.camera_y)

        self.draw_inventory()
        self.draw_stats()
        self.shop.draw(self.screen)

        y_offset = 10
        for message in self.messages[:]: 
            message.rect.y = y_offset
            message.draw(self.screen)
            y_offset += 30 

            if message.is_expired():
                self.messages.remove(message)

        self.draw_ui()

        if self.sphinx_popup.is_open:
            self.sphinx_popup.draw(self.screen)
        
        self.clock.tick(FPS)
        pygame.display.update()

    def draw_ui(self):

        if not self.player:
            return

        # --- HEALTH BAR BEÁLLÍTÁSOK ---
        bar_width = 300
        bar_height = 30
        bar_x = 20
        bar_y = WIN_HEIGHT - bar_height - 20  # 20 pixel távolság az aljától
        border_radius = 5

        # 1. Háttér (sötét)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (40, 40, 40), bg_rect, border_radius=border_radius)

        # 2. HP arány kiszámítása
        hp_ratio = self.player.hp / self.player.max_hp if self.player.max_hp > 0 else 0
        current_width = max(0, int(bar_width * hp_ratio))

        # 3. Szín beállítása
        if hp_ratio > 0.6:
            color = (0, 255, 0)     
        elif hp_ratio > 0.3:
            color = (255, 255, 0)  
        else:
            color = (255, 0, 0)     

        # 4. Előtér (színes rész)
        if current_width > 0:
            hp_rect = pygame.Rect(bar_x, bar_y, current_width, bar_height)
            pygame.draw.rect(self.screen, color, hp_rect, border_radius=border_radius)

        # 5. Szegély
        pygame.draw.rect(self.screen, (200, 200, 200), bg_rect, 2, border_radius=border_radius)

        # 6. Szöveg (HP / MaxHP)
        font = pygame.font.Font(None, 24)
        hp_text = font.render(f"{self.player.hp} / {self.player.max_hp}", True, (255, 255, 255))
        text_rect = hp_text.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
        self.screen.blit(hp_text, text_rect)

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        self.running = True
        self.playing = False

        if hasattr(self, 'game_over_reason') and self.game_over_reason == "win":
            text = self.font.render('🏆 YOU WIN! 🏆', True, (255, 215, 0))
            bg_color = (20, 40, 20) 
            button_color = 'gold'

        else:
            text = self.font.render(' GAME OVER ', True, (255, 0, 0))
            bg_color = (40, 20, 20)  # Sötétpiros háttér
            button_color = 'white'

        text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))

        restart_button = Button(10, WIN_HEIGHT - 60, 120, 50, 'white', 'black', 'Restart', 32)

        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()
                self.running = True

            self.screen.blit(self.go_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Some Game', True, 'black')
        title_rect = title.get_rect(x=10, y=10)

        play_button = Button(10, 50, 100, 50, 'white', 'black', 'Play', 32)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()


g = Game()
g.intro_screen()
g.new()

while g.running:
    g.main()
    g.game_over()

sys.exit()
pygame.quit()