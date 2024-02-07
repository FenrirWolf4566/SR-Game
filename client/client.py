import asyncio
import base64
import json
import pygame
from shared import network

HOST_ADDR = ('217.160.249.124', 5000)


###################################################
## Network client
###################################################

def on_receive(data):
    try:
        print('received data')
        list_str_code = data.decode("utf-8")
        # string = base64.b64decode(list_str_code)
        #print(string)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

def on_remote_close():
    print('Connection closed by server')

###################################################




###################################################
## Network client
###################################################
def jsonParse(json_input):

    json_in = json.loads(json_input)
    
    players = []
    fruits = []

    for player in json_in['players']:
        players.append(player)
    for fruit in json_in['fruits']:
        fruits.append(fruit)

    return(players, fruits)

def draw(screen, players, fruits):
    for player in players:
        x, y = player['x'], player['y']
        id = player['id']
        color = (0, 0, 255) if id == 'ME' else (255, 0, 0)
        pygame.draw.circle(screen, color, (x, y), 10)
    for fruit in fruits:
        x, y = fruit['x'], fruit['y']
        pygame.draw.circle(screen, (0, 255, 0), (x, y), 5)


async def move(keys):
    if keys[pygame.K_UP] or keys[pygame.K_z]:
        await nw.send(b'1')
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        await nw.send(b'2')
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        await nw.send(b'3')
    elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
        await nw.send(b'4')

###################################################






async def main():

    json_input = '''
        {
        "players": [
            {
            "id": "BG",
            "x": 100,
            "y": 200
            },
            {
            "id": "GB",
            "x": 300,
            "y": 400
            }
        ],
        "fruits": [
            {
            "x": 50,
            "y": 50
            },
            {
            "x": 200,
            "y": 100
            }
        ]
        }
        '''


    nw = network.create(HOST_ADDR, on_receive, on_remote_close)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Client')
    clock = pygame.time.Clock()
    screen.fill((255, 255, 255))

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
                await move(keys)

        players, fruits = jsonParse(json_input)
        draw(screen, players, fruits)

        pygame.display.update()
        await asyncio.sleep(0)
        clock.tick(60)
