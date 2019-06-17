import pygame
pygame.init()
from Pygame_UI_test import setup_screen

SIZE = WIDTH, HEIGHT = (1024, 720)
FPS = 30
screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
clock = pygame.time.Clock()

fonts, colors, screen, clock = setup_screen()


def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = text.split(" ")  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for word in words:
        word_surface = font.render(word, 0, color)
        word_width, word_height = word_surface.get_size()
        if x + word_width >= max_width:
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        surface.blit(word_surface, (x, y))
        x += word_width + space
    x = pos[0]  # Reset the x.
    y += word_height  # Start on new row.

    return x, y


text = "This is a really long sentence with a couple of breaks.\nSometimes it will break even if there isn't a break " \
       "in the sentence, but that's because the text is too long to fit the screen.\nIt can look strange sometimes.\n" \
       "This function doesn't check if the text is too high to fit on the height of the surface though, so sometimes " \
       "text will disappear underneath the surface"
font = pygame.font.SysFont('Arial', 60)

lines = text.splitlines()

while True:

    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()

    screen.fill(pygame.Color(50,50,50))
    x, y = (20, 20)
    i = 1
    for line in lines:
        if i == 1:
            current_color = colors['active_font']
            current_font = fonts['active']
        else:
            current_color = colors['inactive_font']
            current_font = fonts['inactive']
        x, y = blit_text(screen, line, (20, y), current_font, current_color)
        i+=1


    #blit_text(screen, text, (20, 20), font, colors['inactive_font'])
    pygame.display.update()