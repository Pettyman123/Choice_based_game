import pygame
import os
import json
import sys
import math


import json

def load_stage(stage_name):
    path = f"stages/{stage_name}.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Stage file not found: {path}")
        return {}



def play_background_music():
    music_path = "assets/audio/bg_music.mp3"
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)  # 🔁 -1 means loop forever
    else:
        print("Background music file not found.")


def play_voice(scene_name):
    voice_path = f"assets/voice/{scene_name}.mp3"
    print(f"Trying to play: {voice_path}")
    if os.path.exists(voice_path):
        voice = pygame.mixer.Sound(voice_path)
        voice.play()
    else:
        print(f"Voice file not found: {voice_path}")

SAVE_PATH = "data/save.json"

def save_game(stage, scene, image_index, memory):
    data = {
        "stage": stage,
        "scene": scene,
        "image_index": image_index,
        "memory": memory
    }
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f)
    print("💾 Game saved.")

def load_game():
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            print("📂 Game loaded.")
            return data
    except FileNotFoundError:
        print("❌ No save file found.")
        return None



# def draw_wavy_text(surface, text, x, y, font, color, time_offset=0, amplitude=5, frequency=0.3):
#     for i, char in enumerate(text):
#         offset_y = math.sin(time_offset + i * frequency) * amplitude
#         char_surf = font.render(char, True, color)
#         surface.blit(char_surf, (x + i * char_surf.get_width(), y + offset_y))


# def draw_glow_text(surface, text, x, y, font, main_color, glow_color, intensity=5):
#     for dx in range(-intensity, intensity + 1):
#         for dy in range(-intensity, intensity + 1):
#             if dx**2 + dy**2 <= intensity**2:
#                 glow_surface = font.render(text, True, glow_color)
#                 surface.blit(glow_surface, (x + dx, y + dy))
#     text_surface = font.render(text, True, main_color)
#     surface.blit(text_surface, (x, y))

# def draw_glowy_wavy_text(surface, text, x, y, font, main_color, glow_color, time_offset=0):
#     for i, char in enumerate(text):
#         offset_y = math.sin(time_offset + i * 0.3) * 5

#         # glow
#         for dx in range(-2, 3):
#             for dy in range(-2, 3):
#                 if dx != 0 or dy != 0:
#                     glow_surf = font.render(char, True, glow_color)
#                     surface.blit(glow_surf, (x + i * 22 + dx, y + offset_y + dy))

#         # main text
#         char_surf = font.render(char, True, main_color)
#         surface.blit(char_surf, (x + i * 22, y + offset_y))


# Initialize Pygame
pygame.init()
pygame.mixer.init()
player_memory = {}
ambient_sound = pygame.mixer.Sound("assets/audio/dripping.mp3")
ambient_channel = pygame.mixer.Channel(1)
ambient_channel.play(ambient_sound, loops=-1)
ambient_channel.set_volume(0.5)
typing_sound = pygame.mixer.Sound("assets/audio/typing.mp3")
typing_sound.set_volume(0.05)  # optional: reduce volume
play_background_music()

# Global Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT_PATH = "assets/fonts/KnightWarrior-w16n8.otf"
FONT_SIZE = 24
font = pygame.font.Font(FONT_PATH, FONT_SIZE)

# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eerie Choice Game")

# Font Setup
# font = pygame.font.SysFont("Arial", 32)
# Load story.json
# with open('data/story.json', 'r') as f:
#     STORY = json.load(f)

current_stage = "stage1"  # default starting point
STORY = load_stage(current_stage)
# Scene Manager
current_scene = "scene1"


