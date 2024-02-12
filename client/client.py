import asyncio
import base64
import json
import pygame
from shared import network

HOST_ADDR = ('217.160.249.124', 5000)
HOST_ADDR = ('localhost', 12345)
players = []
fruits = []
scores = []
Im_still_waiting = True # You could never know what it's like \ Your blood like winter freezes just like ice \ And there's a cold and lonely light that shines from you \ You'll wind up like the wreck you hide behind that mask you use \ And did you think this fool could never win \ Well look at me, I'm coming back again \ I got a taste of love in a simple way \ And if you need to know while I'm still waiting you just fade away \ Don't you know I'm still waiting better than I ever did \ Looking like a true survivor, feeling like a little kid \ I'm still waiting after all this time \ Picking up the pieces of my life without you on my mind \ I'm still waiting yeah yeah yeah (x2) \ Once I never could hope to win \ You starting down the road leaving me again \ The threats you made were meant to cut me down \ And if our love was just a circus you'd be a clown by now \ Y' know, I'm still waiting better than I ever did \ Looking like a true survivor, feeling like a little kid \ I'm still waiting after all this time \ Picking up the pieces of my life without you on my mind \ I'm still waiting yeah yeah yeah (x2) \  (Solo) \ Don't you know that I'm still waiting better than I ever did \ Looking like a true survivor, feeling like a little kid \ I'm still waiting after all this time \ Picking up the pieces of my life without you on my mind \ I'm still waiting yeah yeah yeah (x4)
run = True
ID = 0

###################################################
## Network client
###################################################

def on_receive(data):
    """
    Deccode the data received from the server
    """
    try:
        decoded_data = data.decode("utf-8") # decryption from binary
        string = base64.b64decode(decoded_data) # decryption from base64
        plate = json.loads(string) # load as a JSON
        jsonParse(plate) # Parse the JSON
    except Exception as e:
        print(f"Error during decoding in 'on_receive': {e}")

def on_remote_close():
    print('Connection closed by server')


def jsonParse(json_input):
    """
    Parse the JSON input and update the global variables
    """
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
    """
    Draw the score of the player on the screen (ending screen)
    """
    try:
        scores.sort(key=lambda x: (-x[1])) # Sort list of players by actual scores
        text_to_print = ""
        placement = 1
        for score in scores:
            if score[0]==ID:
                place = "1er" if placement==1 else str(placement) + "ème"
                text_to_print += place + " : " + str(score[1]) + "/15 points"
                break
            placement += 1

        bg = pygame.image.load("client/reunion_flag.png")
        screen.blit(bg, (0, 0))
        font = pygame.font.Font('freesansbold.ttf', 25)
        
        as_won = "Gagné" if placement==1 else "Perdu"
        text_score = font.render(as_won, True, (50,14,59), (166,207,213))
        textRect_score = text_score.get_rect()
        textRect_score.center = (400, 450)
        screen.blit(text_score, textRect_score)

        text = font.render(text_to_print, True, (50,14,59), (166,207,213))
        textRect = text.get_rect()
        textRect.center = (400, 500)
        screen.blit(text, textRect)
        pygame.display.update()
    except Exception as e:
        print(f"Error during drawing score : {e}")


def draw(screen):
    """
    Update the screen with the new positions of the players and the fruits
    """
    screen.fill((100, 100, 100))
    own_score = -1
    other_score = -1
    for player in players:
        x, y = player[2], player[3]
        id = player[0]
        color = ()
        if id == ID:
            color = (0, 0, 255)
            own_score = player[1]
        else:
            color = (255, 0, 0)
            other_score = player[1]
        pygame.draw.circle(screen, color, (x, y), 10)
    score_draw = ""
    if own_score>other_score:
        score_draw = "premier : "+str(own_score)
    elif own_score<other_score:
        score_draw = "second : "+str(own_score)
    else:
        score_draw = "ex aequo : "+str(own_score)
    
    if len(players)==0:
        score_draw = "Waiting for other player"

    font = pygame.font.Font('freesansbold.ttf', 25)
    text_score = font.render(score_draw, True, (50,14,59))
    textRect_score = text_score.get_rect()
    textRect_score.topright = (800, 0)
    screen.blit(text_score, textRect_score)
    

    for fruit in fruits:
        x, y = fruit[0], fruit[1]
        if y>=300:
            border_color = (255,0,0)
        else:
            border_color = (255,255,0)
        pygame.draw.circle(screen, border_color, (x, y), 6)
        pygame.draw.circle(screen, (0,255,0), (x, y), 3)

async def move(nw, keys):
    """
    Detect the key pressed and send the corresponding move to the server
    """
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
    pygame.key.set_repeat(25) # delay before repeating keys (ms) ~40 times per second
    screen.fill((100, 100, 100))

    nw.start()
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                await nw.send(b'quit')
                nw.stop()
                return
            if event.type == pygame.KEYDOWN and not Im_still_waiting:
                keys = pygame.key.get_pressed()
                await move(nw, keys)

        draw(screen)
        pygame.display.update()
        await asyncio.sleep(0)
    await nw.send(b'quit')
    nw.stop()
    draw_score(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return