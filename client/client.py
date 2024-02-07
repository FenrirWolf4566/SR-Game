import base64

import pygame
from shared import network

HOST_ADDR = ('localhost', 12345)

def on_receive(data):
    try:
        list_str_code = data.decode("utf-8")
        string = base64.b64decode(list_str_code)
        print(string)
    except Exception as e:
        print(f"FAILED WITH EXCEPTION : {e}")

def on_remote_close():
    print('Connection closed by server')


screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Client')
clock = pygame.time.Clock()
nw = network.create(HOST_ADDR, on_receive, on_remote_close)





############################################

# Gérer les événements de l'utilisateur, comme la fermeture de la fenêtre de jeu
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop()

# mettre à jour l'état du jeu en fonction des entrées du joueur ou d'autres facteurs
def update_game():
    pass

# afficher les éléments graphiques sur l'écran
def draw():
    # Effacer l'écran
    screen.fill((0, 0, 0))  # Remplacez (0, 0, 0) par la couleur d'arrière-plan souhaitée

    # Dessiner les éléments graphiques (sprites, textes, etc.) sur l'écran
    # Exemple : pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(100, 100, 50, 50))

    # Mettre à jour l'affichage
    pygame.display.flip()

############################################





############################################
# A priori pas besoin de toucher
def main_loop():
    running = True
    while running:
        handle_events()  # Gérer les événements de l'utilisateur
        update_game()   # Mettre à jour l'état du jeu
        draw()          # Afficher les éléments graphiques sur l'écran
        clock.tick(60)  # Limiter le framerate à 60 FPS (images par seconde)

############################################


def start():
    pygame.init()
    nw.start()

def stop():
    pygame.quit()
    nw.stop()
    