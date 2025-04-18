import os
import pygame

def load_scene_images(scene_name, STORY):
    folder = STORY[scene_name]['folder']
    image_files = sorted([
        os.path.join(folder, img)
        for img in os.listdir(folder)
        if img.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    return [pygame.image.load(img).convert() for img in image_files]

def draw_text(surface, text, x, y, width, font, color=(255, 255, 255)):
    words = text.split()
    line = ""
    space = font.size(' ')[0]
    x_offset, y_offset = x, y
    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] < width:
            line = test_line
        else:
            surface.blit(font.render(line, True, color), (x_offset, y_offset))
            line = word + " "
            y_offset += font.get_height() + 5
    if line:
        surface.blit(font.render(line, True, color), (x_offset, y_offset))

def fade_in(surface, image, SCREEN_WIDTH, SCREEN_HEIGHT, duration=500):
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -15):
        surface.blit(pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 17)

def fade_out(surface, SCREEN_WIDTH, SCREEN_HEIGHT, duration=500):
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 15):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 17)

def apply_filter(surface, SCREEN_WIDTH, SCREEN_HEIGHT, color=(50, 50, 50), alpha=80):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
    overlay.fill((*color, alpha))
    surface.blit(overlay, (0, 0))

def play_voice(scene_name):
    voice_path = f"assets/voice/{scene_name}.mp3"
    if os.path.exists(voice_path):
        voice = pygame.mixer.Sound(voice_path)
        voice.play()
    else:
        print(f"Voice file not found: {voice_path}")

import numpy as np
x = np.array([1,2,3])
x *= x
print(x)