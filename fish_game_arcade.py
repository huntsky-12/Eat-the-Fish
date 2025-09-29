
import arcade
import os
import math
import random
import copy
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum
import tkinter as tk
from tkinter import font

# Game constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Eat the Fish, ft. Pengu"

# Board layout
BOARD_COLS = 8
BOARD_ROWS = 6
TOTAL_TILES = BOARD_COLS * BOARD_ROWS

# Hex tile constants
HEX_RADIUS = 50
HEX_WIDTH = HEX_RADIUS * 2
HEX_HEIGHT = HEX_RADIUS * 1.732

# Beautiful color palette - Rich and elegant
WATER_COLOR = (25, 42, 86)          # Deep navy blue
WATER_DARK = (15, 25, 50)           # Darker navy for depth
WATER_FOAM = (135, 206, 235, 30)    # Light blue foam (transparent)

# Gorgeous tile colors - Dark yellow/amber theme
TILE_BASE = (218, 165, 32)          # Dark goldenrod (main tile)
TILE_LIGHT = (238, 203, 90)         # Lighter amber highlight  
TILE_DARK = (184, 134, 11)          # Darker amber shadow
TILE_OUTLINE = (139, 90, 0)         # Deep amber outline
TILE_SHADOW = (92, 51, 23, 120)     # Warm brown shadow

# Alternative tile colors for variety
TILE_HONEY = (255, 193, 37)         # Honey amber
TILE_BRONZE = (205, 127, 50)        # Bronze amber
TILE_COPPER = (184, 115, 51)        # Copper amber

# Beautiful fish colors - Ocean themed
FISH_CORAL = (255, 127, 80)         # Coral orange
FISH_TURQUOISE = (64, 224, 208)     # Turquoise blue  
FISH_GOLD = (255, 215, 0)           # Golden fish
FISH_SALMON = (250, 128, 114)       # Salmon pink

# Enhanced penguin colors
PENGUIN_HUMAN_BASE = (220, 20, 60)   # Crimson red
PENGUIN_HUMAN_LIGHT = (255, 69, 0)   # Red orange highlight
PENGUIN_HUMAN_DARK = (139, 0, 0)     # Dark red shadow

PENGUIN_AI_BASE = (30, 144, 255)     # Dodger blue
PENGUIN_AI_LIGHT = (135, 206, 250)   # Light sky blue
PENGUIN_AI_DARK = (0, 100, 200)      # Deep blue shadow

# Premium UI colors
SELECTED_COLOR = (255, 215, 0)       # Pure gold selection
VALID_MOVE_COLOR = (50, 205, 50)     # Lime green moves  
INVALID_MOVE = (255, 69, 0, 100)     # Red invalid (transparent)

TEXT_PRIMARY = (245, 245, 220)       # Beige text
TEXT_ACCENT = (255, 215, 0)          # Gold accent text
TEXT_SHADOW = (0, 0, 0, 150)         # Text shadow

ACCENT_GLOW = (255, 215, 0, 80)      # Golden glow effect
PARTICLE_GOLD = (255, 215, 0)        # Gold particles
PARTICLE_BLUE = (30, 144, 255)       # Blue particles

class FishCount(Enum):
    ONE = 1
    TWO = 2  
    THREE = 3

@dataclass
class Tile:
    col: int
    row: int
    fish_count: FishCount
    has_penguin: bool = False
    penguin_player: int = -1
    exists: bool = True
    # Enhanced animation properties
    hover_scale: float = 1.0
    selected_glow: float = 0.0
    fish_animation_offset: float = 0.0
    tile_variant: int = 0  # For color variety

@dataclass
class Penguin:
    player_id: int
    col: int
    row: int
    # Animation properties
    bob_offset: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    happiness: float = 0.5  # For expression

