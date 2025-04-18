import pygame
import os
import json
import sys
import math

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

# Keep track of the current voice sound
current_voice_sound = None

def play_voice(scene_name):
    global current_voice_sound
    
    # Stop any currently playing voice
    if current_voice_sound:
        current_voice_sound.stop()
    
    voice_path = f"assets/voice/{scene_name}.mp3"
    print(f"Trying to play: {voice_path}")
    if os.path.exists(voice_path):
        current_voice_sound = pygame.mixer.Sound(voice_path)
        current_voice_sound.play()
    else:
        print(f"Voice file not found: {voice_path}")
        current_voice_sound = None

def stop_voice():
    global current_voice_sound
    if current_voice_sound:
        current_voice_sound.stop()
        current_voice_sound = None

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


# Cache for loaded character images
character_cache = {}


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
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 100, 100)

FONT_PATH = "assets/fonts/KnightWarrior-w16n8.otf"
FONT_SIZE = 24
font = pygame.font.Font(FONT_PATH, FONT_SIZE)

# Setup Window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eerie Choice Game")

current_stage = "stage1"  # default starting point
STORY = load_stage(current_stage)
STORY = {}
STORY.update(load_stage("stage1"))
STORY.update(load_stage("stage2"))
STORY.update(load_stage("stage3"))
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


# Character overlay constants
CHARACTER_WIDTH = 300  # Standard width for character images
CHARACTER_HEIGHT = 350  # Standard height for character images
FACE_WIDTH = 200  # Standard width for face images
FACE_HEIGHT = 200  # Standard height for face images
FACE_POSITION = (980, 50)  # Top right, with some padding
CHARACTER_POSITION = (800, 320)  # Bottom right, with some padding

# Character cache dictionary
character_cache = {}

def load_character_image(type_path, name, width=None, height=None):
    """Load character images with caching and resize to standard dimensions"""
    cache_key = f"{type_path}/{name}/{width}/{height}"
    if cache_key in character_cache:
        return character_cache[cache_key]
    
    path = f"assets/{type_path}/{name}.png"  # This should match your file path format
    if os.path.exists(path):
        image = pygame.image.load(path).convert_alpha()
        
        # Resize if dimensions provided
        if width and height:
            image = pygame.transform.smoothscale(image, (width, height))
        
        character_cache[cache_key] = image
        return image
    else:
        print(f"❌ Character image not found: {path}")
        return None

def display_character(surface, scene_data):
    """Display character overlays with standardized dimensions"""
    if 'emotion' in scene_data and 'pose' in scene_data:
        # Get the emotion and pose values
        emotion = scene_data['emotion']
        pose = scene_data['pose']
        
        # Load face with standardized size
        face_img = load_character_image('faces', f"face_{emotion}", 
                                      FACE_WIDTH, FACE_HEIGHT)
        
        # Load chibi with standardized size
        chibi_img = load_character_image('chibi', pose, 
                                       CHARACTER_WIDTH, CHARACTER_HEIGHT)
        
        # Position and display face
        if face_img:
            surface.blit(face_img, FACE_POSITION)
        
        # Position and display chibi
        if chibi_img:
            surface.blit(chibi_img, CHARACTER_POSITION)

# Function to skip to the end of the current scene
def skip_to_end():
    global image_index, visible_text, char_index
    # Skip to the last image in the scene
    image_index = len(scene_images) - 1
    # Show all text immediately
    visible_text = full_text
    char_index = len(full_text)
    # Stop current voice
    stop_voice()

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

# Skip button dimensions and position
skip_button_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 30)

# Game Loop
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Only allow clicking on buttons
            mx, my = pygame.mouse.get_pos()
            
            # Skip button handling
            if skip_button_rect.collidepoint(mx, my):
                skip_to_end()
                
            # Choice buttons handling
            elif image_index == len(scene_images) - 1:
                if choice_a_rect.collidepoint(mx, my):
                    fade_out(600)  # fade to black before switching
                    current_scene = STORY[current_scene]['choices']['A']
                    scene_images = load_scene_images(current_scene)
                    image_index = 0
                    show_new_image = True
                    
                    # Stop previous voice before playing new one
                    stop_voice()
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
                    
                    # Stop previous voice before playing new one
                    stop_voice()
                    play_voice(current_scene)
                    
                    last_slide_time = pygame.time.get_ticks()
                    # Store player's choice
                    player_memory[current_scene] = "B"  # Fixed - was "A"
                    
                    # 🔁 Reset typing text
                    full_text = STORY[current_scene]['text']
                    visible_text = ""
                    char_index = 0
                    last_char_time = pygame.time.get_ticks()
                    typing_sound.play()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("🔁 Replaying current scene")
                
                # Stop current voice
                stop_voice()

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
                    # Stop current voice
                    stop_voice()
                    
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
            
            # Add spacebar as skip shortcut
            elif event.key == pygame.K_SPACE:
                skip_to_end()

    # Show current scene image
    if show_new_image:
        fade_in(screen, scene_images[image_index])
        show_new_image = False
    else:
        screen.blit(pygame.transform.scale(scene_images[image_index], (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
        apply_filter(screen, color=(20, 20, 20), alpha=100)  # dark fog

    # Display character overlay with standardized sizing
    if current_scene in STORY:
        display_character(screen, STORY[current_scene])

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

    # Draw text box background for better readability
    text_box = pygame.Rect(40, 40, SCREEN_WIDTH - 80, 200)
    pygame.draw.rect(screen, (0, 0, 0, 150), text_box, border_radius=10)
    pygame.draw.rect(screen, (100, 100, 100), text_box, 2, border_radius=10)  # Border

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

    # Draw skip button (only when not at the last image)
    if image_index < len(scene_images) - 1:
        # Change color when mouse hovers over button
        mx, my = pygame.mouse.get_pos()
        button_color = RED if skip_button_rect.collidepoint(mx, my) else DARK_GRAY
        
        pygame.draw.rect(screen, button_color, skip_button_rect, border_radius=5)
        pygame.draw.rect(screen, GRAY, skip_button_rect, 2, border_radius=5)  # Border
        skip_text = font.render("SKIP", True, WHITE)
        text_rect = skip_text.get_rect(center=skip_button_rect.center)
        screen.blit(skip_text, text_rect)

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