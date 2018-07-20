import
def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def built_text(text, coords, size=30, color=(255, 255, 255)):
    myfont = font.SysFont('Comic Sans MS', size)
    textsurface, TextRect = text_objects(text, myfont, color)
    TextRect.center = coords
    win.blit(textsurface, TextRect)