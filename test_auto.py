import pygame
from visualizador_recursos import EditorMaestroSprites

pygame.init()
pygame.display.set_mode((100, 100))
editor = EditorMaestroSprites()
# mock the image sheet
surf = pygame.Surface((100, 100), pygame.SRCALPHA)
surf.fill((0, 0, 0, 255)) # black bg
pygame.draw.rect(surf, (255, 255, 255, 255), (10, 10, 20, 20)) # sprite 1
pygame.draw.rect(surf, (255, 255, 255, 255), (40, 10, 20, 20)) # sprite 2
# overlapping bounding box case? No, just isolated sprites.
editor.img_sheet = surf

try:
    editor.auto_detectar_sprites()
    print("FINAL", len(editor.frames_grid))
except Exception as e:
    import traceback
    traceback.print_exc()