# Load all images from the current scene folder
def load_scene_images(scene_name):
    folder = STORY[scene_name]['folder']
    image_files = sorted([
        os.path.join(folder, img)
        for img in os.listdir(folder)
        if img.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    return [pygame.image.load(img).convert() for img in image_files]

def draw_text(surface, text, x, y, width, font, color=WHITE):
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


def fade_in(surface, image, duration=500):
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    fade.fill((0, 0, 0))

    for alpha in range(255, -1, -15):
        screen.blit(pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 17)

def fade_out(duration=500):
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 15):
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        pygame.time.delay(duration // 17)

def apply_filter(surface, blur_strength=5, color=(50, 50, 50), alpha=80):
    # Get the original surface dimensions
    width, height = surface.get_size()
    
    # Create a scaled-down copy of the original surface
    scale_factor = 1 / blur_strength
    scaled_width = max(1, int(width * scale_factor))
    scaled_height = max(1, int(height * scale_factor))
    
    # Create the blur effect through downscaling and upscaling
    small_surface = pygame.transform.smoothscale(surface, (scaled_width, scaled_height))
    blurred = pygame.transform.smoothscale(small_surface, (width, height))
    
    # Apply the tint if alpha > 0
    if alpha > 0:
        overlay = pygame.Surface((width, height)).convert_alpha()
        overlay.fill((*color, alpha))
        blurred.blit(overlay, (0, 0))
    
    # Blit the processed surface back to the original
    surface.blit(blurred, (0, 0))
    
    return surface


# Initialize first scene images
scene_images = load_scene_images(current_scene)
full_text = STORY[current_scene]['text']
visible_text = ""
char_index = 0
text_speed = 40  # milliseconds per character
last_char_time = pygame.time.get_ticks()

play_voice(current_scene)  # 🔊 play voice on first load

image_index = 0
clock = pygame.time.Clock()
running = True
show_new_image = True
SLIDE_DURATION = 3000  # time per image in ms (3 seconds)
last_slide_time = pygame.time.get_ticks()
last_typing_sound_time = 0
sound_delay = 10  # milliseconds

# Game Loop
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only allow clicking on buttons
            mx, my = pygame.mouse.get_pos()
            if image_index == len(scene_images) - 1:
                if choice_a_rect.collidepoint(mx, my):
                    fade_out(600)  # fade to black before switching
                    current_scene = STORY[current_scene]['choices']['A']
                    scene_images = load_scene_images(current_scene)
                    image_index = 0
                    show_new_image = True
                    play_voice(current_scene)
                    last_slide_time = pygame.time.get_ticks()
                    # Store player's choice
                    player_memory[current_scene] = "A"  # or "B"

                    # 🔁 Reset typing text
                    full_text = STORY[current_scene]['text']
                    visible_text = ""
                    char_index = 0
                    last_char_time = pygame.time.get_ticks()
                    typing_sound.play()

                elif choice_b_rect.collidepoint(mx, my):
                    fade_out(600)  # fade to black before switching
                    current_scene = STORY[current_scene]['choices']['B']
                    scene_images = load_scene_images(current_scene)
                    image_index = 0
                    show_new_image = True
                    play_voice(current_scene)
                    last_slide_time = pygame.time.get_ticks()
                    # Store player's choice
                    player_memory[current_scene] = "A"  # or "B"

                    # 🔁 Reset typing text
                    full_text = STORY[current_scene]['text']
                    visible_text = ""
                    char_index = 0
                    last_char_time = pygame.time.get_ticks()
                    typing_sound.play()


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("🔁 Replaying current scene")

                # Reset image index and reload current scene images
                scene_images = load_scene_images(current_scene)
                image_index = 0

                # Reset typing effect
                full_text = STORY[current_scene]['text']
                visible_text = ""
                char_index = 0
                last_char_time = pygame.time.get_ticks()

                # Play voice again
                play_voice(current_scene)

                # Reset image fade trigger and slide timer
                show_new_image = True
                last_slide_time = pygame.time.get_ticks()

            if event.key == pygame.K_i:
                save_game(current_stage, current_scene, image_index, player_memory)
            elif event.key == pygame.K_o:
                save_data = load_game()
                if save_data:
                    current_stage = save_data["stage"]
                    STORY = load_stage(current_stage)
                    current_scene = save_data["scene"]
                    scene_images = load_scene_images(current_scene)
                    image_index = save_data["image_index"]
                    player_memory = save_data["memory"]
                    show_new_image = True
                    play_voice(current_scene)

                    # Reset typing effect
                    full_text = STORY[current_scene]["text"]
                    visible_text = ""
                    char_index = 0
                    last_char_time = pygame.time.get_ticks()




    # Show current scene image
    if show_new_image:
        fade_in(screen, scene_images[image_index])
        show_new_image = False
    else:
        screen.blit(pygame.transform.scale(scene_images[image_index], (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        apply_filter(screen, color=(20, 20, 20), alpha=100)  # dark fog


    # Show text
    
    dialogue = STORY[current_scene]['text']
    now = pygame.time.get_ticks()
    if char_index < len(full_text) and now - last_char_time > text_speed:
        current_char = full_text[char_index]
        visible_text += current_char

        # ✅ Play sound only if it's not a space AND not at the end AND enough time has passed
        if current_char != ' ' and now - last_typing_sound_time > sound_delay:
            typing_sound.play()
            last_typing_sound_time = now

        char_index += 1
        last_char_time = now


    draw_text(screen, visible_text, 50, 50, SCREEN_WIDTH - 100, font)


    # Show choices ONLY on last image
    if image_index == len(scene_images) - 1:
        choice_a_text = "A: " + STORY[current_scene]['choices']['A_text']
        choice_b_text = "B: " + STORY[current_scene]['choices']['B_text']

        choice_a_rect = pygame.Rect(100, SCREEN_HEIGHT - 120, 500, 60)
        choice_b_rect = pygame.Rect(680, SCREEN_HEIGHT - 120, 500, 60)

        pygame.draw.rect(screen, (50, 50, 50), choice_a_rect)
        pygame.draw.rect(screen, (50, 50, 50), choice_b_rect)

        draw_text(screen, choice_a_text, choice_a_rect.x + 10, choice_a_rect.y + 10, 480, font)
        draw_text(screen, choice_b_text, choice_b_rect.x + 10, choice_b_rect.y + 10, 480, font)

    # Automatically go to next image after duration
    if image_index < len(scene_images) - 1:
        now = pygame.time.get_ticks()
        if now - last_slide_time > SLIDE_DURATION:
            image_index += 1
            show_new_image = True
            last_slide_time = now

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()