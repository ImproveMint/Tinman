import pygame

pygame.init()

#create screen
screen = pygame.display.set_mode((1000, 700))

#Title
pygame.display.set_caption("Tinman")
icon = pygame.image.load('heart.png')
pygame.display.set_icon(icon)


hole1 = pygame.image.load('png/2_of_clubs.png')
hole1 = pygame.transform.scale(hole1, (130, 180))
hole2 = pygame.image.load('png/Ace_of_clubs.png')
hole2 = pygame.transform.scale(hole2, (130, 180))

hole1x = 400
hole1y = 500

hole2x = 550
hole2y = 500

def card():
    screen.blit(hole1,(hole1x, hole1y))
    screen.blit(hole2, (hole2x, hole2y))

#Game Loop
running = True
while running:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    card()
    pygame.display.update()
