import cv2
import numpy as np
import os
import time
from PIL import Image, ImageDraw, ImageFont
import pyvirtualcam
from pyvirtualcam import PixelFormat
import concurrent.futures
from colorama import Fore, Back, Style, init

# Initialisation de la caméra
realCam = cv2.VideoCapture(0)

# Paramètres de l'ASCII art
block_size = 5  # Ajuster pour changer la taille des blocs
font_size = 20  # Ajuster pour changer la taille de la police
ascii_chars = " .:-=+*#%@8&WM"
ascii_chars_images = []
font_path = "Consolas.ttf"

num_threads = 10

# Charger une police de caractères monospacée
font = ImageFont.truetype(font_path, font_size)

# Effacer le terminal une seule fois avant la boucle principale
os.system('cls' if os.name == 'nt' else 'clear')

def setup():
    for ascii_char in ascii_chars:
        char_image = Image.new('RGB', (font_size, font_size), color=(30, 30, 30))
        char_draw = ImageDraw.Draw(char_image)
        char_draw.text((0, 0), ascii_char, font=font, fill=(250, 250, 250))
        ascii_chars_images.append(char_image)

def segment_image_to_ascii(segment, block_size, ascii_chars, index):
    h, w, _ = segment.shape
    ascii_art = "\n".join(["0".join([str(int(np.mean(segment[i:i+block_size, j:j+block_size])/255*(len(ascii_chars)-1))) for j in range(0, w, block_size)]) for i in range(0, h, block_size)])
    return index, ascii_art

def segment_ascii_to_image(segment, index):
    lines = segment.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # Supprimer les lignes vides

    width_obs = max(len(line) for line in lines) * (font_size // 2)
    height_obs = len(lines) * font_size

    # Créer une nouvelle image
    image = Image.new('RGB', (width_obs, height_obs), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)

    # Dessiner le texte ASCII sur l'image
    x = 0
    y = 0
    for line in lines:
        for char in line:
            char_image = ascii_chars_images[int(char)]
            image.paste(char_image, (x, y))
            x += font_size
            y += font_size

    return index, image


def segment_image_to_ascii_image(segment, block_size, ascii_chars, index):
    _, ascii_segment = segment_image_to_ascii(segment, block_size, ascii_chars, index)
    _, image_segment = segment_ascii_to_image(ascii_segment, index)
    return index, image_segment

def process_image_to_ascii_image(image, block_size, ascii_chars):
    h, w, _ = image.shape
    segment_height = h // num_threads

    segments = [image[i * segment_height:(i + 1) * segment_height] for i in range(num_threads)]
    if h % num_threads != 0:
        segments.append(image[num_threads * segment_height:])

    ascii_images = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(segment_image_to_ascii_image, segment, block_size, ascii_chars, i)
            for i, segment in enumerate(segments)
        ]
        for future in concurrent.futures.as_completed(futures):
            ascii_images.append(future.result())

    ascii_images.sort(key=lambda x: x[0])

    combined_image = Image.new('RGB', (ascii_images[0][1].width, sum(img.height for _, img in ascii_images)))
    y_offset = 0
    for _, img in ascii_images:
        combined_image.paste(img, (0, y_offset))
        y_offset += img.height

    return combined_image

# Créer une webcam virtuelle avec pyvirtualcam
with pyvirtualcam.Camera(width=2560, height=1940, fps=20, fmt=PixelFormat.BGR) as cam:
    print(f'Utilisation de la caméra virtuelle : {cam.device} ({cam.width}x{cam.height} @ {cam.fps}fps)')

    setup()

    while True:
        start_time = time.time()

        ret, image = realCam.read()
        if not ret:
            break

        new_image = process_image_to_ascii_image(image, block_size, ascii_chars)

        new_image = new_image.resize((2560, 1940), Image.NEAREST)

        image_np = np.array(new_image)

        cam.send(image_np)

        cam.sleep_until_next_frame()

        end_time = time.time()
        fps = 1 / (end_time - start_time)

        print(f"FPS: {fps:.2f}")
