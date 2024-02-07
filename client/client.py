import asyncio
import base64

import pygame
from shared import network

HOST_ADDR = ('localhost', 12345)

def on_receive(data):
    try:
        print('received data')
        list_str_code = data.decode("utf-8")
        string = base64.b64decode(list_str_code)
        print(string)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

def on_remote_close():
    print('Connection closed by server')


nw = network.create(HOST_ADDR, on_receive, on_remote_close)

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Client')
clock = pygame.time.Clock()

async def main():
    nw.start()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                nw.stop()
                print('Quitting')
                return
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    await nw.send(bytes(keys))
        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)
