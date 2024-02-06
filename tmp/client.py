import asyncio
import network
import pygame


HOST_ADDR = ('127.0.0.1', 12345)

def on_receive(data):
    print("Reception")
    print(f'Received {list(data)}')

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
                return
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    await nw.send(bytes(keys))
        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)


asyncio.run(main())
