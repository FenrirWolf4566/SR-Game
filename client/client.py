import asyncio
import base64
import json
import pygame
from shared import network

HOST_ADDR = ('localhost', 12345)
players = []
fruits = []

ID = 0

###################################################
## Network client
###################################################

def on_receive(data):
    try:
        list_str_code = data.decode("utf-8")
        string = base64.b64decode(list_str_code)
        plate = json.loads(string)
        jsonParse(plate)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

def on_remote_close():
    print('Connection closed by server')

###################################################




###################################################
## Network client
###################################################
def jsonParse(json_input):
    global ID, players, fruits
    if 'id' in json_input:
        ID = json_input['id']
    else :
        players = json_input['players']
        fruits = json_input['fruits']
    return

def draw(screen):
    screen.fill((100, 100, 100))
    for player in players:
        x, y = player[2], player[3]
        id = player[0]
        color = (0, 0, 255) if id == ID else (255, 0, 0)
        pygame.draw.circle(screen, color, (x, y), 10)
    for fruit in fruits:
        x, y = fruit[0], fruit[1]
        pygame.draw.circle(screen, (0, 255, 0), (x, y), 5)

async def move(nw, keys):
    if keys[pygame.K_UP] or keys[pygame.K_z]:
        print(f'move 1')
        await nw.send(b'1')
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        print(f'move 2')
        await nw.send(b'2')
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        print(f'move 3')
        await nw.send(b'3')
    elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
        print(f'move 4')
        await nw.send(b'4')

###################################################






async def main():
    nw = network.create(HOST_ADDR, on_receive, on_remote_close)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Client')
    clock = pygame.time.Clock()
    screen.fill((100, 100, 100))

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
                await move(nw, keys)

        draw(screen)
        pygame.display.update()
        await asyncio.sleep(0)
        #clock.tick(0.1)
