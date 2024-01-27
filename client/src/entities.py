import pygame

class Player():
    def __init__(self, x, y, width, height, color, max_x, max_y):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = 3
        self.max_X = max_x
        self.max_Y = max_y

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            authorized_slide = self.x if (self.x < self.vel) else self.vel
            self.x -= authorized_slide
    
        if keys[pygame.K_RIGHT]:
            authorized_slide = (self.max_X - (self.x+self.width)) if (self.max_X - (self.x+self.width))<self.vel else self.vel
            self.x += authorized_slide

        if keys[pygame.K_UP]:
            authorized_slide = self.y if (self.y < self.vel) else self.vel
            self.y -= authorized_slide

        if keys[pygame.K_DOWN]:
            authorized_slide = (self.max_Y - (self.y+self.height)) if ((self.max_Y - (self.y+self.height))<self.vel) else self.vel
            self.y += authorized_slide

        self.update()

    def update(self):
        self.rect = (self.x, self.y, self.width, self.height)

class Fruit():
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)