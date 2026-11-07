import unittest

from snek import is_collision, score_for_berry


class GameLogicTests(unittest.TestCase):
    def test_combo_bonus_is_capped(self):
        self.assertEqual(score_for_berry(10, 1), 10)
        self.assertEqual(score_for_berry(10, 3), 20)
        self.assertEqual(score_for_berry(10, 99), 30)

    def test_wall_collision(self):
        self.assertTrue(is_collision((-1, 0), 5, 5, [(2, 2)], set(), set()))

    def test_obstacle_and_hazard_collisions(self):
        snake = [(2, 2), (2, 1)]
        self.assertTrue(is_collision((1, 2), 5, 5, snake, {(1, 2)}, set()))
        self.assertTrue(is_collision((1, 2), 5, 5, snake, set(), {(1, 2)}))

    def test_tail_cell_is_safe_when_not_eating(self):
        snake = [(2, 2), (2, 1), (1, 1)]
        self.assertFalse(is_collision((1, 1), 5, 5, snake, set(), set(), eating=False))
        self.assertTrue(is_collision((1, 1), 5, 5, snake, set(), set(), eating=True))


if __name__ == "__main__":
    unittest.main()