class ParticleEffect:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], particle_type: str = "default"):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-3, 3)
        self.vel_y = random.uniform(2, 5)
        self.color = color
        self.life = 1.5
        self.max_life = self.life
        self.size = random.uniform(3, 6)
        self.particle_type = particle_type
        self.spin = random.uniform(-5, 5)
        self.angle = 0

    def update(self, delta_time: float):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= delta_time
        self.vel_y -= 0.15  # Gravity
        self.angle += self.spin * delta_time

        # Sparkle effect for gold particles
        if self.particle_type == "gold":
            self.vel_x += random.uniform(-0.1, 0.1)

    def draw(self):
        if self.life > 0:
            life_ratio = self.life / self.max_life
            alpha = int(life_ratio * 255)
            size = self.size * life_ratio

            if self.particle_type == "gold":
                # Draw sparkling gold particle
                arcade.draw_circle_filled(self.x, self.y, size, (*self.color, alpha))
                arcade.draw_circle_filled(self.x, self.y, size * 0.5, (255, 255, 255, alpha // 2))
            else:
                arcade.draw_circle_filled(self.x, self.y, size, (*self.color, alpha))

class AIPlayer:

    def __init__(self, player_id: int):
        self.player_id = player_id
        self.thinking_particles = []

    def add_thinking_particle(self, x: float, y: float):
        self.thinking_particles.append(ParticleEffect(x, y, PARTICLE_BLUE, "thinking"))

    def update_particles(self, delta_time: float):
        self.thinking_particles = [p for p in self.thinking_particles if p.life > 0]
        for particle in self.thinking_particles:
            particle.update(delta_time)

    def draw_particles(self):
        for particle in self.thinking_particles:
            particle.draw()

    # [Previous AI logic methods remain the same]
    def evaluate_move(self, game, from_col, from_row, to_col, to_row):
        to_tile = game.get_tile(to_col, to_row)
        if not to_tile:
            return -1000

        from_tile = game.get_tile(from_col, from_row)
        score = from_tile.fish_count.value if from_tile else 0
        score += to_tile.fish_count.value * 0.5

        opponent_blocked = 0
        for penguin in game.get_player_penguins(1 - self.player_id):
            if game.can_reach(penguin.col, penguin.row, to_col, to_row):
                opponent_blocked += 1
        score += opponent_blocked * 2

        center_col, center_row = BOARD_COLS // 2, BOARD_ROWS // 2
        distance_from_center = abs(to_col - center_col) + abs(to_row - center_row)
        score -= distance_from_center * 0.1

        return score

    def get_best_move(self, game):
        best_move = None
        best_score = -1000

        for penguin in game.get_player_penguins(self.player_id):
            if random.random() < 0.2:  # Add thinking particles
                center_x, center_y = game.get_tile_center(penguin.col, penguin.row)
                self.add_thinking_particle(
                    center_x + random.uniform(-25, 25),
                    center_y + random.uniform(-25, 25)
                )

            valid_moves = game.get_valid_moves(penguin.col, penguin.row)

            for to_col, to_row in valid_moves:
                score = self.evaluate_move(game, penguin.col, penguin.row, to_col, to_row)

                if score > best_score:
                    best_score = score
                    best_move = (penguin.col, penguin.row, to_col, to_row)

        return best_move

    def get_best_placement(self, game):
        best_placement = None
        best_score = -1000

        for col in range(BOARD_COLS):
            for row in range(BOARD_ROWS):
                tile = game.get_tile(col, row)
                if tile and not tile.has_penguin and tile.fish_count == FishCount.ONE:
                    score = 0

                    adjacent_count = 0
                    for adj_col, adj_row in game.get_adjacent_positions(col, row):
                        adj_tile = game.get_tile(adj_col, adj_row)
                        if adj_tile and adj_tile.exists:
                            adjacent_count += 1
                            score += adj_tile.fish_count.value * 0.1

                    score += adjacent_count

                    center_col, center_row = BOARD_COLS // 2, BOARD_ROWS // 2
                    distance_from_center = abs(col - center_col) + abs(row - center_row)
                    score -= distance_from_center * 0.5

                    if score > best_score:
                        best_score = score
                        best_placement = (col, row)

        return best_placement

class FishGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(WATER_COLOR)
        font_path = os.path.join("fonts", "PressStart2P-Regular.ttf")
        arcade.load_font(font_path)

        # Game state
        self.board: List[List[Optional[Tile]]] = []
        self.penguins: List[Penguin] = []
        self.current_player = 0
        self.game_phase = "placement"
        self.player_scores = [0, 0]
        self.penguins_per_player = 4 # this is to change the minimum number of 1 penguins we need to choose

        # AI
        self.ai = AIPlayer(1)
        self.ai_thinking = False
        self.ai_timer = 0.0
        self.ai_delay = 1.2

        # UI state
        self.selected_penguin = None
        self.valid_moves = []
        self.status_message = ""

        # Animation state
        self.time_elapsed = 0.0
        self.particles = []
        self.water_animation_offset = 0.0

        # Visual positioning
        self.board_start_x = SCREEN_WIDTH // 2 - (BOARD_COLS * HEX_RADIUS * 1.5) // 2
        self.board_start_y = SCREEN_HEIGHT // 2

        # Beautiful text objects
        self.title_text = arcade.Text(
            "Eat the Fish, ft. Pengu", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT - 40,
            TEXT_ACCENT, 
            25, 
            anchor_x="center",
            font_name="PressStart2P",
            bold=True
        )

        self.human_score_text = arcade.Text(
            "", 15, SCREEN_HEIGHT - 90, PENGUIN_HUMAN_BASE, 15,
            font_name="PressStart2P", bold=True
        )

        self.ai_score_text = arcade.Text(
            "", 15, SCREEN_HEIGHT - 125, PENGUIN_AI_BASE, 15,
            font_name="PressStart2P", bold=True
        )

        self.status_text = arcade.Text(
            "", SCREEN_WIDTH // 2, 80, TEXT_PRIMARY, 25,
            anchor_x="center", font_name="PressStart2P", bold=True
        )

        self.phase_text = arcade.Text(
            "", SCREEN_WIDTH - 30, SCREEN_HEIGHT - 90, TEXT_ACCENT, 22,
            anchor_x="right", font_name="PressStart2P", bold=True
        )

        self.controls_text = arcade.Text(
            "", SCREEN_WIDTH // 2, 50, TEXT_PRIMARY, 15,
            anchor_x="center", font_name="PressStart2P"
        )

    def setup(self):
        self.create_board()
        self.status_message = "Place the Penguins on 1-fish tiles!"
        self.update_text_objects()

    def update_text_objects(self):
        self.human_score_text.text = f"human (Brown): {self.player_scores[0]} fish"
        self.human_score_text.color = (210, 180, 140)
        self.human_score_text.font_name = "Press Start 2P"

        self.ai_score_text.text = f"TARS (Blue): {self.player_scores[1]} fish"
        self.ai_score_text.color = (100, 149, 237)
        self.ai_score_text.font_name = "Press Start 2P"
        self.status_text.text = self.status_message
        self.status_text.color = (255, 255, 255)
        self.status_text.font_name = "Press Start 2P"
        self.status_text.bold=True
        self.status_text.font_size = 20 
        self.status_text.anchor_x = "center"
        self.status_text.x = SCREEN_WIDTH / 2
        self.status_text.y = 125
        

        if self.game_phase == "placement":
            self.phase_text.text = "PLACEMENT PHASE"
        elif self.game_phase == "playing":
            self.phase_text.text = "PLAYING PHASE"
        elif self.game_phase == "game_over":
            self.phase_text.text = "GAME OVER"

        self.phase_text.color = (0, 0, 0)
        self.phase_text.font_name = "Press Start 2P"
        self.phase_text.font_size = 25
        self.phase_text.x = self.width // 2
        self.phase_text.anchor_x = "center"
        self.phase_text.anchor_y = "bottom"

        if self.game_phase == "placement":
            self.controls_text.text = "Click on 1-fish tiles to place the penguins"
        elif self.game_phase == "playing":
            self.controls_text.text = "Click the penguin, then click where to move"
        elif self.game_phase == "game_over":
            self.controls_text.text = "Press R to restart"

        self.controls_text.color = (192, 192, 192)
        self.controls_text.font_name = "Courier New"
        self.controls_text.font_size = 14
        self.controls_text.x = self.width // 2
        self.controls_text.y = 40
        self.controls_text.anchor_x = "center"

    def create_board(self):
        """Create board with beautiful color variations"""
        self.board = []
        
        fish_pattern = [
            [1, 2, 3, 1, 2, 1, 3],
            [2, 1, 1, 3, 1, 2, 2],
            [1, 3, 2, 1, 3, 1, 2],
            [3, 1, 1, 2, 1, 3, 1],
            [2, 3, 2, 1, 2, 3, 1],
            [1, 2, 3, 2, 1, 1, 3],
            [3, 1, 2, 3, 1, 2, 1],
            [2, 3, 1, 1, 2, 3, 2]
        ]



        for row in range(BOARD_ROWS):
            board_row = []
            for col in range(BOARD_COLS):
                fish_count_value = fish_pattern[row][col] if row < len(fish_pattern) and col < len(fish_pattern[row]) else random.choice([1, 1, 1, 2, 2, 3])
                fish_count = FishCount(fish_count_value)

                tile = Tile(col, row, fish_count)
                tile.fish_animation_offset = random.uniform(0, math.pi * 2)
                tile.tile_variant = random.randint(0, 2)  # For color variety
                board_row.append(tile)

            self.board.append(board_row)

    # [Previous game logic methods remain the same]
    def get_tile(self, col: int, row: int) -> Optional[Tile]:
        if 0 <= col < BOARD_COLS and 0 <= row < BOARD_ROWS:
            return self.board[row][col]
        return None

    def get_tile_center(self, col: int, row: int) -> Tuple[float, float]:
        x_offset = HEX_RADIUS * 0.75 if row % 2 == 1 else 0
        x = self.board_start_x + col * (HEX_RADIUS * 1.5) + x_offset
        y = self.board_start_y + row * (HEX_HEIGHT * 0.75) - (BOARD_ROWS * HEX_HEIGHT * 0.75) // 2
        return x, y

    def pixel_to_tile(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        best_distance = float('inf')
        best_tile = None

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                tile_x, tile_y = self.get_tile_center(col, row)
                distance = math.sqrt((x - tile_x)**2 + (y - tile_y)**2)

                if distance < HEX_RADIUS and distance < best_distance:
                    best_distance = distance
                    best_tile = (col, row)

        return best_tile

    def get_player_penguins(self, player_id: int) -> List[Penguin]:
        return [p for p in self.penguins if p.player_id == player_id]

    def get_penguin_at(self, col: int, row: int) -> Optional[Penguin]:
        for penguin in self.penguins:
            if penguin.col == col and penguin.row == row:
                return penguin
        return None

    def get_adjacent_positions(self, col: int, row: int) -> List[Tuple[int, int]]:
        adjacent = []
        if row % 2 == 0:
            offsets = [(-1, -1), (0, -1), (-1, 0), (1, 0), (-1, 1), (0, 1)]
        else:
            offsets = [(0, -1), (1, -1), (-1, 0), (1, 0), (0, 1), (1, 1)]

        for dx, dy in offsets:
            new_col, new_row = col + dx, row + dy
            if 0 <= new_col < BOARD_COLS and 0 <= new_row < BOARD_ROWS:
                adjacent.append((new_col, new_row))

        return adjacent

    def can_reach(self, from_col: int, from_row: int, to_col: int, to_row: int) -> bool:
        if from_col == to_col and from_row == to_row:
            return False

        dx = to_col - from_col
        dy = to_row - from_row
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return False

        step_x = dx / steps
        step_y = dy / steps

        for step in range(1, steps + 1):
            check_col = from_col + round(step_x * step)
            check_row = from_row + round(step_y * step)

            tile = self.get_tile(check_col, check_row)
            if not tile or not tile.exists:
                return False

            if step < steps and tile.has_penguin:
                return False

        return True

    def get_valid_moves(self, col: int, row: int) -> List[Tuple[int, int]]:
        valid_moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dx, dy in directions:
            distance = 1
            while True:
                new_col = col + dx * distance
                new_row = row + dy * distance

                if not (0 <= new_col < BOARD_COLS and 0 <= new_row < BOARD_ROWS):
                    break

                tile = self.get_tile(new_col, new_row)
                if not tile or not tile.exists or tile.has_penguin:
                    break

                valid_moves.append((new_col, new_row))
                distance += 1

        return valid_moves

    def place_penguin(self, col: int, row: int, player_id: int) -> bool:
        tile = self.get_tile(col, row)
        if not tile or tile.has_penguin or tile.fish_count != FishCount.ONE:
            return False

        penguin = Penguin(player_id, col, row)
        penguin.bob_offset = random.uniform(0, math.pi * 2)
        penguin.happiness = 0.8  # Happy to be placed!
        self.penguins.append(penguin)

        tile.has_penguin = True
        tile.penguin_player = player_id

        # Beautiful placement particles
        center_x, center_y = self.get_tile_center(col, row)
        particle_color = PARTICLE_GOLD if player_id == 0 else PARTICLE_BLUE
        for _ in range(12):
            self.particles.append(ParticleEffect(center_x, center_y, particle_color, "gold"))

        return True

    def move_penguin(self, from_col: int, from_row: int, to_col: int, to_row: int) -> bool:
        from_tile = self.get_tile(from_col, from_row)
        to_tile = self.get_tile(to_col, to_row)

        if not from_tile or not to_tile or not from_tile.has_penguin:
            return False

        penguin = self.get_penguin_at(from_col, from_row)
        if not penguin:
            return False

        # Collect fish with beautiful particles
        fish_collected = from_tile.fish_count.value
        self.player_scores[penguin.player_id] += fish_collected

        center_x, center_y = self.get_tile_center(from_col, from_row)
        for _ in range(fish_collected * 5):
            fish_colors = [FISH_CORAL, FISH_TURQUOISE, FISH_GOLD, FISH_SALMON]
            color = random.choice(fish_colors)
            self.particles.append(ParticleEffect(center_x, center_y, color, "gold"))

        from_tile.exists = False
        from_tile.has_penguin = False

        penguin.col = to_col
        penguin.row = to_row
        penguin.happiness = min(penguin.happiness + 0.2, 1.0)  # Happy after eating!

        to_tile.has_penguin = True
        to_tile.penguin_player = penguin.player_id

        return True

    def check_game_over(self) -> bool:
        player_penguins = self.get_player_penguins(self.current_player)
        for penguin in player_penguins:
            if self.get_valid_moves(penguin.col, penguin.row):
                return False
        return True

    def handle_placement_click(self, col: int, row: int):
        if self.current_player != 0:
            return

        if self.place_penguin(col, row, 0):
            human_penguins = len(self.get_player_penguins(0))
            ai_penguins = len(self.get_player_penguins(1))

            if human_penguins < self.penguins_per_player:
                self.current_player = 1
                self.status_message = " TARS is selecting perfect position..."
            elif human_penguins >= self.penguins_per_player and ai_penguins >= self.penguins_per_player:
                self.game_phase = "playing"
                self.current_player = 0
                self.status_message = "All set! Click the penguin to begin fishing!"
            else:
                self.current_player = 1
                self.status_message = " TARS positioning strategically..."
        else:
            self.status_message = "Please click a golden tile with 1 fish!"

        self.update_text_objects()

    def handle_playing_click(self, col: int, row: int):
        if self.current_player != 0:
            return

        penguin = self.get_penguin_at(col, row)

        if penguin and penguin.player_id == 0:
            self.selected_penguin = penguin
            self.valid_moves = self.get_valid_moves(col, row)
            self.status_message = f"Penguin ready! Choose the destination!"
        elif self.selected_penguin and (col, row) in self.valid_moves:
            if self.move_penguin(self.selected_penguin.col, self.selected_penguin.row, col, row):
                self.selected_penguin = None
                self.valid_moves = []

                if self.check_game_over():
                    self.game_phase = "game_over"
                    self.status_message = self.show_game_over()
                else:
                    self.current_player = 1
                    self.status_message = "TARS analyzing best fishing spots..."
        else:
            self.status_message = " Select the penguin first!"

        self.update_text_objects()

    def show_game_over(self):
        human_score = self.player_scores[0]
        ai_score = self.player_scores[1]

        if human_score > ai_score:
            msg = f"Player Wins!   \nFinal Score: {human_score} \nAI: {ai_score}"
            fg_color = "white"
        elif ai_score > human_score:
            msg = f"TARS Wins!   \nFinal Score: Player: {human_score} \nAI: {ai_score}"
            fg_color = "white"
        else:
            msg = f"It's a Tie!  \nScore: Player: {human_score} \nAI: {ai_score}"
            fg_color = "yellow"

        root = tk.Tk()
        root.withdraw()  # hide main window

        popup = tk.Toplevel(root)
        popup.title("GAME OVER")
        popup.configure(bg="black")
        popup.geometry("500x300")
        popup.resizable(False, False)

        # Retro arcade font
        arcade_font = font.Font(family="Press Start 2P", size=16, weight="bold")

        # Message label with glowing effect (simulate by adding a border)
        label = tk.Label(
            popup,
            text=msg,
            fg=fg_color,
            bg="black",
            font=arcade_font,
            wraplength=480,
            justify="center",
            relief="solid",
            bd=4
        )
        label.pack(expand=True, pady=20)

        # OK button in matching style
        button = tk.Button(
            popup,
            text="OK",
            command=popup.destroy,
            font=arcade_font,
            bg="gray20",
            fg="white",
            activebackground="gray40",
            activeforeground="white",
            bd=3
        )
        button.pack(pady=10)

        # Center popup on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - popup.winfo_width()) // 2
        y = (popup.winfo_screenheight() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        popup.mainloop()

    def ai_place_penguin(self):
        placement = self.ai.get_best_placement(self)
        if placement:
            col, row = placement
            if self.place_penguin(col, row, 1):
                human_penguins = len(self.get_player_penguins(0))
                ai_penguins = len(self.get_player_penguins(1))

                if human_penguins >= self.penguins_per_player and ai_penguins >= self.penguins_per_player:
                    self.game_phase = "playing"
                    self.current_player = 0
                    self.status_message = " Perfect setup! Your turn to fish!"
                else:
                    self.current_player = 0
                    self.status_message = "Your turn to place on golden tiles!"

        self.update_text_objects()

    def ai_make_move(self):
        best_move = self.ai.get_best_move(self)
        if best_move:
            from_col, from_row, to_col, to_row = best_move
            if self.move_penguin(from_col, from_row, to_col, to_row):
                if self.check_game_over():
                    self.game_phase = "game_over"
                    self.status_message = self.show_game_over()
                else:
                    self.current_player = 0
                    self.status_message = "Your turn to make a brilliant move!"
        else:
            self.game_phase = "game_over"
            self.status_message = self.show_game_over()

        self.update_text_objects()

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if self.game_phase == "game_over":
            return

        tile_pos = self.pixel_to_tile(x, y)
        if not tile_pos:
            return

        col, row = tile_pos

        if self.game_phase == "placement":
            self.handle_placement_click(col, row)
        elif self.game_phase == "playing":
            self.handle_playing_click(col, row)

    def on_update(self, delta_time: float):
        """Beautiful animations update"""
        self.time_elapsed += delta_time
        self.water_animation_offset += delta_time * 0.3

        # Update beautiful particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(delta_time)

        # Update AI particles
        self.ai.update_particles(delta_time)

        # Update penguin animations
        for penguin in self.penguins:
            penguin.bob_offset += delta_time * 1.8
            penguin.scale = 1.0 + math.sin(penguin.bob_offset) * 0.04
            penguin.happiness = max(penguin.happiness - delta_time * 0.1, 0.5)  # Happiness fades slowly

        # Update tile animations
        for row in self.board:
            for tile in row:
                if tile:
                    tile.fish_animation_offset += delta_time * 1.2

                    # Beautiful hover effect
                    if (tile.col, tile.row) in self.valid_moves:
                        tile.hover_scale = min(tile.hover_scale + delta_time * 2.5, 1.08)
                    else:
                        tile.hover_scale = max(tile.hover_scale - delta_time * 2.5, 1.0)

                    # Golden selection glow
                    if (self.selected_penguin and 
                        self.selected_penguin.col == tile.col and 
                        self.selected_penguin.row == tile.row):
                        tile.selected_glow = min(tile.selected_glow + delta_time * 4, 1.0)
                    else:
                        tile.selected_glow = max(tile.selected_glow - delta_time * 4, 0.0)

        # AI logic
        if self.ai_thinking:
            self.ai_timer += delta_time
            if self.ai_timer >= self.ai_delay:
                self.ai_thinking = False
                self.ai_timer = 0.0

                if self.game_phase == "placement":
                    self.ai_place_penguin()
                elif self.game_phase == "playing":
                    self.ai_make_move()
        elif self.current_player == 1 and self.game_phase != "game_over":
            self.ai_thinking = True
            self.ai_timer = 0.0

    def draw_beautiful_background(self):
        """Draw gorgeous animated ocean background"""
        # Multi-layer water effect
        for layer in range(3):
            for i in range(0, SCREEN_HEIGHT, 15):
                wave_offset = math.sin(self.water_animation_offset * (0.5 + layer * 0.3) + i * 0.008) * (8 + layer * 4)
                color_base = [WATER_COLOR[j] for j in range(3)]

                # Add shimmer
                shimmer = 0.85 + 0.15 * math.sin(self.water_animation_offset * 2 + i * 0.02 + layer)
                for j in range(3):
                    color_base[j] = int(color_base[j] * shimmer)

                arcade.draw_lrbt_rectangle_filled(
                    wave_offset - 10, SCREEN_WIDTH, i , i+15,
                    tuple(color_base)
                )
                


        # Add foam effects
        if random.random() < 0.1:
            foam_x = random.uniform(0, SCREEN_WIDTH)
            foam_y = random.uniform(0, SCREEN_HEIGHT)
            self.particles.append(ParticleEffect(foam_x, foam_y, (255, 255, 255), "foam"))

    def get_tile_color(self, tile: Tile) -> Tuple[int, int, int]:
        """Get beautiful tile color based on variant"""
        base_colors = [TILE_BASE, TILE_HONEY, TILE_BRONZE]
        return base_colors[tile.tile_variant % len(base_colors)]

    def draw_gorgeous_hexagon(self, center_x: float, center_y: float, radius: float, 
                             color: Tuple[int, int, int], tile: Tile):
        """Draw hexagon with beautiful 3D gradient effect"""
        points = []
        for i in range(6):
            angle = math.pi / 3 * i + math.pi / 6
            point_x = center_x + radius * math.cos(angle) * tile.hover_scale
            point_y = center_y + radius * math.sin(angle) * tile.hover_scale
            points.append([point_x, point_y])

        # Beautiful shadow with soft edges
        shadow_points = []
        shadow_offset = 4
        for point in points:
            shadow_points.append([point[0] + shadow_offset, point[1] - shadow_offset])

        # Multi-layer shadow for depth
        for layer in range(3):
            shadow_alpha = 40 - layer * 10
            layer_offset = shadow_offset - layer
            layer_points = []
            for point in points:
                layer_points.append([point[0] + layer_offset, point[1] - layer_offset])
            arcade.draw_polygon_filled(layer_points, (*TILE_SHADOW[:3], shadow_alpha))

        # Main tile with gradient
        arcade.draw_polygon_filled(points, color)

        # Beautiful top highlight
        highlight_points = []
        for i in range(3):  # Top half
            point = points[i]
            highlight_points.append([point[0] - 1, point[1] + 2])
        if len(highlight_points) >= 3:
            light_color = tuple(min(255, c + 40) for c in color)
            arcade.draw_polygon_filled(highlight_points, light_color)

        # Bottom shading
        shade_points = []
        for i in range(3, 6):  # Bottom half
            point = points[i]
            shade_points.append([point[0] + 1, point[1] - 2])
        if len(shade_points) >= 3:
            dark_color = tuple(max(0, c - 30) for c in color)
            arcade.draw_polygon_filled(shade_points, dark_color)

        # Golden selection glow
        if tile.selected_glow > 0:
            glow_intensity = tile.selected_glow
            glow_radius = radius * (1 + glow_intensity * 0.25)
            glow_points = []
            for i in range(6):
                angle = math.pi / 3 * i + math.pi / 6
                point_x = center_x + glow_radius * math.cos(angle)
                point_y = center_y + glow_radius * math.sin(angle)
                glow_points.append([point_x, point_y])

            glow_alpha = int(glow_intensity * 120)
            arcade.draw_polygon_filled(glow_points, (*SELECTED_COLOR, glow_alpha))

        # Beautiful outline
        outline_color = SELECTED_COLOR if tile.selected_glow > 0.5 else TILE_OUTLINE
        arcade.draw_polygon_outline(points, outline_color, 3)

    def draw_beautiful_fish(self, center_x: float, center_y: float, scale: float, 
                           animation_offset: float, fish_colors: List[Tuple[int, int, int]]):
        """Draw gorgeous animated fish"""
        # Swimming animation
        swim_x = center_x + math.sin(animation_offset) * 2
        swim_y = center_y + math.cos(animation_offset * 1.1) * 1

        body_length = 16 * scale
        body_height = 8 * scale + math.sin(animation_offset * 2.5) * 0.8
        tail_size = 6 * scale

        # Gradient body
        main_color = random.choice(fish_colors)
        arcade.draw_ellipse_filled(swim_x, swim_y, body_length, body_height, main_color)

        # Shimmer effect
        shimmer_color = tuple(min(255, c + 30) for c in main_color)
        arcade.draw_ellipse_filled(swim_x + 1, swim_y + 0.5, body_length * 0.7, body_height * 0.5, shimmer_color)

        # Animated tail with gradient
        tail_wave = math.sin(animation_offset * 4) * 0.4
        tail_points = [
            [swim_x - body_length // 2, swim_y],
            [swim_x - body_length // 2 - tail_size, swim_y - tail_size // 2 + tail_wave],
            [swim_x - body_length // 2 - tail_size, swim_y + tail_size // 2 + tail_wave]
        ]
        tail_color = tuple(max(0, c - 20) for c in main_color)
        arcade.draw_polygon_filled(tail_points, tail_color)

        # Beautiful eye with shine
        blink = 1.0 if math.sin(animation_offset * 0.4) > 0.95 else 0.0
        eye_size = (2.5 * scale) * (1 - blink * 0.8)
        if eye_size > 0.5:
            arcade.draw_circle_filled(swim_x + body_length // 4, swim_y + body_height // 4, eye_size, arcade.color.WHITE)
            arcade.draw_circle_filled(swim_x + body_length // 4, swim_y + body_height // 4, eye_size * 0.6, arcade.color.BLACK)
            arcade.draw_circle_filled(swim_x + body_length // 4 - 0.5, swim_y + body_height // 4 + 0.5, eye_size * 0.25, arcade.color.WHITE)

    def draw_fish_symbols(self, center_x: float, center_y: float, fish_count: int, animation_offset: float):
        """Draw beautiful fish symbols"""
        fish_colors = [FISH_CORAL, FISH_TURQUOISE, FISH_GOLD, FISH_SALMON]

        if fish_count == 1:
            self.draw_beautiful_fish(center_x, center_y, 1.0, animation_offset, fish_colors)
        elif fish_count == 2:
            self.draw_beautiful_fish(center_x - 9, center_y, 0.85, animation_offset, fish_colors)
            self.draw_beautiful_fish(center_x + 9, center_y, 0.85, animation_offset + 1.2, fish_colors)
        elif fish_count == 3:
            self.draw_beautiful_fish(center_x, center_y + 9, 0.75, animation_offset, fish_colors)
            self.draw_beautiful_fish(center_x - 9, center_y - 5, 0.75, animation_offset + 0.8, fish_colors)
            self.draw_beautiful_fish(center_x + 9, center_y - 5, 0.75, animation_offset + 1.6, fish_colors)

    def draw_gorgeous_penguin(self, center_x: float, center_y: float, penguin: Penguin):
        """Draw penguin with beautiful details and animation"""
        # Enhanced bobbing animation
        bob_y = center_y + math.sin(penguin.bob_offset) * 3.5
        scale = penguin.scale
        happiness_glow = penguin.happiness * 20

        color_base = PENGUIN_HUMAN_BASE if penguin.player_id == 0 else PENGUIN_AI_BASE
        color_light = PENGUIN_HUMAN_LIGHT if penguin.player_id == 0 else PENGUIN_AI_LIGHT
        color_dark = PENGUIN_HUMAN_DARK if penguin.player_id == 0 else PENGUIN_AI_DARK

        # Soft shadow with multiple layers
        for layer in range(3):
            shadow_offset = 3 - layer
            shadow_alpha = 30 - layer * 8
            arcade.draw_circle_filled(
                center_x + shadow_offset, bob_y - shadow_offset - 3, 
                18 * scale, (0, 0, 0, shadow_alpha)
            )

        # Happiness glow
        if happiness_glow > 10:
            arcade.draw_circle_filled(center_x, bob_y, 22 * scale, (*color_light, int(happiness_glow)))

        # Main body with beautiful gradient
        arcade.draw_circle_filled(center_x, bob_y, 18 * scale, color_base)
        arcade.draw_circle_filled(center_x - 2, bob_y + 2, 15 * scale, color_light)
        arcade.draw_circle_filled(center_x + 1, bob_y - 1, 12 * scale, color_dark)

        # Gorgeous white belly
        arcade.draw_circle_filled(center_x, bob_y - 3, 11 * scale, arcade.color.WHITE)
        arcade.draw_circle_filled(center_x - 1, bob_y - 1, 8 * scale, (255, 255, 255, 180))

        # Head with beautiful shading
        head_y = bob_y + 12 * scale
        arcade.draw_circle_filled(center_x, head_y, 9 * scale, arcade.color.BLACK)
        arcade.draw_circle_filled(center_x - 1, head_y + 1, 7 * scale, (60, 60, 60))

        # 3D beak with highlights
        beak_points = [
            [center_x - 2.5, head_y],
            [center_x + 2.5, head_y],
            [center_x, head_y + 5]
        ]
        arcade.draw_polygon_filled(beak_points, arcade.color.ORANGE)

        highlight_points = [
            [center_x - 1.5, head_y],
            [center_x + 1.5, head_y],
            [center_x, head_y + 3.5]
        ]
        arcade.draw_polygon_filled(highlight_points, (255, 215, 0))

        # Beautiful eyes with shine and expression
        eye_size = 2.0 * scale
        eye_happiness = 1.0 + penguin.happiness * 0.3

        # Eye whites
        arcade.draw_circle_filled(center_x - 3.5, head_y + 2, eye_size * eye_happiness, arcade.color.WHITE)
        arcade.draw_circle_filled(center_x + 3.5, head_y + 2, eye_size * eye_happiness, arcade.color.WHITE)

        # Pupils
        arcade.draw_circle_filled(center_x - 3.5, head_y + 2, eye_size * 0.7, arcade.color.BLACK)
        arcade.draw_circle_filled(center_x + 3.5, head_y + 2, eye_size * 0.7, arcade.color.BLACK)

        # Eye shine
        arcade.draw_circle_filled(center_x - 3, head_y + 2.5, eye_size * 0.4, arcade.color.WHITE)
        arcade.draw_circle_filled(center_x + 4, head_y + 2.5, eye_size * 0.4, arcade.color.WHITE)

        # Animated flippers
        flipper_angle = math.sin(penguin.bob_offset * 1.8) * 0.3
        flipper_color = tuple(max(0, c - 40) for c in color_base)

        # Left flipper
        arcade.draw_ellipse_filled(
            center_x - 14, bob_y,
            10 * scale, 5 * scale,
            flipper_color,
            math.degrees(flipper_angle)
        )

        # Right flipper  
        arcade.draw_ellipse_filled(
            center_x + 14, bob_y,
            10 * scale, 5 * scale,
            flipper_color,
            math.degrees(-flipper_angle)
        )

    def on_draw(self):
        """Render the beautiful game"""
        self.clear()

        # Draw gorgeous background
        self.draw_beautiful_background()

        # Draw tiles with beautiful effects
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                tile = self.board[row][col]
                if tile and tile.exists:
                    center_x, center_y = self.get_tile_center(col, row)

                    # Get beautiful tile color
                    color = self.get_tile_color(tile)
                    if (col, row) in self.valid_moves:
                        color = VALID_MOVE_COLOR

                    # Draw gorgeous hexagon
                    self.draw_gorgeous_hexagon(center_x, center_y, HEX_RADIUS, color, tile)

                    # Draw beautiful fish
                    self.draw_fish_symbols(center_x, center_y, tile.fish_count.value, tile.fish_animation_offset)

                    # Draw gorgeous penguin if present
                    if tile.has_penguin:
                        penguin = self.get_penguin_at(col, row)
                        if penguin:
                            self.draw_gorgeous_penguin(center_x, center_y, penguin)

        # Draw beautiful particles
        for particle in self.particles:
            particle.draw()

        # Draw AI thinking particles
        self.ai.draw_particles()

        # Draw beautiful UI
        self.title_text.draw()
        self.human_score_text.draw()
        self.ai_score_text.draw()
        self.status_text.draw()
        self.phase_text.draw()
        self.controls_text.draw()
        

        # Victory celebration effect
        if self.game_phase == "game_over":
            celebration_alpha = int(abs(math.sin(self.time_elapsed * 4)) * 40 + 20)
            color = (ACCENT_GLOW[0], ACCENT_GLOW[1], ACCENT_GLOW[2], celebration_alpha)

            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH // 2 - SCREEN_WIDTH // 2,
                right=SCREEN_WIDTH // 2 + SCREEN_WIDTH // 2,
                top=SCREEN_HEIGHT // 2 + SCREEN_HEIGHT // 2,
                bottom=SCREEN_HEIGHT // 2 - SCREEN_HEIGHT // 2,
                color=color
            )
            self.show_game_over()




    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.R and self.game_phase == "game_over":
            self.__init__()
            self.setup()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

def main():
    """Run the beautiful game"""
    game = FishGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
