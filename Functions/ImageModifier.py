import pygame, random, json

def switch_color(img: pygame.Surface, from_color: list[tuple[int, int, int]], to_color: list[tuple[int, int, int]]):
    for i in range(min(len(from_color), len(to_color))):
        img.blit(pygame.mask.from_threshold(img, from_color[i], threshold=(2, 2, 2, 0)).to_surface(setcolor=to_color[i], unsetcolor=(0, 0, 0, 0)), (0, 0))
def isScaled(color1, color2) -> bool:
    scale = None
    for i in range(3):
        if (color1[i] == 0):
            if (color2[i] != 0): return False
            continue
        
        if (scale == None):
            scale = color2[i] / color1[i]
        elif (scale != color2[i] / color1[i]):
            return False
    
    return True
def randomPalette(paletteSrc: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    palette: list = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))]

    for i in range(1, len(paletteSrc)):
        if isScaled(paletteSrc[i-1], paletteSrc[i]):
            palette.append((
                min(255, max(0, palette[-1][0] + paletteSrc[i][0] - paletteSrc[i - 1][0])),
                min(255, max(0, palette[-1][1] + paletteSrc[i][1] - paletteSrc[i - 1][1])),
                min(255, max(0, palette[-1][2] + paletteSrc[i][2] - paletteSrc[i - 1][2]))
            ))
        else:
            palette.append((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    return palette
def randomPaletteFor(path: str) -> list[tuple[int, int, int]]:
    data = json.load(open(path, 'r'))
    return randomPalette(data.get("from_color", []))

def loadSprite(jsonData: dict, SPRITE_LIB: pygame.Surface, gridSize: int = 32, colors: list[tuple[int, int, int]] = []):
    length = jsonData.get("animation_length", 1)
    from_color = jsonData.get("from_color", [])
    
    img = SPRITE_LIB.subsurface(
        jsonData['animation_position'][0] * gridSize,
        jsonData['animation_position'][1] * gridSize,
        length * gridSize, gridSize).copy()
    switch_color(img, from_color, colors)

    return img