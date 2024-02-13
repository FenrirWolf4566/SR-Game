import random
import unittest

from shared import network
from client import client
from server import server

"""
Objective: Test the server only
* Verify collision (borders)
* Verify collision (players)
* Verify fruits consomption
"""


class TestBorderCollision(unittest.TestCase):

    def test_collision_top_left_corner(self):
        x, y = -10, -10
        expected_x, expected_y = 10, 10 
        new_x, new_y = server.borders_of_screen(x, y)
        self.assertEqual((new_x, new_y), (expected_x, expected_y))

    def test_collision_bottom_right_corner(self):
        x, y = 810, 610
        expected_x, expected_y = 790, 590
        new_x, new_y = server.borders_of_screen(x, y)
        self.assertEqual((new_x, new_y), (expected_x, expected_y))

    def test_no_collision_inside_map(self):
        x, y = 400, 300 
        expected_x, expected_y = 400, 300
        new_x, new_y = server.borders_of_screen(x, y)
        self.assertEqual((new_x, new_y), (expected_x, expected_y))



class TestPlayersCollision(unittest.TestCase):


    def test_collision_same_position(self):
        player_size = 2
        id_ref = 0
        x, y = 400, 300
        players = [[0, 0, 400, 300], [1, 0, 400, 300]] # (id, score, x, y)
        expected = True
        collision = server.is_another_player_here(id_ref, x, y)
        self.assertEqual(collision, expected)

    def test_no_collision_different_position(self):
        player_size = 2
        id_ref = 0
        x, y = 400, 300
        players = [[0, 0, 400, 300], [1, 0, 500, 300]] 
        expected = False
        collision = server.is_another_player_here(id_ref, x, y)
        self.assertEqual(collision, expected)



class TestFruitsConsomption(unittest.TestCase):


    def test_consume_fruit(self):
        player_size = 2
        fruit_size = 3
        x, y = 50, 50
        fruits = [(50, 50), (400, 50), (750, 50)]
        expected = [(400, 50), (750, 50)]
        new_fruits = server.has_eaten_a_fruit(x, y)
        self.assertEqual(new_fruits, expected)

    def test_no_consume_fruit(self):
        player_size = 2
        fruit_size = 3
        x, y = 0, 0
        fruits = [(50, 50), (400, 50), (750, 50)]
        expected = [(50, 50), (400, 50), (750, 50)]
        new_fruits = server.has_eaten_a_fruit(x, y)
        self.assertEqual(new_fruits, expected)


def main():
    unittest.main()