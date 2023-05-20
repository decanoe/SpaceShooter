import pygame

def shift_hsl(img: pygame.Surface, hOffset: int = 0, sOffset: int = 0, lOffset: int = 0):
    pixels = pygame.PixelArray(img)
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            color = img.unmap_rgb(pixels[x][y])
            h, s, l, a = color.hsla
            color.hsla = (
                int(h + hOffset) % 360,
                int(s + hOffset) % 100,
                int(l + hOffset) % 100,
                int(a))
            pixels[x][y] = color
    del pixels

def loadSprite(jsonData: dict, SPRITE_LIB: pygame.Surface, gridSize: int = 32, color1: tuple[int, int, int] = (0, 0, 0), color2: tuple[int, int, int] = (0, 0, 0)):
    img = None
    length = jsonData.get("animation_length", 1)

    # effect without color
    if ('animation_position_NoneColor' in jsonData):
        img = SPRITE_LIB.subsurface(
            jsonData['animation_position_NoneColor'][0] * gridSize,
            jsonData['animation_position_NoneColor'][1] * gridSize,
            length * gridSize, gridSize).copy()
    
    # base color
    if ('animation_position_color1' in jsonData):
        temp = SPRITE_LIB.subsurface(
            jsonData['animation_position_color1'][0] * gridSize,
            jsonData['animation_position_color1'][1] * gridSize,
            length * gridSize, gridSize).copy()
        shift_hsl(temp, *color1)

        if (img == None):
            img = temp
        else:
            img.blit(temp, (0, 0))

    # second color
    if ('animation_position_color2' in jsonData):
        temp = SPRITE_LIB.subsurface(
            jsonData['animation_position_color2'][0] * gridSize,
            jsonData['animation_position_color2'][1] * gridSize,
            length * gridSize, gridSize).copy()
        shift_hsl(temp, *color2)

        if (img == None):
            img = temp
        else:
            img.blit(temp, (0, 0))

    return img