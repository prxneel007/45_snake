from pathlib import Path
import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 22)
        self.quit_requested = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            assets = Path(__file__).resolve().parent.parent / "assets"
            self.sounds = {name: pygame.mixer.Sound(str(assets / f"{name}.wav"))
                           for name in ("eat", "game_over")}
        except (pygame.error, OSError):
            # Audio is optional on computers without a working sound device.
            print("Sound unavailable; continuing without audio.")
        self.reset("Easy")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def finish_game(self):
        if not self.game_over:
            self.game_over = True
            self.play_sound("game_over")

    def reset(self, difficulty):
        self.difficulty = difficulty
        self.moves_per_second = {"Easy": 8, "Medium": 12, "Hard": 20}[difficulty]
        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size)
        self.food.respawn(self.snake.body)
        self.score = 0
        self._elapsed = 0.0
        self.game_over = False

    def handle_keydown(self, key):
        if key in (pygame.K_ESCAPE, pygame.K_q):
            self.quit_requested = True
            return
        if self.game_over:
            choice = {pygame.K_1: "Easy", pygame.K_2: "Medium", pygame.K_3: "Hard"}.get(key)
            if choice:
                self.reset(choice)
            return
        # Arrow keys and WASD use the same guarded direction change.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        # Reserved for continuously-held-key input (not used for a
        # grid-based snake, but kept here to mirror the engine's shape).
        pass

    def update(self, dt=1 / 60):
        if self.game_over:
            return
        # Movement speed is independent of display frame rate.
        self._elapsed += dt
        interval = 1 / self.moves_per_second
        while self._elapsed + 1e-9 >= interval and not self.game_over:
            self._elapsed -= interval
            self.step()

    def step(self):
        head_x, head_y = self.snake.body[0]
        dx, dy = self.snake.direction
        eating = (head_x + dx, head_y + dy) == (self.food.x, self.food.y)
        if eating:
            self.snake.grow()
        self.snake.move()

        if self.snake.collides_with_wall(self.grid_width, self.grid_height):
            self.finish_game()
            return

        if self.snake.collides_with_self():
            self.finish_game()
            return

        if eating:
            self.score += 1
            self.play_sound("eat")
            if not self.food.respawn(self.snake.body):
                self.finish_game()

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}   |   {self.difficulty}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))
            title = "You won!" if len(self.snake.body) == self.grid_width * self.grid_height else "Game Over"
            lines = [(title, self.font), (f"Final score: {self.score}", self.font),
                     ("Replay: 1 Easy   2 Medium   3 Hard", self.small_font),
                     ("Press Q or Esc to exit", self.small_font)]
            for index, (text, font) in enumerate(lines):
                label = font.render(text, True, WHITE)
                screen.blit(label, label.get_rect(center=(self.width // 2, 235 + index * 45)))
