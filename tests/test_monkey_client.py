import random
import asyncio
import pygame
import unittest
import multiprocessing
from shared import network
from client import client
from server import server
from shared import entities
from unittest.mock import MagicMock

##############################################################################
class ExtendedPlayer(entities.Player):
    """
    Create a simple user with automatic random movement
    """
    def __init__(self, x, y, width, height, color, max_x, max_y):
        super().__init__(x, y, width, height, color, max_x, max_y)
    
    async def move(self):
        directions = [b'1', b'2', b'3', b'4']
        choice = random.choice(directions)
        await self.nw.send(choice)

##############################################################################

"""
def move(self):
    directions = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    choice = random.choice(directions)
    return choice
"""

async def run_game():
    # server.server = MagicMock()

    HOST_ADDR = ('localhost', 12345)
    nw = network.create(HOST_ADDR, client.on_receive, client.on_remote_close)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Client')
    clock = pygame.time.Clock()
    pygame.key.set_repeat(25) # delay before repeating keys (ms) ~40 times per second
    screen.fill((100, 100, 100))

    nw.start()
    run =True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                nw.stop()
                print('Quitting')
                return
            if event.type == pygame.KEYDOWN and not client.Im_still_waiting: #
                keys = pygame.key.get_pressed()
                await client.move(nw, keys)

        client.draw(screen)
        pygame.display.update()
        await asyncio.sleep(0)
        #clock.tick(1)
    nw.stop()
    client.draw_score(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print('Quitting')
                return
            

async def main():
    tasks = [run_game() for _ in range(2)]  # Créer deux instances de run_game
    await asyncio.gather(*tasks)

async def test_monkey():
    pygame.init()
    asyncio.run(main())