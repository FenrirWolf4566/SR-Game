import pygame
from network import Network
from shared.entities import Player, Fruit

width = 1000
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

pygame.font.init() # you have to call this at the start, if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)


def redrawWindow(win,player, player2, fruits):
    win.fill((255,255,255))
    if player2 != None:
        player.draw(win)
        player2.draw(win)
        for fruit in fruits :
            fruit.draw(win)
    else:
        text_surface = my_font.render('Waiting room', False, (0, 0, 0))
        win.blit(text_surface, (0,0))
    pygame.display.update()


def main():
    run = True
    n = Network()
    p = n.getP()
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        reply = n.send(p)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(win, p, reply['player'], reply['fruits'])

main()