import asyncio
import base64
import json
import pygame
from shared import network
import time

HOST_ADDR = ('localhost', 12345)
players = []
fruits = []
scores = []
Im_still_waiting = True # after all this time ...
run = True
ID = 0

###################################################
## Network client
###################################################

def on_receive(data):
    try:
        decoded_data = data.decode("utf-8")
        str_code = decoded_data
    except Exception as e:
        print(f"1 : {e}")
    try:
        string = base64.b64decode(str_code)
    except Exception as e:
        print(f"2 : {e} / {str_code}")
    try:
        plate = json.loads(string)
    except Exception as e:
        print(f"3 : {e} / {str_code} / {string}")
    try:
        jsonParse(plate)
    except Exception as e:
        print(f"4 : {e} / {plate}")

def on_remote_close():
    print('Connection closed by server')

###################################################




###################################################
## Network client
###################################################
def jsonParse(json_input):
    global ID, players, fruits, scores, Im_still_waiting, run
    if 'id' in json_input:
        ID = json_input['id']
    elif 'scores' in json_input:
        scores = json_input['scores']
        run = False
    else :
        Im_still_waiting = False
        players = json_input['players']
        fruits = json_input['fruits']
    return

def draw_score(screen):
    scores.sort(key=lambda x: (-x[1])) # Sort list of players by actual scores
    text_to_print = ""
    placement = 1
    for score in scores:
        if score[0]==ID:
            text_to_print += "-> Place " + str(placement) + " : " + str(score[1]) + " points <-\n"
        else:
            text_to_print += "Place " + str(placement) + " : " + str(score[1]) + " points\n"
        placement += 1
    screen.fill((100, 100, 100))
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(text_to_print, True, (255,0,0), (0,0,255))
    textRect = text.get_rect()
    textRect.center = (400, 300)
    screen.blit(text, textRect)
    pygame.display.update()


def draw(screen):
    screen.fill((100, 100, 100))
    for player in players:
        x, y = player[2], player[3]
        id = player[0]
        color = (0, 0, 255) if id == ID else (255, 0, 0)
        pygame.draw.circle(screen, color, (x, y), 10)
    for fruit in fruits:
        x, y = fruit[0], fruit[1]
        if y>=300:
            border_color = (255,0,0)
        else:
            border_color = (255,255,0)
        pygame.draw.circle(screen, border_color, (x, y), 6)
        pygame.draw.circle(screen, (0,255,0), (x, y), 3)

async def move(nw, keys):
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
    nw = network.create(HOST_ADDR, on_receive, on_remote_close)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Client')
    clock = pygame.time.Clock()
    pygame.key.set_repeat(25) # delay before repeating keys (ms) ~40 times per second
    screen.fill((100, 100, 100))

    nw.start()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                nw.stop()
                print('Quitting')
                return
            if event.type == pygame.KEYDOWN and not Im_still_waiting: #
                keys = pygame.key.get_pressed()
                await move(nw, keys)

        draw(screen)
        pygame.display.update()
        await asyncio.sleep(0)
        #clock.tick(1)
    nw.stop()
    draw_score(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print('Quitting')
                return