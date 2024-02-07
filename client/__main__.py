import asyncio
import pygame

from .client import nw


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