import asyncio
import pygame
import socket

Addr = tuple[str, int]
Sock = socket.socket

HOST_ADDR = Addr(('192.168.1.31', 12345))

client = Sock(socket.AF_INET, socket.SOCK_STREAM)
client.connect(HOST_ADDR)
client.setblocking(False)

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Client')
clock = pygame.time.Clock()

async def print_received_data():
    loop = asyncio.get_event_loop()
    run = True
    while run:
        print('Waiting for data')
        try:
            data = await loop.sock_recv(client, 1024)
            if data:
                print(f'Received {data} from {client.getpeername()}')
        except asyncio.CancelledError:
            run = False
        except ConnectionResetError:
            print('Connection closed by server')
            run = False


async def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(print_received_data())
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                task.cancel()
                return
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    await loop.sock_sendall(client, b'hello')
        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)


asyncio.run(main())
client.close()
