import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import unittest
from unittest.mock import Mock, patch
import pygame
from game.snake import Snake
from game.food import Food
from game.game_engine import GameEngine

pygame.init()
pygame.display.set_mode((600, 600))

class GameTests(unittest.TestCase):
    def test_reverse_and_rapid_turns(self):
        snake = Snake(5, 5, 20)
        snake.set_direction(-1, 0)
        snake.move()
        self.assertEqual(snake.body[0], (6, 5))
        snake.set_direction(0, -1)
        snake.set_direction(-1, 0)
        snake.set_direction(0, 1)
        snake.move()
        self.assertEqual(snake.body[0], (6, 4))
        self.assertFalse(snake.collides_with_self())

    def test_vacating_tail_is_safe(self):
        snake = Snake(2, 2, 20)
        snake.body = [(2, 2), (2, 3), (1, 3), (1, 2)]
        snake.direction = (-1, 0)
        snake.move()
        self.assertFalse(snake.collides_with_self())

    def test_walls_and_self(self):
        snake = Snake(0, 0, 20)
        for cell in [(-1, 0), (0, -1), (30, 0), (0, 30)]:
            snake.body[0] = cell
            self.assertTrue(snake.collides_with_wall(30, 30))
        snake.body = [(2, 2), (2, 3), (1, 3), (1, 2), (1, 1)]
        snake.direction = (-1, 0)
        snake.move()
        self.assertTrue(snake.collides_with_self())

    def test_food_and_full_board(self):
        food = Food(2, 2, 20)
        self.assertTrue(food.respawn([(0, 0), (0, 1), (1, 0)]))
        self.assertEqual((food.x, food.y), (1, 1))
        self.assertFalse(food.respawn([(0, 0), (0, 1), (1, 0), (1, 1)]))
        for _ in range(30):
            engine = GameEngine(600, 600)
            self.assertNotIn((engine.food.x, engine.food.y), engine.snake.body)

    def test_eating_grows_immediately(self):
        engine = GameEngine(600, 600)
        engine.food.x, engine.food.y = (16, 15)
        for _ in range(8): engine.update()
        self.assertEqual(engine.score, 1)
        self.assertEqual(len(engine.snake.body), 4)
        self.assertNotIn((engine.food.x, engine.food.y), engine.snake.body)

    def test_game_over_waits_and_quits(self):
        engine = GameEngine(600, 600)
        engine.snake.body = [(29, 5), (28, 5), (27, 5)]
        for _ in range(8): engine.update()
        self.assertTrue(engine.game_over)
        body = engine.snake.body.copy()
        for _ in range(30): engine.update()
        self.assertEqual(body, engine.snake.body)
        engine.render(pygame.display.get_surface())
        engine.handle_keydown(pygame.K_q)
        self.assertTrue(engine.quit_requested)

    def test_replay_all_difficulties(self):
        engine = GameEngine(600, 600)
        for key, name, speed in [(pygame.K_1, "Easy", 8), (pygame.K_2, "Medium", 12), (pygame.K_3, "Hard", 20)]:
            engine.game_over = True
            engine.score = 10
            engine.handle_keydown(key)
            self.assertFalse(engine.game_over)
            self.assertEqual(engine.score, 0)
            self.assertEqual(len(engine.snake.body), 3)
            self.assertEqual(engine.difficulty, name)
            self.assertEqual(engine.moves_per_second, speed)
            engine.food.x, engine.food.y = (0, 0)
            engine.update(0.5)
            self.assertEqual(engine.snake.body[0], (15 + speed // 2, 15))

    def test_sound_events_once(self):
        engine = GameEngine(600, 600)
        self.assertEqual(set(engine.sounds), {"eat", "game_over"})
        engine.sounds = {"eat": Mock(), "game_over": Mock()}
        engine.food.x, engine.food.y = (16, 15)
        engine.update(0.125)
        engine.sounds["eat"].play.assert_called_once()
        engine.snake.body = [(29, 5), (28, 5), (27, 5)]
        engine.update(0.125)
        engine.update(1)
        engine.sounds["game_over"].play.assert_called_once()

    def test_no_audio_device(self):
        with patch('pygame.mixer.get_init', return_value=None), patch('pygame.mixer.init', side_effect=pygame.error('No audio device')):
            engine = GameEngine(600, 600)
            engine.update(0.125)
            engine.finish_game()
            self.assertTrue(engine.game_over)

if __name__ == '__main__':
    unittest.main()
